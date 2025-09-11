import copy
import os
import warnings
from typing import Union

import numpy as np

from asltk.logging_config import get_logger, log_data_info
from asltk.utils.image_manipulation import collect_data_volumes
from asltk.utils.io import ImageIO


class ASLData:
    def __init__(
        self,
        **kwargs,
    ):
        """ASLData constructor

        The basic data needed to represent ASL data are:
        - The full path to load the image file
        - The Labeling Duration (LD) array
        - The Post-labeling Delay (PLD) array

        If none of these are provided, a null ASLData object is created, which can be further populated using the get/set methods.

        The constructor supports classic ASL data, multi-TE, and Diffusion-Weighted (DW) ASL protocols.
        There are specific get/set methods for TE/DW data. If TE/DW is not provided, those properties are set to `None`.
        To provide TE or DW values, use the `te_values` or `dw_values` keyword arguments.

        Examples:
            By default, the LD and PLD arrays are empty lists.

            >>> data = ASLData()
            >>> data.get_ld()
            []
            >>> data.get_pld()
            []

            >>> data = ASLData(te_values=[13.0, 20.2, 50.5, 90.5, 125.2])
            >>> data.get_te()
            [13.0, 20.2, 50.5, 90.5, 125.2]

            >>> data = ASLData(dw_values=[13.0, 20.2, 50.5, 90.5, 125.2])
            >>> data.get_dw()
            [13.0, 20.2, 50.5, 90.5, 125.2]

        Other parameters:
            pcasl (str, optional): The ASL data full path with filename. Defaults to ''.
            m0 (str, optional): The M0 data full path with filename. Defaults to ''.
            ld_values (list, optional): The LD values. Defaults to [].
            pld_values (list, optional): The PLD values. Defaults to [].
            te_values (list, optional): The TE values. Defaults to None.
            dw_values (list, optional): The DW values. Defaults to None.
            average_m0 (bool, optional): If True, average the M0 image across the first dimension. This may be helpful for MRI acquisitions that collect an subset sample of M0 volumes and take the average of it. Defaults to False.
        """
        self._asl_image = None
        self._m0_image = None
        self._parameters = {
            'ld': [],
            'pld': [],
            'te': None,
            'dw': None,
        }

        logger = get_logger('asldata')
        logger.info('Creating ASLData object')

        if kwargs.get('pcasl') is not None:
            if isinstance(kwargs.get('pcasl'), str):
                pcasl_path = kwargs.get('pcasl')
                logger.info(f'Loading ASL image from: {pcasl_path}')
                self._asl_image = ImageIO(image_path=pcasl_path)
                if self._asl_image is not None:
                    log_data_info(
                        'ASL image',
                        self._asl_image.get_as_numpy().shape,
                        pcasl_path,
                    )
            elif isinstance(kwargs.get('pcasl'), np.ndarray):
                self._asl_image = ImageIO(image_array=kwargs.get('pcasl'))
                logger.info('ASL image loaded')
                log_data_info(
                    'ASL image', self._asl_image.get_as_numpy().shape
                )

        if kwargs.get('m0') is not None:
            average_m0 = kwargs.get('average_m0', False)
            if self._asl_image:
                self._asl_image._average_m0 = average_m0

            if isinstance(kwargs.get('m0'), str):
                m0_path = kwargs.get('m0')
                logger.info(f'Loading M0 image from: {m0_path}')
                self._m0_image = ImageIO(
                    image_path=m0_path, average_m0=average_m0
                )

                # Check if M0 image is 4D and warn if so
                if (
                    self._m0_image is not None
                    and len(self._m0_image.get_as_numpy().shape) > 3
                ):
                    warnings.warn('M0 image has more than 3 dimensions.')

                if self._m0_image is not None:
                    log_data_info(
                        'M0 image',
                        self._m0_image.get_as_numpy().shape,
                        m0_path,
                    )
            elif isinstance(kwargs.get('m0'), np.ndarray):
                self._m0_image = ImageIO(
                    image_array=kwargs.get('m0'), average_m0=average_m0
                )
                logger.info('M0 image loaded as numpy array')
                log_data_info(
                    'M0 image',
                    self._m0_image.get_as_numpy().shape,
                    'numpy array',
                )

        self._parameters['ld'] = (
            [] if kwargs.get('ld_values') is None else kwargs.get('ld_values')
        )
        self._parameters['pld'] = (
            []
            if kwargs.get('pld_values') is None
            else kwargs.get('pld_values')
        )

        if self._parameters['ld'] or self._parameters['pld']:
            logger.info(
                f"ASL timing parameters - LD: {self._parameters['ld']}, PLD: {self._parameters['pld']}"
            )

        self._check_ld_pld_sizes(
            self._parameters['ld'], self._parameters['pld']
        )
        if kwargs.get('te_values'):
            te_values = kwargs.get('te_values')
            self._parameters['te'] = te_values
            logger.info(f'Multi-TE parameters set: {te_values}')

        if kwargs.get('dw_values'):
            dw_values = kwargs.get('dw_values')
            self._parameters['dw'] = dw_values
            logger.info(f'Diffusion-weighted parameters set: {dw_values}')

        logger.debug('ASLData object created successfully')

    def set_image(self, image: Union[str, np.ndarray], spec: str, **kwargs):
        """Insert an image necessary to define the ASL data processing.

        The `spec` parameters specifies what is the type of image to be used in
        ASL processing step. Choose one of the options: `m0` for the M0 volume,
        `pcasl` for the pCASL data.

        Note:
            The image can be a full path to the image file or a numpy array.
            In case the image parameter is a path, then the method will load
            the image file directly and associate it with the `spec` parameter.
            However, if the image is a numpy array, then the method will
            pass it to the ASLData object image data regarding the `spec`
            parameter as well.

        Examples:
            >>> data = ASLData()
            >>> path_m0 = './tests/files/m0.nii.gz' # M0 file with shape (5,35,35)
            >>> data.set_image(path_m0, spec='m0')
            >>> data('m0').get_as_numpy().shape
            (5, 35, 35)

        Args:
            image (str): The image to be used.
            spec (str): The type of image being used in the ASL processing.
        """
        if isinstance(image, str) and os.path.exists(image):
            if spec == 'm0':
                self._m0_image = ImageIO(image, **kwargs)
            elif spec == 'pcasl':
                self._asl_image = ImageIO(image, **kwargs)
        elif isinstance(image, np.ndarray):
            warnings.warn(
                'Using numpy array as image input does not preserve metadata or image properties.'
            )
            if spec == 'm0':
                self._m0_image = ImageIO(image_array=image, **kwargs)
            elif spec == 'pcasl':
                self._asl_image = ImageIO(image_array=image, **kwargs)
        elif isinstance(image, ImageIO):
            if spec == 'm0':
                self._m0_image = image
            elif spec == 'pcasl':
                self._asl_image = image
        else:
            raise ValueError(
                f'Invalid image type or path: {image}. '
                'Please provide a valid file path or a numpy array.'
            )

    def get_ld(self):
        """Obtain the LD array values"""
        return self._parameters['ld']

    def set_ld(self, ld_values: list):
        """Set the LD values.

        The proper way to inform the values here is using a list of int or
        float data. The total quantity of values depends on the image
        acquisition protocol.

        The list length for LD must be equal to PLD list length.

        Args:
            ld_values (list): The values to be adjusted for LD array
        """
        self._check_input_parameter(ld_values, 'LD')
        self._parameters['ld'] = ld_values

    def get_pld(self):
        """Obtain the PLD array values"""
        return self._parameters['pld']

    def set_pld(self, pld_values: list):
        """Set the PLD values.

        The proper way to inform the values here is using a list of int or
        float data. The total quantity of values depends on the image
        acquisition protocol.

        The list length for PLD must be equal to LD list length.

        Args:
            pld_values (list): The values to be adjusted for PLD array
        """
        self._check_input_parameter(pld_values, 'PLD')
        self._parameters['pld'] = pld_values

    def get_te(self):
        """Obtain the TE array values"""
        return self._parameters['te']

    def set_te(self, te_values: list):
        """Set the TE values.

        The proper way to inform the values here is using a list of int or
        float data. The total quantity of values depends on the image
        acquisition protocol.

        Args:
            te_values (list): The values to be adjusted for TE array
        """
        self._check_input_parameter(te_values, 'TE')
        self._parameters['te'] = te_values

    def get_dw(self):
        """Obtain the Diffusion b values array"""
        return self._parameters['dw']

    def set_dw(self, dw_values: list):
        """Set the Diffusion b values.

        The proper way to inform the values here is using a list of int or
        float data. The total quantity of values depends on the image
        acquisition protocol.

        Args:
            dw_values (list): The values to be adjusted for DW array
        """
        self._check_input_parameter(dw_values, 'DW')
        self._parameters['dw'] = dw_values

    def copy(self):
        """
        Make a copy of the ASLData object.
        This method creates a deep copy of the ASLData object, including all
        its attributes and data. It is useful when you want to preserve the
        original object while working with a modified version.

        Note:
            This method uses `copy.deepcopy` to ensure that all nested objects
            are also copied, preventing any unintended side effects from
            modifying the original object.

        Examples:
            >>> data = ASLData(pcasl='./tests/files/t1-mri.nrrd')
            >>> data_copy = data.copy()
            >>> type(data_copy)
            <class 'asltk.asldata.ASLData'>


        Returns:
            ASLData: A new instance of ASLData that is a deep copy of the original object.
        """
        return copy.deepcopy(self)

    def __call__(self, spec: str):
        """Object caller to expose the image data.

        Examples:
            >>> data = ASLData(pcasl='./tests/files/t1-mri.nrrd')
            >>> type(data('pcasl'))
            <class 'asltk.utils.io.ImageIO'>
            >>> type(data('pcasl').get_as_numpy())
            <class 'numpy.ndarray'>

            >>> np.min(data('pcasl').get_as_numpy())
            0

        Returns:
            (numpy.ndarray): The data placed in the ASLData object
        """
        if spec == 'pcasl':
            return self._asl_image
        elif spec == 'm0':
            return self._m0_image

    def __len__(self):
        """Return the number of volumes in the ASL data.

        This method returns the number of volumes in the ASL data based on
        the pCASL image format.

        Returns:
            int: The number of volumes in the ASL data considering the `pcasl` data.
        """
        if self._asl_image is not None:
            return len(collect_data_volumes(self._asl_image)[0])
        else:
            return 0

    def _check_input_parameter(self, values, param_type):
        for v in values:
            if not isinstance(v, int) and not isinstance(v, float):
                raise ValueError(
                    f'{param_type} values is not a list of valid numbers.'
                )
            if v <= 0:
                raise ValueError(
                    f'{param_type} values must be postive non zero numbers.'
                )

    def _check_ld_pld_sizes(self, ld, pld):
        logger = get_logger('asldata')
        if len(ld) != len(pld):
            error_msg = f'LD and PLD must have the same array size. LD size is {len(ld)} and PLD size is {len(pld)}'
            logger.error(error_msg)
            raise ValueError(error_msg)
        else:
            logger.debug(
                f'LD and PLD size validation passed: {len(ld)} elements each'
            )

    def _check_m0_dimension(self):
        if len(self._m0_image.get_as_numpy().shape) > 3:
            warnings.warn(
                'M0 image has more than 3 dimensions. '
                'This may cause issues in processing. '
                'Consider averaging the M0 image across the first dimension.'
            )
