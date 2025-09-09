import json
import logging
import sys
from datetime import date, datetime
from os import environ
from pathlib import Path

import click

from gpas import constants, models, tasks, util
from gpas.client import env
from gpas.errors import AuthorizationError
from gpas.log_utils import configure_debug_logging


@click.group(name="GPAS", context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option()
@click.option(
    "--debug", is_flag=True, default=False, help="Enable verbose debug messages"
)
def main(*, debug: bool = False) -> None:
    """GPAS command line interface."""
    tasks.check_for_newer_version()
    util.display_cli_version()
    configure_debug_logging(debug)


@main.command()
@click.option(
    "--host",
    type=str,
    default=None,
    help="API hostname (for development)",
)
@click.option(
    "--check-expiry",
    is_flag=True,
    default=False,
    help="Check for a current token and print the expiry if exists",
)
def auth(*, host: str | None = None, check_expiry: bool = False) -> None:
    """Authenticate with GPAS."""
    host = env.get_host(host)
    if check_expiry:
        expiry = env.get_token_expiry(host)
        if expiry and env.is_auth_token_live(host):
            logging.info(f"Current token for {host} expires at {expiry}")
            return
        else:
            logging.info(f"You do not have a valid token for {host}")
    tasks.authenticate(host=host)


@main.command()
@click.option(
    "--host",
    type=str,
    default=None,
    help="API hostname (for development)",
)
def balance(
    *,
    host: str | None = None,
) -> None:
    """Check your GPAS account balance."""
    host = env.get_host(host)
    tasks.fetch_credit_balance(host=host)


@main.command()
def autocomplete() -> None:
    """Enable shell autocompletion."""
    shell = environ.get("SHELL", "/bin/bash").split("/")[-1]
    single_use_command = f'eval "$(_GPAS_COMPLETE={shell}_source gpas)"'
    print(f"Run this command to enable autocompletion:\n    {single_use_command}")  # noqa: T201
    print(  # noqa: T201
        f"Add this to your ~/.{shell}rc file to enable this permanently:\n"
        f"    command -v gpas > /dev/null 2>&1 && {single_use_command}"
    )


@main.command()
@click.argument(
    "input_csv",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
)
@click.option(
    "--output-dir",
    type=click.Path(
        file_okay=False, dir_okay=True, writable=True, exists=True, path_type=Path
    ),
    default=".",
    help="Output directory for the cleaned FastQ files, defaults to the current working directory.",
)
@click.option(
    "--threads",
    type=int,
    default=None,
    help="Number of alignment threads used during decontamination",
)
@click.option(
    "--skip-fastq-check", is_flag=True, help="Skip checking FASTQ files for validity"
)
def decontaminate(
    input_csv: Path,
    *,
    output_dir: Path = Path("."),
    threads: int = 1,
    skip_fastq_check: bool = False,
) -> None:
    """Decontaminate reads from provided csv samples."""
    batch = models.create_batch_from_csv(input_csv, skip_fastq_check)
    batch.validate_all_sample_fastqs()
    cleaned_batch_metadata = tasks.decontaminate_samples_with_hostile(
        batch, threads, output_dir
    )
    batch.update_sample_metadata(metadata=cleaned_batch_metadata)


@main.command()
@click.argument(
    "upload_csv",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
)
@click.option(
    "--threads",
    type=int,
    default=None,
    help="Number of alignment threads used during decontamination",
)
@click.option(
    "--save", is_flag=True, help="Retain decontaminated reads after upload completion"
)
@click.option(
    "--host",
    type=str,
    default=None,
    help="API hostname (for development)",
)
@click.option(
    "--skip-fastq-check", is_flag=True, help="Skip checking FASTQ files for validity"
)
@click.option(
    "--skip-decontamination",
    is_flag=True,
    default=False,
    help="Run decontamination prior to upload",
)
@click.option(
    "--output-dir",
    type=click.Path(
        file_okay=False, dir_okay=True, writable=True, exists=True, path_type=Path
    ),
    default=".",
    help="Output directory for the cleaned FastQ files, defaults to the current working directory.",
)
def upload(
    upload_csv: Path,
    *,
    threads: int = 1,
    save: bool = False,
    host: str | None = None,
    skip_decontamination: bool = True,
    skip_fastq_check: bool = False,
    output_dir: Path = Path("."),
) -> None:
    """Validate, decontaminate and upload reads to GPAS.

    Creates a mapping CSV file which can be used to download output
    files with original sample names.
    """
    host = env.get_host(host)
    tasks.check_version_compatibility(host=host)
    if skip_fastq_check and skip_decontamination:
        logging.warning(
            "Cannot skip FastQ checks and decontamination due to metadata requirements for upload, continuing with"
            "checks enabled."
        )
        skip_fastq_check = False
    batch = models.create_batch_from_csv(upload_csv, skip_fastq_check)

    if env.is_auth_token_live(host):
        tasks.fetch_credit_balance(host=host)
        tasks.validate_upload_permissions(batch, protocol=env.get_protocol(), host=host)
        if skip_decontamination:
            batch.validate_all_sample_fastqs()
            batch.update_sample_metadata()
        else:
            cleaned_batch_metadata = tasks.decontaminate_samples_with_hostile(
                batch, threads, output_dir=output_dir
            )
            batch.update_sample_metadata(metadata=cleaned_batch_metadata)
        tasks.upload_batch(
            batch=batch, save=save, skip_decontamination=skip_decontamination
        )
        tasks.fetch_credit_balance(host=host)
    else:
        raise AuthorizationError()


@main.command()
@click.argument("samples", type=str)
@click.option(
    "--filenames",
    type=str,
    default="main_report.json",
    help="Comma-separated list of output filenames to download",
)
@click.option(
    "--inputs", is_flag=True, help="Also download decontaminated input FASTQ file(s)"
)
@click.option(
    "--output-dir",
    type=click.Path(
        file_okay=False, dir_okay=True, writable=True, exists=True, path_type=Path
    ),
    default=".",
    help="Output directory for the downloaded files.",
)
@click.option(
    "--rename/--no-rename",
    default=True,
    help="Rename downloaded files using sample names when given a mapping CSV",
)
@click.option("--host", type=str, default=None, help="API hostname (for development)")
def download(
    samples: str,
    *,
    filenames: str = "main_report.json",
    inputs: bool = False,
    output_dir: Path = Path(),
    rename: bool = True,
    host: str | None = None,
) -> None:
    """Download input and output files associated with sample IDs or a mapping CSV file.

    That are created during upload.
    """
    host = env.get_host(host)
    if env.is_auth_token_live(host):
        if util.validate_guids(util.parse_comma_separated_string(samples)):
            tasks.download(
                samples=samples,
                filenames=filenames,
                inputs=inputs,
                out_dir=output_dir,
                host=host,
            )
        elif Path(samples).is_file():
            tasks.download(
                mapping_csv=Path(samples),
                filenames=filenames,
                inputs=inputs,
                out_dir=output_dir,
                rename=rename,
                host=host,
            )
        else:
            raise ValueError(
                f"{samples} is neither a valid mapping CSV path nor a comma-separated list of valid GUIDs"
            )
    else:
        raise AuthorizationError()


@main.command()
@click.argument("samples", type=str)
@click.option("--host", type=str, default=None, help="API hostname (for development)")
def query_raw(samples: str, *, host: str | None = None) -> None:
    """Fetch metadata for one or more SAMPLES in JSON format.

    SAMPLES should be command separated list of GUIDs or path to mapping CSV.
    """
    host = env.get_host(host)
    if util.validate_guids(util.parse_comma_separated_string(samples)):
        result = tasks.fetch_sample_metadata(samples=samples, host=host)
    elif (sample_path := Path(samples)).is_file():
        result = tasks.fetch_sample_metadata(mapping_csv=sample_path, host=host)
    else:
        raise ValueError(
            f"{samples} is neither a valid mapping CSV path nor a comma-separated list of valid GUIDs"
        )
    print(json.dumps(result, indent=4))  # noqa: T201


@main.command()
@click.argument("samples", type=str)
@click.option("--output_json", is_flag=True, help="Output status in JSON format")
@click.option("--host", type=str, default=None, help="API hostname (for development)")
def query_status(
    samples: str, *, output_json: bool = False, host: str | None = None
) -> None:
    """Fetch processing status for one or more SAMPLES.

    SAMPLES should be command separated list of GUIDs or path to mapping CSV.
    """
    host = env.get_host(host)
    if util.validate_guids(util.parse_comma_separated_string(samples)):
        result = tasks.fetch_sample_status(samples=samples, host=host)
    elif (sample_path := Path(samples)).is_file():
        result = tasks.fetch_sample_status(mapping_csv=sample_path, host=host)
    else:
        raise ValueError(
            f"{samples} is neither a valid mapping CSV path nor a comma-separated list of valid GUIDs"
        )
    if output_json:
        print(json.dumps(result, indent=4))  # noqa: T201
    else:
        for name, status in result.items():
            print(f"{name} \t{status}")  # noqa: T201


@main.command()
def download_index() -> None:
    """Download and cache host decontamination index."""
    tasks.download_index()


@main.command()
@click.argument(
    "upload_csv", type=click.Path(exists=True, dir_okay=False, readable=True)
)
@click.option("--host", type=str, default=None, help="API hostname (for development)")
def validate(upload_csv: Path, *, host: str | None = None) -> None:
    """Validate a given upload CSV."""
    host = env.get_host(host)
    batch = models.create_batch_from_csv(upload_csv)
    tasks.validate_csv(host, batch)
    tasks.validate_upload_permissions(
        batch=batch, protocol=env.get_protocol(), host=host
    )
    batch.validate_all_sample_fastqs()
    logging.info(f"Successfully validated {upload_csv}")


@main.command()
@click.argument(
    "samples-folder", type=click.Path(exists=True, file_okay=False), required=True
)
@click.option(
    "--output-csv",
    type=click.Path(dir_okay=False),
    default="upload.csv",
    help="Path to output CSV file",
    required=True,
)
@click.option("--batch-name", type=str, help="Batch name", required=True)
@click.option(
    "--collection-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=str(date.today()),
    show_default=True,
    help="Collection date (YYYY-MM-DD)",
    required=True,
)
@click.option(
    "--country",
    type=str,
    help="3-letter Country Code",
    required=True,
    default=constants.DEFAULT_COUNTRY,
    show_default=True,
)
@click.option(
    "--instrument-platform",
    type=click.Choice(["illumina", "ont"]),
    default=constants.DEFAULT_INSTRUMENTPLATFORM,
    help="Sequencing technology",
)
@click.option(
    "--subdivision",
    type=str,
    help="Subdivision",
    default=constants.DEFAULT_SUBDIVISION,
    show_default=True,
)
@click.option(
    "--district",
    type=str,
    help="District",
    default=constants.DEFAULT_DISTRICT,
    show_default=True,
)
@click.option(
    "--specimen-organism",
    "pipeline",
    type=click.Choice(["mycobacteria", "sars-cov-2"]),
    help="Specimen organism",
    default=constants.DEFAULT_PIPELINE,
    show_default=True,
)
@click.option(
    "--amplicon-scheme",
    type=click.Choice(tasks.fetch_amplicon_schemes()),
    help="Amplicon scheme, use only when SARS-CoV-2 is the specimen organism",
    default=None,
    show_default=True,
)
@click.option(
    "--ont_read_suffix",
    type=str,
    default=constants.DEFAULT_ONT_READ_SUFFIX,
    help="Read file ending for ONT fastq files",
    show_default=True,
)
@click.option(
    "--illumina_read1_suffix",
    type=str,
    default=constants.DEFAULT_ILLUMINA_READ1_SUFFIX,
    help="Read file ending for Illumina read 1 files",
    show_default=True,
)
@click.option(
    "--illumina_read2_suffix",
    type=str,
    default=constants.DEFAULT_ILLUMINA_READ2_SUFFIX,
    help="Read file ending for Illumina read 2 files",
    show_default=True,
)
@click.option("--max-batch-size", type=int, default=50, show_default=True)
def build_csv(
    samples_folder: Path,
    output_csv: Path,
    instrument_platform: str,
    batch_name: str,
    collection_date: datetime,
    country: str,
    subdivision: str = constants.DEFAULT_SUBDIVISION,
    district: str = constants.DEFAULT_DISTRICT,
    pipeline: str = constants.DEFAULT_PIPELINE,
    amplicon_scheme: str | None = None,
    host_organism: str = "homo sapiens",
    ont_read_suffix: str = constants.DEFAULT_ONT_READ_SUFFIX,
    illumina_read1_suffix: str = constants.DEFAULT_ILLUMINA_READ1_SUFFIX,
    illumina_read2_suffix: str = constants.DEFAULT_ILLUMINA_READ2_SUFFIX,
    max_batch_size: int = constants.DEFAULT_MAX_BATCH_SIZE,
) -> None:
    r"""Command to create upload csv from SAMPLES_FOLDER containing sample fastqs.

    Use max_batch_size to split into multiple separate upload csvs.

    Adjust the read_suffix parameters to match the file endings for your read files.
    """  # noqa: D205
    if len(country) != 3:
        raise ValueError(f"Country ({country}) should be 3 letter code")
    output_csv = Path(output_csv)
    samples_folder = Path(samples_folder)

    upload_data = models.UploadData(
        batch_name=batch_name,
        instrument_platform=instrument_platform,  # type: ignore
        collection_date=collection_date,
        country=country,
        subdivision=subdivision,
        district=district,
        specimen_organism=pipeline,  # type: ignore
        amplicon_scheme=amplicon_scheme,
        host_organism=host_organism,
        ont_read_suffix=ont_read_suffix,
        illumina_read1_suffix=illumina_read1_suffix,
        illumina_read2_suffix=illumina_read2_suffix,
        max_batch_size=max_batch_size,
    )

    tasks.build_upload_csv(
        samples_folder,
        output_csv,
        upload_data,
    )


@main.command()
@click.option("--host", type=str, default=None, help="API hostname (for development)")
def get_amplicon_schemes(*, host: str | None = None) -> None:
    """Get valid amplicon schemes from the server."""
    schemes = tasks.fetch_amplicon_schemes(host=host)
    logging.info("Valid amplicon schemes:")
    for scheme in schemes:
        logging.info(scheme)


if __name__ == "__main__":
    main(sys.argv[1:])
