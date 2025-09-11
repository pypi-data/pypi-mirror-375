import logging

import pandas as pd

from anemoi.inference.config.run import RunConfiguration
from anemoi.inference.runners import create_runner

from eagle.tools.log import setup_simple_log

logger = logging.getLogger("eagle.tools")


def create_anemoi_config(
    init_date: pd.Timestamp,
    main_config: dict,
) -> dict:
    """
    Create the config that will be passed to anemoi-inference.
    As of right now the "extract_lam" functionality is really only used to save out a static lam file when wanted.
    This could be easily updated if we think we would ever be interested in running inference over just CONUS.

    Args:
        init_date (str): date of initialization.
        extract_lam (bool): logic to extract lam domain, or run whole nested domain.
        lead_time (int): desired lead time to save out. Default=LEAD_TIME.
        lam (bool): true/false indication if LAM. Default=LAM.
        checkpoint_path (str): path to checkpoint. Default=CHECKPOINT.
        input_data_path (str): path to input data when not using LAM (e.g. you trained on 1 source). Default=INPUT_DATA_PATH.
        lam_path (str): path to regional data when using LAM. Default=LAM_PATH.
        global_path (str: path to global data when using LAM. Default=GLOBAL_PATH.
        output_path (str): path for saving files. Default=OUTPUT_PATH.

    Returns:
        dict -- config for anemoi-inference.
    """
    date_str = init_date.strftime("%Y-%m-%dT%H")

    lead_time = main_config.get("lead_time")
    config = {
        "checkpoint": main_config["checkpoint_path"],
        "date": date_str,
        "lead_time": lead_time,
        "input": {"dataset": main_config["input_dataset_kwargs"]},
        "runner": main_config.get("runner", "default"),
    }
    if main_config.get("extract_lam", False):
        config["output"] = {
            "extract_lam": {
                "output": {
                    "netcdf": {
                        "path": f"{main_config['output_path']}/{date_str}.{lead_time}h.lam.nc",
                    },
                },
            },
        }
    else:
        config["output"] = {
            "netcdf": f"{main_config['output_path']}/{date_str}.{lead_time}h.nc",
        }

    return config


def run_forecast(
    init_date: pd.Timestamp,
    main_config: dict,
) -> None:
    """
    Inference pipeline.

    Args:
        init_date (str): date of initialization.

    Returns:
        None -- files saved out to output path.
    """
    anemoi_config = create_anemoi_config(
        init_date=init_date,
        main_config=main_config,
    )
    run_config = RunConfiguration.load(anemoi_config)
    runner = create_runner(run_config)
    runner.execute()
    return


def main(config):
    """Runs Anemoi inference pipeline over many initialization dates.

    \b
    Note:
        There may be ways to do this directly with anemoi-inference, and
        there might be more efficient ways to parallelize inference by
        better using anemoi-inference.
        However, this works, especially for low resolution applications.

    \b
    Note:
        The arguments documented here are passed via a config dictionary.

    \b
    Config Args:
        start_date (str): The first initial condition date to process.
        \b
        end_date (str): The last initial condition date to process.
        \b
        freq (str): Frequency string for the date range (e.g., "6h").
        \b
        lead_time (int): Forecast lead time in hours (e.g., 240 = 240h = 10days).
        \b
        checkpoint_path (str): Path to the trained model checkpoint for inference.
        \b
        input_dataset_kwargs (dict): A dictionary of arguments passed to
            anemoi-dataset to open an anemoi dataset for initial conditions.
        \b
        output_path (str): Directory where the output NetCDF files will be saved in the format
            f"{output_path}/{t0}.{lead_time}h.nc", or
            if extract_lam=True, then f"{output_path}/{t0}.{lead_time}h.lam.nc"
        \b
        runner (str, optional): The name of the anemoi-inference runner to use.
            Defaults to "default".
        \b
        extract_lam (bool, optional): If True, extracts and saves only the LAM
            (Limited Area Model) domain from the output. Only used for Nested model configurations.
            Defaults to False.
    """

    setup_simple_log()

    dates = pd.date_range(start=config["start_date"], end=config["end_date"], freq=config["freq"])

    logger.info(f" --- Running Inference --- ")
    logger.info(f"Initial Conditions:\n{dates}")
    for d in dates:
        logger.info(f"Processing {d}")
        run_forecast(
            init_date=d,
            main_config=config,
        )
        logger.info(f"Done with {d}")
    logger.info(f" --- Done Running Inference --- \n")
