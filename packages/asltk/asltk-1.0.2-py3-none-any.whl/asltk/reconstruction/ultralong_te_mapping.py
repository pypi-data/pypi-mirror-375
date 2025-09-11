import warnings
from multiprocessing import Array, Pool, cpu_count
from typing import Union

import numpy as np
import SimpleITK as sitk
from rich import print
from rich.progress import Progress
from scipy.optimize import curve_fit

from asltk.asldata import ASLData
from asltk.aux_methods import (
    _apply_smoothing_to_maps,
    _check_mask_values,
    get_optimal_core_count,
)
from asltk.models.signal_dynamic import asl_model_multi_te
from asltk.mri_parameters import MRIParameters
from asltk.reconstruction import CBFMapping
from asltk.utils.io import ImageIO

# Global variables to assist multi cpu threading
cbf_map = None
att_map = None
brain_mask = None
asl_data = None
ld_arr = None
pld_arr = None
te_arr = None
tblgm_map = None
t2bl = None
t2gm = None


class UltraLongTE_ASLMapping(MRIParameters):
    def __init__(self, asl_data: ASLData) -> None:
        """UltraLongTE ASL mapping constructor for T1 time exchange tissue relaxometry.

        UltraLongTE_ASLMapping enables advanced ASL analysis by incorporating multiple
        echo times (TE) to estimate tissue-specific T1 relaxation times. This
        provides better characterization of blood vs. tissue compartments and
        improved CBF quantification.

        The class requires ASL data acquired with multiple echo times and performs:
        - Basic CBF and ATT mapping (via CBFMapping)
        - T1 relaxometry for blood-grey matter differentiation
        - Ultralong-TE model fitting for enhanced tissue characterization

        Notes:
            The ASLData object must contain `te_values` - a list of echo times
            used during ASL acquisition. These TE values are critical for the
            multi-echo model fitting and T1 estimation.

        Notes:
            This method is based from the original paper of:
            Leonie Petitclerc, Lydiane Hirschler, Jack A. Wells, David L. Thomas,
            Marianne A.A. van Walderveen, Mark A. van Buchem, Matthias J.P. van Osch,
            "Ultra-long-TE arterial spin labeling reveals rapid and brain-wide
            blood-to-CSF water transport in humans", NeuroImage, ISSN 1053-8119,
            doi: [10.1016/j.neuroimage.2021.118755](http://doi.org/10.1016/j.neuroimage.2021.118755).

        Important:
            Although this method applies a parallel CPU processing, it still a
            highly time and memory consuming procedure. Take this into account
            when working with large datasets or high-resolution images.

        Examples:
            Basic Ultralong-TE ASL mapping setup:
            >>> from asltk.asldata import ASLData
            >>> from asltk.reconstruction import UltraLongTE_ASLMapping
            >>> # Create ASL data with multi-TE parameters
            >>> asl_data = ASLData(
            ...     pcasl='./tests/files/pcasl_mte.nii.gz',
            ...     m0='./tests/files/m0.nii.gz',
            ...     te_values=[13.2, 25.7, 50.4],  # Multiple echo times
            ...     ld_values=[1.8, 1.8, 1.8],
            ...     pld_values=[0.8, 1.8, 2.8]
            ... )
            >>> ulte_mapper = UltraLongTE_ASLMapping(asl_data)
            >>> # Access default MRI parameters
            >>> ulte_mapper.get_constant('T1csf')
            1400.0

            Custom MRI parameters for specific field strength:
            >>> # Adjust T1 values for 3T scanner
            >>> ulte_mapper.set_constant(1600.0, 'T1csf')  # CSF T1 at 3T
            >>> ulte_mapper.get_constant('T1csf')
            1600.0
            >>> # Verify default parameters unchanged for other objects
            >>> from asltk.mri_parameters import MRIParameters
            >>> default_param = MRIParameters()
            >>> default_param.get_constant('T1csf')
            1400.0

        Args:
            asl_data (ASLData): The ASL data object containing ultralong-TE acquisition.
                Must include te_values, ld_values, and pld_values.

        Raises:
            ValueError: If ASLData object lacks required TE values for ultralong-TE analysis.

        See Also:
            CBFMapping: For basic CBF/ATT mapping without multi-echo analysis
            MultiDW_ASLMapping: For diffusion-weighted ASL analysis
            MultiTE_ASLMapping: For the multi-echo TE ASL analysis (the predecessor of this method)
        """
        super().__init__()
        self._asl_data = asl_data
        self._basic_maps = CBFMapping(asl_data)
        if self._asl_data.get_te() is None:
            raise ValueError(
                'ASLData is incomplete. UltraLongTE_ASLMapping need a list of TE values.'
            )

        self._brain_mask = np.ones(self._asl_data('m0').get_as_numpy().shape)
        self._cbf_map = np.zeros(self._asl_data('m0').get_as_numpy().shape)
        self._att_map = np.zeros(self._asl_data('m0').get_as_numpy().shape)
        self._t1csfgm_map = np.zeros(self._asl_data('m0').get_as_numpy().shape)

        # Changing the T2csf and T2blood as requested in the original paper
        self.set_constant(1500.0, 'T2csf')  # T2 relaxation time for CSF in ms
        self.set_constant(100.0, 'T2bl')  # T2 relaxation time for blood in ms

    def set_brain_mask(self, brain_mask: ImageIO, label: int = 1):
        """Defines whether a brain a mask is applied to the CBFMapping
        calculation

        A image mask is simply an image that defines the voxels where the ASL
        calculation should be made. Basically any integer value can be used as
        proper label mask.

        A most common approach is to use a binary image (zeros for background
        and 1 for the brain tissues). Anyway, the default behavior of the
        method can transform a integer-pixel values image to a binary mask with
        the `label` parameter provided by the user

        Args:
            brain_mask (np.ndarray): The image representing the brain mask label (int, optional): The label value used to define the foreground tissue (brain). Defaults to 1.
        """
        if not isinstance(brain_mask, ImageIO):
            raise TypeError(
                'The brain_mask parameter must be an instance of ImageIO.'
            )

        _check_mask_values(
            brain_mask, label, self._asl_data('m0').get_as_numpy().shape
        )

        binary_mask = (brain_mask.get_as_numpy() == label).astype(
            np.uint8
        ) * label
        self._brain_mask = binary_mask

    def get_brain_mask(self):
        """Get the brain mask image

        Returns:
            (ImageIO): The brain mask image
        """
        return self._brain_mask

    def set_cbf_map(self, cbf_map: ImageIO):
        """Set the CBF map to the MultiTE_ASLMapping object.

        Note:
            The CBF maps must have the original scale in order to calculate the
            T1 CSF-GM map correclty. Hence, if the CBF map was made using
            CBFMapping class, one can use the 'cbf' output.

        Args:
            cbf_map (ImageIO): The CBF map that is set in the MultiTE_ASLMapping object
        """
        self._cbf_map = cbf_map.get_as_numpy()

    def get_cbf_map(self) -> np.ndarray:
        """Get the CBF map storaged at the MultiTE_ASLMapping object

        Returns:
            (ImageIO): The CBF map that is storaged in the
            MultiTE_ASLMapping object
        """
        return self._cbf_map

    def set_att_map(self, att_map: ImageIO):
        """Set the ATT map to the MultiTE_ASLMapping object.

        Args:
            att_map (ImageIO): The ATT map that is set in the MultiTE_ASLMapping object
        """
        self._att_map = att_map.get_as_numpy()

    def get_att_map(self):
        """Get the ATT map storaged at the MultiTE_ASLMapping object

        Returns:
            (ImageIO): The ATT map that is storaged in the
            MultiTE_ASLMapping object
        """
        return self._att_map

    def get_t1csfgm_map(self):
        """Get the T1csfGM map storaged at the MultiTE_ASLMapping object

        Returns:
            (ImageIO): The T1csfGM map that is storaged in the
            MultiTE_ASLMapping object
        """
        return self._t1csfgm_map

    def create_map(
        self,
        ub: list = [np.inf],
        lb: list = [0.0],
        par0: list = [400],
        cores: Union[int, str] = 'auto',
        smoothing=None,
        smoothing_params=None,
        suppress_warnings=True,
    ):
        """Create ultra-long-TE ASL maps including T1 csf-gray matter exchange (T1csfGM).

        This method performs advanced multi-echo ASL analysis to generate tissue-specific
        T1 relaxation maps that characterize blood-to-gray matter water exchange. The
        analysis uses multiple echo times to separate blood and tissue signal contributions.

        Note:
            The method implements the multi-compartment TE ASL model described in:
            "Ultra-long-TE arterial spin labeling reveals rapid and brain-wide
            blood-to-CSF water transport in humans", NeuroImage, 2022.
            doi: [10.1016/j.neuroimage.2021.118755](http://doi.org/10.1016/j.neuroimage.2021.118755)

        Note:
            The CBF and ATT maps can be provided before calling this method,
            using the set_cbf_map() and set_att_map() methods. If not provided,
            basic CBF/ATT maps are automatically calculated using the CBFMapping class.

        Note:
            The CBF map must be in original scale (not normalized) to perform the
            correct ultralong-TE-ASL model fitting. Use the 'cbf' output from CBFMapping,
            not the 'cbf_norm' version.

        The method assumes the T1csfGM values are well-characterized by the initial
        guess parameter. Results are filtered to include only positive values and
        values below 4 times the initial guess to remove unrealistic outliers.

        Note:
            Consider applying spatial smoothing to the output T1csfGM map to improve
            SNR. The create_map() method does not apply filtering by default to
            preserve spatial resolution.

        Args:
            ub (list, optional): Upper bounds for T1csfGM fitting. Defaults to [np.inf].
                Typically 800-1200 ms for healthy gray matter at 3T.
            lb (list, optional): Lower bounds for T1csfGM fitting. Defaults to [0.0].
                Should be positive for realistic T1 values.
            par0 (list, optional): Initial guess for T1csfGM in milliseconds.
                Defaults to [400]. Good starting values: 300-500 ms.
            cores (int or str, optional): Number of CPU threads for parallel processing.
                If "auto" (default), automatically determines the optimal number based on
                available system memory. If an integer is provided, uses that specific number.
            smoothing (str, optional): Type of spatial smoothing filter to apply.
                Options: None (default, no smoothing), 'gaussian', 'median'.
                Smoothing is applied to all output maps after reconstruction.
            smoothing_params (dict, optional): Parameters for the smoothing filter.
                For 'gaussian': {'sigma': float} (default: 1.0)
                For 'median': {'size': int} (default: 3)
            suppress_warnings (bool, optional): Whether to suppress warnings during
                processing. Defaults to True.

        Returns:
            dict: Dictionary containing:
                - 'cbf': Basic CBF map in original units (ImageIO)
                - 'cbf_norm': Normalized CBF in mL/100g/min (ImageIO)
                - 'att': Arterial transit time in ms (ImageIO)
                - 't1csfgm': T1 csf-gray matter exchange time in ms (ImageIO)
                All maps are smoothed if smoothing is enabled.

        Examples:
            Basic multi-TE ASL analysis:
            >>> from asltk.asldata import ASLData
            >>> from asltk.reconstruction import UltraLongTE_ASLMapping
            >>> from asltk.utils.io import ImageIO
            >>> import numpy as np
            >>> # Load multi-TE ASL data
            >>> asl_data = ASLData(
            ...     pcasl='./tests/files/pcasl_mte.nii.gz',
            ...     m0='./tests/files/m0.nii.gz',
            ...     te_values=[13.2, 25.7, 50.4],  # Multiple echo times
            ...     ld_values=[1.8, 1.8, 1.8],
            ...     pld_values=[0.8, 1.8, 2.8]
            ... )
            >>> ulte_mapper = UltraLongTE_ASLMapping(asl_data)
            >>> # Set brain mask for faster processing
            >>> brain_mask = ImageIO(image_array=np.ones(asl_data('m0').get_as_numpy().shape))
            >>> ulte_mapper.set_brain_mask(brain_mask)
            >>> # Generate all maps
            >>> results = ulte_mapper.create_map() # doctest: +SKIP


            Custom parameters for specific analysis:
            >>> # For expected shorter T1csfGM values (faster exchange)
            >>> results = ulte_mapper.create_map(
            ...     ub=[600.0],        # Lower upper bound
            ...     lb=[50.0],         # Minimum realistic T1
            ...     par0=[300.0]       # Lower initial guess
            ... ) # doctest: +SKIP

            Apply spatial smoothing to improve SNR:
            >>> # Gaussian smoothing with default sigma=1.0
            >>> results_smooth = ulte_mapper.create_map(
            ...     smoothing='gaussian'
            ... ) # doctest: +SKIP
            >>> # Custom smoothing parameters
            >>> results_custom = ulte_mapper.create_map(
            ...     smoothing='gaussian',
            ...     smoothing_params={'sigma': 1.5}
            ... ) # doctest: +SKIP
            >>> # Median filtering for edge preservation
            >>> results_median = ulte_mapper.create_map(
            ...     smoothing='median',
            ...     smoothing_params={'size': 5}
            ... ) # doctest: +SKIP

        Raises:
            ValueError: If cores parameter is invalid or required data is missing.

        See Also:
            set_cbf_map(): Provide pre-computed CBF map
            set_att_map(): Provide pre-computed ATT map
            CBFMapping: For basic CBF/ATT mapping
        """
        # Determine optimal number of cores based on available memory
        actual_cores = get_optimal_core_count(cores)

        # Use context manager to suppress warnings if requested
        with warnings.catch_warnings():
            if suppress_warnings:
                # Filter common warnings that might appear during fitting and processing
                warnings.filterwarnings('ignore', category=RuntimeWarning)
                warnings.filterwarnings('ignore', category=UserWarning)
                warnings.filterwarnings(
                    'ignore', category=np.VisibleDeprecationWarning
                )

            self._basic_maps.set_brain_mask(
                ImageIO(image_array=self._brain_mask)
            )

            basic_maps = {'cbf': self._cbf_map, 'att': self._att_map}
            if np.mean(self._cbf_map) == 0 or np.mean(self._att_map) == 0:
                # If the CBF/ATT maps are zero (empty), then a new one is created
                print(
                    '[blue][INFO] The CBF/ATT map were not provided. Creating these maps before next step...'
                )
                basic_maps = self._basic_maps.create_map()
                self._cbf_map = basic_maps['cbf'].get_as_numpy()
                self._att_map = basic_maps['att'].get_as_numpy()

            global asl_data, brain_mask, cbf_map, att_map, t2bl, t2gm
            asl_data = self._asl_data
            brain_mask = self._brain_mask
            cbf_map = self._cbf_map
            att_map = self._att_map
            ld_arr = self._asl_data.get_ld()
            pld_arr = self._asl_data.get_pld()
            te_arr = self._asl_data.get_te()
            t2bl = self.T2bl
            t2gm = self.T2gm

            x_axis = self._asl_data('m0').get_as_numpy().shape[2]   # height
            y_axis = self._asl_data('m0').get_as_numpy().shape[1]   # width
            z_axis = self._asl_data('m0').get_as_numpy().shape[0]   # depth

            tcsfgm_map_shared = Array(
                'd', z_axis * y_axis * x_axis, lock=False
            )

            # Make a copy of base information
            m0_array = asl_data('m0').get_as_numpy()
            pcasl_array = asl_data('pcasl').get_as_numpy()

            with Pool(
                processes=actual_cores,
                initializer=_multite_init_globals,
                initargs=(
                    cbf_map,
                    att_map,
                    brain_mask,
                    asl_data,
                    ld_arr,
                    pld_arr,
                    te_arr,
                    tcsfgm_map_shared,
                    t2bl,
                    t2gm,
                ),
            ) as pool:
                with Progress() as progress:
                    task = progress.add_task(
                        'ultralongTE-ASL processing...', total=x_axis
                    )
                    results = [
                        pool.apply_async(
                            _tcsfgm_multite_process_slice,
                            args=(
                                i,
                                x_axis,
                                y_axis,
                                z_axis,
                                par0,
                                lb,
                                ub,
                                m0_array,
                                pcasl_array,
                            ),
                            callback=lambda _: progress.update(
                                task, advance=1
                            ),
                        )
                        for i in range(x_axis)
                    ]
                    for result in results:
                        result.wait()

            self._t1csfgm_map = np.frombuffer(tcsfgm_map_shared).reshape(
                z_axis, y_axis, x_axis
            )

            # Adjusting output image boundaries
            self._t1csfgm_map = self._adjust_image_limits(
                self._t1csfgm_map, par0[0]
            )

            # Prepare output maps
            cbf_map_image = ImageIO(self._asl_data('m0').get_image_path())
            cbf_map_image.update_image_data(self._cbf_map)

            cbf_map_norm_image = ImageIO(self._asl_data('m0').get_image_path())
            cbf_map_norm_image.update_image_data(
                self._cbf_map * (60 * 60 * 1000)
            )

            att_map_image = ImageIO(self._asl_data('m0').get_image_path())
            att_map_image.update_image_data(self._att_map)

            t1csfgm_map_image = ImageIO(self._asl_data('m0').get_image_path())
            t1csfgm_map_image.update_image_data(self._t1csfgm_map)

            # Create output maps dictionary
            output_maps = {
                'cbf': cbf_map_image,
                'cbf_norm': cbf_map_norm_image,
                'att': att_map_image,
                't1csfgm': t1csfgm_map_image,
            }

            # Apply smoothing if requested
            return _apply_smoothing_to_maps(
                output_maps, smoothing, smoothing_params
            )

    def _adjust_image_limits(self, map, init_guess):
        img = sitk.GetImageFromArray(map)
        thr_filter = sitk.ThresholdImageFilter()
        thr_filter.SetUpper(
            4 * init_guess
        )   # assuming upper to 4x the initial guess
        thr_filter.SetLower(0.0)
        img = thr_filter.Execute(img)

        return sitk.GetArrayFromImage(img)


