import argparse
import os
import warnings
from functools import *

import numpy as np
import SimpleITK as sitk
from rich import print

from asltk.asldata import ASLData
from asltk.logging_config import (
    configure_for_scripts,
    get_logger,
    log_processing_step,
)
from asltk.reconstruction import MultiDW_ASLMapping
from asltk.utils.io import load_image, save_image

warnings.filterwarnings('ignore', category=RuntimeWarning)

parser = argparse.ArgumentParser(
    prog='Multi-DW ASL Mapping',
    description='Python script to calculate the Multi-DW ASL map for the T1 relaxation exchange between blood and Gray Matter (GM).',
)
parser._action_groups.pop()
required = parser.add_argument_group(title='Required parameters')
optional = parser.add_argument_group(title='Optional parameters')

required.add_argument(
    'pcasl',
    type=str,
    help='ASL raw data obtained from the MRI scanner. This must be the multi-DW ASL MRI acquisition protocol.',
)
required.add_argument(
    'm0', type=str, help='M0 image reference used to calculate the ASL signal.'
)
optional.add_argument(
    'mask',
    type=str,
    nargs='?',
    default='',
    help='Image mask defining the ROI where the calculations must be done. Any pixel value different from zero will be assumed as the ROI area. Outside the mask (value=0) will be ignored. If not provided, the entire image space will be calculated.',
)
required.add_argument(
    'out_folder',
    type=str,
    nargs='?',
    default=os.path.expanduser('~'),
    help='The output folder that is the reference to save all the output images in the script. The images selected to be saved are given as tags in the script caller, e.g. the options --cbf_map and --att_map. By default, the TblGM map is placed in the output folder with the name tblgm_map.nii.gz',
)
optional.add_argument(
    '--cbf',
    type=str,
    nargs='?',
    required=False,
    help='The CBF map that is provided to skip this step in the MultiTE-ASL calculation. If CBF is not provided, than a CBF map is calculated at the runtime. Important: The CBF passed here is with the original voxel scale, i.e. without voxel normalization.',
)
optional.add_argument(
    '--att',
    type=str,
    nargs='?',
    required=False,
    help='The ATT map that is provided to skip this step in the MultiTE-ASL calculation. If ATT is not provided, than a ATT map is calculated at the runtime.',
)
optional.add_argument(
    '--pld',
    type=str,
    nargs='+',
    required=False,
    default=[170.0, 270.0, 370.0, 520.0, 670.0, 1070.0, 1870.0],
    help='Posts Labeling Delay (PLD) trend, arranged in a sequence of float numbers. If not passed, the default values will be used.',
)
optional.add_argument(
    '--ld',
    type=str,
    nargs='+',
    required=False,
    default=[100.0, 100.0, 150.0, 150.0, 400.0, 800.0, 1800.0],
    help='Labeling Duration trend (LD), arranged in a sequence of float numbers. If not passed, the default values will be used.',
)
optional.add_argument(
    '--dw',
    type=str,
    nargs='+',
    required=False,
    default=[0, 50, 100, 250],
    help='Diffusion b-values arranged in a sequence of float numbers. If not passed, the default values will be used.',
)
optional.add_argument(
    '--verbose',
    action='store_true',
    help='Show more details thoughout the processing.',
)
optional.add_argument(
    '--file_fmt',
    type=str,
    nargs='?',
    default='nii',
    help='The file format that will be used to save the output images. It is not allowed image compression (ex: .gz, .zip, etc). Default is nii, but it can be choosen: mha, nrrd.',
)


args = parser.parse_args()

# Configure logging based on verbose flag
configure_for_scripts(verbose=args.verbose)
logger = get_logger('dw_asl_script')

