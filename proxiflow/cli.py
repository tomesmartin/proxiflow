import click
import polars as pl

from .config import Config
from .utils import *
from .core import Cleaner, Normalizer


@click.group(invoke_without_command=True, no_args_is_help=True)
@click.option(
    "--config-file",
    "-c",
    required=True,
    type=click.Path(exists=True),
    help="Path to configuration file",
)
@click.option(
    "--input-file",
    "-i",
    required=True,
    type=click.Path(exists=True),
    help="Path to input data file",
)
@click.option(
    "--output-file",
    "-o",
    required=True,
    type=click.Path(exists=False),
    help="Path to output data file",
)
@click.pass_context
@click.version_option()
def main(ctx, config_file, input_file, output_file):
    # Set up logger
    logger = get_logger(__name__)

    # Load configuration
    config = Config(config_file)

    # Load data
    try:
        data = load_data(input_file, input_file_format=config.input_format)
    except FileNotFoundError as e:
        logger.error("Input file not found: %s", str(e))
    except ValueError as e:
        logger.error("Error parsing input file: %s", str(e))

    # Perform data cleaning
    cleaner = Cleaner(config)
    try:
        cleaned_data = cleaner.clean_data(data)
    except ValueError as e:
        logger.error("Error cleaning data: %s", str(e))
        return

    # Perform data normalization
    normalizer = Normalizer(config)
    # normalized_data = normalizer.normalize(cleaned_data)
    try:
        normalized_data = normalizer.normalize(cleaned_data)
    except Exception as e:
        logger.error("Normalizing data: %s", str(e))
        return

    # Perform feature engineering

    try:
        write_data(
            normalized_data, output_file, output_file_format=config.output_format
        )
    except Exception as e:
        logger.error(f"Error writing data to file {output_file}: {str(e)}")

    # Log completion message
    logger.info("Data preprocessing complete.")


if __name__ == "__main__":
    main()
