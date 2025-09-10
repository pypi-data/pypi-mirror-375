from pathlib import Path


def add_dicom_conversion_subparser(subparsers):
    # Add subcommands
    convert_parser = subparsers.add_parser(
        "convert", help="Convert dicom data to the NIfTI format"
    )
    convert_parser.add_argument(
        "dicoms",
        help="Path to a dicom directory or a file containing a list of dicom directories",
        type=Path,
    )
    convert_parser.add_argument(
        "output_dir",
        type=Path,
        help="Path to the output directory",
    )
    convert_parser.add_argument(
        "--data-dir",
        "-d",
        type=Path,
        default=Path(""),
        help="Data directory for the input dicoms (i.e. {data_dir}/dicom_folder) - useful for remapping in docker. Default is no data directory.",
    )
    convert_parser.add_argument(
        "--n-processes",
        "-n",
        type=int,
        default=1,
        help="Number of processes to use for conversion (default: 1)",
    )
    convert_parser.add_argument(
        "--threads-per-process",
        "-t",
        type=int,
        default=4,
        help="Maximum number of transformation threads per process (default: 4)",
    )
    convert_parser.add_argument(
        "--axial-only",
        "-ax",
        action="store_true",
        help="Only convert axial series",
    )
    convert_parser.add_argument(
        "--no-mip", "-nm", action="store_true", help="Do not convert MIP series"
    )
    convert_parser.add_argument(
        "--no-resampling",
        "-nr",
        action="store_true",
        help="Do not resample the dicoms to LAS orientation",
    )
    convert_parser.add_argument(
        "--resample-interpolation-order",
        "-i",
        type=int,
        default=3,
        help="Interpolation order for resampling (default: 3)",
    )
    convert_parser.add_argument(
        "--resample-padding",
        "-p",
        type=int,
        default=-1024,
        help="Padding Hounsfield Unit for resampling (default: -1024)",
    )
    convert_parser.add_argument(
        "--validate-orthogonal",
        "-v",
        action="store_true",
        help="Validate that the dicoms are orthogonal. Will not convert gantry tilted series.",
    )
    convert_parser.add_argument(
        "--skip-slice-increment-validation",
        "-ssi",
        action="store_true",
        help="Skip validation of consistent slice increment in DICOM series. Use with caution",
    )
    convert_parser.add_argument(
        "--skip-instance-number-validation",
        "-sin",
        action="store_true",
        help="Skip validation of dicom instance numbers. Use with caution.",
    )
    convert_parser.add_argument(
        "--skip-slice-count-validation",
        "-ssc",
        action="store_true",
        help="Skip validation of slice counts in the dicoms. Use with caution.",
    )
    convert_parser.add_argument(
        "--min-slice-count",
        "-s",
        type=int,
        default=30,
        help="Minimum number of slices to consider a series valid (default: 30)",
    )
    convert_parser.add_argument(
        "--db-batch-size",
        "-b",
        type=int,
        default=100,
        help="Batch size for database insertion (default: 100)",
    )
