import datetime
import logging
import time
import warnings
from math import ceil
from pathlib import Path

from dpdispatcher.dlog import dlog

from thkit import THKIT_ROOT
from thkit.config import load_config, validate_config
from thkit.pkg import create_logger
from thkit.stuff import text_color

#####ANCHOR Change logfile path
# "%Y%b%d_%H%M%S" "%Y%m%d_%H%M%S"
_DEFAULT_LOG_FILE = f"{time.strftime('%y%b%d_%H%M%S')}_dispatch.log"


def change_logpath_dispatcher(newlogfile: str = _DEFAULT_LOG_FILE):
    """Change the logfile of dpdispatcher."""
    try:
        for hl in dlog.handlers[:]:  # Remove all old handlers
            hl.close()
            dlog.removeHandler(hl)

        fh = logging.FileHandler(newlogfile)
        # fmt = logging.Formatter(
        #     "%(asctime)s | %(name)s-%(levelname)s: %(message)s", "%Y%b%d %H:%M:%S"
        # )
        fmt = logging.Formatter(
            "%(asctime)s | dispatch-%(levelname)s: %(message)s", "%Y%b%d %H:%M:%S"
        )
        fh.setFormatter(fmt)
        dlog.addHandler(fh)
        dlog.info(f"LOG INIT: dispatcher log direct to {newlogfile}")

        ### Remove the old log file if it exists
        if Path("./dpdispatcher.log").is_file():
            Path("./dpdispatcher.log").unlink()
    except Exception as e:
        warnings.warn(f"Error during change logfile_path {e}. Use the original path.")
    return


#####ANCHOR helper functions
_COLOR_MAP = {
    0: "blue",
    1: "green",
    2: "yellow",
    3: "magenta",
    4: "cyan",
    5: "red",
    6: "white",
    7: "white",
    8: "white",
    9: "white",
    10: "white",
}


def _info_current_dispatch(
    num_tasks: int,
    num_tasks_current_chunk: int,
    job_limit,
    chunk_index,  # start from 0
    old_time=None,
    new_time=None,
    machine_index=0,
) -> str:
    """Return the information of the current chunk of tasks."""
    total_chunks = ceil(num_tasks / job_limit)
    remaining_tasks = num_tasks - chunk_index * job_limit
    text = f"Machine {machine_index} is handling {num_tasks_current_chunk}/{remaining_tasks} jobs [chunk {chunk_index + 1}/{total_chunks}]."
    ### estimate time remaining
    if old_time is not None and new_time is not None:
        time_elapsed = new_time - old_time
        time_remain = time_elapsed * (total_chunks - chunk_index)
        delta_str = str(datetime.timedelta(seconds=time_remain)).split(".", 2)[0]
        text += f" ETC {delta_str}"
    text = text_color(text, color=_COLOR_MAP[machine_index])  # make color
    return text


def _remote_info(machine_dict) -> str:
    """Return the remote machine information.
    Args:
        mdict (dict): the machine dictionary
    """
    remote_path = machine_dict["remote_root"]
    hostname = machine_dict["remote_profile"]["hostname"]
    info_text = f"{' ' * 12}Remote host: {hostname}\n"
    info_text += f"{' ' * 12}Remote path: {remote_path}"
    return info_text


def _init_jobman_logger(logfile: str = _DEFAULT_LOG_FILE):
    """Initialize the default logger not provided"""
    Path("log").mkdir(parents=True, exist_ok=True)  # create log directory
    time_str = time.strftime("%y%m%d_%H%M%S")  # "%y%b%d" "%Y%m%d"
    DEFAULT_LOGFILE = f"job/{time_str}_jobman.log"

    Logger = create_logger("alff", level="INFO", log_file=DEFAULT_LOGFILE)
    change_logpath_dispatcher(DEFAULT_LOGFILE)
    return Logger


def validate_machine_config(machine_file: str):
    """Validate the YAML file contains multiple machines configs. This function is used to validate machine configs at very beginning of program to avoid later errors.

    Notes:
        - To specify multiple remote machines for the same purpose, the top-level keys in the machine config file should start with the same prefix. Example:
            - `train_1`, `train_2`,... for training jobs
            - `lammps_1`, `lammps_2`,... for lammps jobs
            - `gpaw_1`, `gpaw_2`,... for gpaw jobs
    """
    SCHEMA_MACHINE_FILE = f"{THKIT_ROOT}/jobman/schema/schema_machine.yml"
    schema = load_config(SCHEMA_MACHINE_FILE)
    multi_mdict = load_config(machine_file)
    for k, v in multi_mdict.items():
        validate_config(config_dict={k: v}, schema_dict={k: schema["tha"]})

    ### validate each type of machine config
    # for k, v in config.items():
    #     if k.startswith("md"):
    #         validate_config(config_dict={k: v}, schema_dict={k: schema["tha"]})
    #     elif k.startswith("train"):
    #         validate_config(config_dict={k: v}, schema_dict={k: schema["train"]})
    #     elif k.startswith("dft"):
    #         validate_config(config_dict={k: v}, schema_dict={k: schema["dft"]})
    return


def _parse_multi_mdict(multi_mdict: dict, mdict_prefix: str = "") -> list[dict]:
    """Parse multiple machine dicts from a multi-machine dict based on the prefix.

    Args:
        multi_mdict (dict): the bid dict contains multiple machines configs
        mdict_prefix (str): the prefix to select remote machines for the same purpose. Example: 'dft', 'md', 'train'.

    Returns:
        list[dict]: list of machine dicts
    """
    mdict_list = [v for k, v in multi_mdict.items() if k.startswith(mdict_prefix)]
    assert len(mdict_list) > 0, f"No remote machines found for the mdict_prefix: '{mdict_prefix}'"
    return mdict_list


def load_multi_machine_config(machine_file: str, mdict_prefix: str = "") -> list[dict]:
    """Load and validate the YAML file contains multiple machine configs. This function to load machine configs for general purpose usage.

    Args:
        machine_file (str): the path of the machine config file

    Returns:
        dict: the multi-machine dict
    """
    validate_machine_config(machine_file)
    multi_mdict = load_config(machine_file)
    mdict_list = _parse_multi_mdict(multi_mdict, mdict_prefix)
    return mdict_list