# Script check-up parameters
def checkUpParameters():
    is_ok = True
    # Check output folder exist
    if not (os.path.isdir(args.out_folder)):
        print(
            f'Output folder path does not exist (path: {args.out_folder}). Please create the folder before executing the script.'
        )
        is_ok = False

    # Check ASL image exist
    if not (os.path.isfile(args.pcasl)):
        print(
            f'ASL input file does not exist (file path: {args.asl}). Please check the input file before executing the script.'
        )
        is_ok = False

    # Check M0  image exist
    if not (os.path.isfile(args.m0)):
        print(
            f'M0 input file does not exist (file path: {args.m0}). Please check the input file before executing the script.'
        )
        is_ok = False

    if args.file_fmt not in ('nii', 'mha', 'nrrd'):
        print(
            f'File format is not allowed or not available. The select type is {args.file_fmt}, but options are: nii, mha or nrrd'
        )
        is_ok = False

    return is_ok


asl_img = load_image(args.pcasl)
m0_img = load_image(args.m0)

mask_img = np.ones(asl_img[0, 0, :, :, :].shape)
if args.mask != '':
    mask_img = load_image(args.mask)


cbf_map = None
if args.cbf is not None:
    cbf_map = load_image(args.cbf)

att_map = None
if args.att is not None:
    att_map = load_image(args.att)


try:
    dw = [float(s) for s in args.dw]
    pld = [float(s) for s in args.pld]
    ld = [float(s) for s in args.ld]
except:
    dw = [float(s) for s in str(args.dw[0]).split()]
    pld = [float(s) for s in str(args.pld[0]).split()]
    ld = [float(s) for s in str(args.ld[0]).split()]

if not checkUpParameters():
    raise RuntimeError(
        'One or more arguments are not well defined. Please, revise the script call.'
    )


# Step 2: Show the input information to assist manual conference
if args.verbose:
    print(' --- Script Input Data ---')
    print('ASL file path: ' + args.pcasl)
    print('ASL image dimension: ' + str(asl_img.shape))
    print('Mask file path: ' + args.mask)
    print('Mask image dimension: ' + str(mask_img.shape))
    print('M0 file path: ' + args.m0)
    print('M0 image dimension: ' + str(m0_img.shape))
    print('PLD: ' + str(pld))
    print('LD: ' + str(ld))
    print('DW: ' + str(dw))
    if args.cbf != '':
        print('(optional) CBF map: ' + str(args.cbf))
    if args.att != '':
        print('(optional) ATT map: ' + str(args.att))
    print('Output file format: ' + str(args.file_fmt))


data = ASLData(
    pcasl=args.pcasl, m0=args.m0, ld_values=ld, pld_values=pld, dw_values=dw
)
recon = MultiDW_ASLMapping(data)
recon.set_brain_mask(mask_img)
if isinstance(cbf_map, np.ndarray) and isinstance(att_map, np.ndarray):
    recon.set_cbf_map(cbf_map)
    recon.set_att_map(att_map)

maps = recon.create_map()

# TODO Check print message not showing when cbf_map is None
save_path = args.out_folder + os.path.sep + 'cbf_map.' + args.file_fmt
if args.verbose and cbf_map is not None:
    print('Saving CBF map - Path: ' + save_path)
save_image(maps['cbf'], save_path)

save_path = (
    args.out_folder + os.path.sep + 'cbf_map_normalized.' + args.file_fmt
)
if args.verbose and cbf_map is not None:
    print('Saving normalized CBF map - Path: ' + save_path)
save_image(maps['cbf_norm'], save_path)

save_path = args.out_folder + os.path.sep + 'att_map.' + args.file_fmt
if args.verbose and att_map is not None:
    print('Saving ATT map - Path: ' + save_path)
save_image(maps['att'], save_path)

save_path = args.out_folder + os.path.sep + 'mte_kw_map.' + args.file_fmt
if args.verbose:
    print('Saving multiDW-ASL kw map - Path: ' + save_path)
save_image(maps['kw'], save_path)

if args.verbose:
    print('Execution: ' + parser.prog + ' finished successfully!')