def _multite_init_globals(
    cbf_map_,
    att_map_,
    brain_mask_,
    asl_data_,
    ld_arr_,
    pld_arr_,
    te_arr_,
    tblgm_map_,
    t2bl_,
    t2gm_,
):   # pragma: no cover
    # indirect call method by CBFMapping().create_map()
    global cbf_map, att_map, brain_mask, asl_data, ld_arr, te_arr, pld_arr, tblgm_map, t2bl, t2gm
    cbf_map = cbf_map_
    att_map = att_map_
    brain_mask = brain_mask_
    asl_data = asl_data_
    ld_arr = ld_arr_
    pld_arr = pld_arr_
    te_arr = te_arr_
    tblgm_map = tblgm_map_
    t2bl = t2bl_
    t2gm = t2gm_


def _tcsfgm_multite_process_slice(
    i, x_axis, y_axis, z_axis, par0, lb, ub, m0, pcasl
):   # pragma: no cover
    # indirect call method by CBFMapping().create_map()
    for j in range(y_axis):
        for k in range(z_axis):
            if brain_mask[k, j, i] != 0:
                m0_px = m0[k, j, i]

                def mod_2comp(Xdata, par1):
                    return asl_model_multi_te(
                        Xdata[:, 0],
                        Xdata[:, 1],
                        Xdata[:, 2],
                        m0_px,
                        cbf_map[k, j, i],
                        att_map[k, j, i],
                        par1,
                        t2bl,
                        t2gm,
                    )

                Ydata = (
                    pcasl[:, :, k, j, i]
                    .reshape(
                        (
                            len(ld_arr) * len(te_arr),
                            1,
                        )
                    )
                    .flatten()
                )

                # Calculate the processing index for the 3D space
                index = k * (y_axis * x_axis) + j * x_axis + i

                try:
                    Xdata = _multite_create_x_data(
                        ld_arr,
                        pld_arr,
                        te_arr,
                    )
                    par_fit, _ = curve_fit(
                        mod_2comp,
                        Xdata,
                        Ydata,
                        p0=par0,
                        bounds=(lb, ub),
                    )
                    tblgm_map[index] = par_fit[0]
                except RuntimeError:   # pragma: no cover
                    tblgm_map[index] = 0.0


def _multite_create_x_data(ld, pld, te):   # pragma: no cover
    # array for the x values, assuming an arbitrary size based on the PLD
    # and TE vector size
    Xdata = np.zeros((len(pld) * len(te), 3))

    count = 0
    for i in range(len(pld)):
        for j in range(len(te)):
            Xdata[count] = [ld[i], pld[i], te[j]]
            count += 1

    return Xdata
