from thkit.pkg import check_package

# check_package("dpdispatcher", auto_install=True)
check_package(
    "dpdispatcher",
    auto_install=True,
    git_repo="https://github.com/thangckt/dpdispatcher.git@master",
)

import asyncio
import time
from copy import deepcopy
from math import ceil
from pathlib import Path

from dpdispatcher import Machine, Resources, Submission, Task
from dpdispatcher.entrypoints.submission import handle_submission

from thkit.jobman.helper import (
    _COLOR_MAP,
    _info_current_dispatch,
    _init_jobman_logger,
    _parse_multi_mdict,
    _remote_info,
)
from thkit.stuff import chunk_list, text_color


#####SECTION Dispatcher
def _prepare_submission(
    mdict: dict,
    work_dir: str,
    task_list: list[Task],
    forward_common_files: list[str] = [],
    backward_common_files: list[str] = [],
    create_remote_path: bool = True,
) -> Submission:
    """Function to simplify the preparation of the [Submission](https://docs.deepmodeling.com/projects/dpdispatcher/en/latest/api/dpdispatcher.html#dpdispatcher.Submission) object for dispatching jobs.

    Args:
        mdict (dict): a dictionary contain settings of the remote machine. The parameters described in [here](https://docs.deepmodeling.com/projects/dpdispatcher/en/latest/machine.html)
        create_remote_path (bool): whether to create the remote path if it does not exist.
    """
    machine_dict = mdict["machine"]
    resources_dict = mdict["resources"]

    ### revise input path to absolute path and as_string
    abs_machine_dict = machine_dict.copy()
    abs_machine_dict["local_root"] = Path("./").resolve().as_posix()

    ### Create remote_path if not exist
    if create_remote_path:
        execute_command = machine_dict.get("remote_profile").get("execute_command", "")
        remote_path = machine_dict.get("remote_root")
        abs_machine_dict["remote_profile"]["execute_command"] = (
            f"{execute_command} && ([! -d {remote_path}] && mkdir -p {remote_path}) "
        )

    ### Set default values
    if "group_size" not in resources_dict:
        resources_dict["group_size"] = 1

    submission = Submission(
        machine=Machine.load_from_dict(abs_machine_dict),
        resources=Resources.load_from_dict(resources_dict),
        work_base=work_dir,
        task_list=task_list,
        forward_common_files=forward_common_files,
        backward_common_files=backward_common_files,
    )
    return submission


#####ANCHOR Synchronous submission
def submit_job_chunk(
    mdict: dict,
    work_dir: str,
    task_list: list[Task],
    forward_common_files: list[str] = [],
    backward_common_files: list[str] = [],
    machine_index: int = 0,
    Logger: object = None,
):
    """Function to submit a jobs to the remote machine. The function will:

    - Prepare the task list
    - Make the submission of jobs to remote machines
    - Wait for the jobs to finish and download the results to the local machine

    Args:
        mdict (dict): a dictionary contain settings of the remote machine. The parameters described in the [remote machine schema](https://thangckt.github.io/thkit_doc/schema_doc/config_remote_machine/). This dictionary defines the login information, resources, execution command, etc. on the remote machine.
        task_list (list[Task]): a list of [Task](https://docs.deepmodeling.com/projects/dpdispatcher/en/latest/task.html) objects. Each task object contains the command to be executed on the remote machine, and the files to be copied to and from the remote machine. The dirs of each task must be relative to the `work_dir`.
        forward_common_files (list[str]): common files used for all tasks. These files are i n the `work_dir`.
        backward_common_files (list[str]): common files to download from the remote machine when the jobs are finished.
        machine_index (int): index of the machine in the list of machines.
        Logger (object): the logger object to be used for logging.

    Note:
        - Split the `task_list` into chunks to control the number of jobs submitted at once.
        - Should not use the `Local` contexts, it will interference the current shell environment which leads to the unexpected behavior on local machine. Instead, use another account to connect local machine with `SSH` context.
    """
    if Logger is None:
        Logger = _init_jobman_logger()

    num_tasks = len(task_list)
    machine_dict = mdict["machine"]
    text = text_color(
        f"Assigned {num_tasks} jobs to Machine {machine_index} \n{_remote_info(machine_dict)}",
        color=_COLOR_MAP[machine_index],
    )
    Logger.info(text)

    ### Divide task_list into chunks
    job_limit = mdict.get("job_limit", 5)
    chunks = chunk_list(task_list, job_limit)
    old_time = None
    for chunk_index, task_list_current_chunk in enumerate(chunks):
        num_tasks_current_chunk = len(task_list_current_chunk)
        new_time = time.time()
        text = _info_current_dispatch(
            num_tasks,
            num_tasks_current_chunk,
            job_limit,
            chunk_index,
            old_time,
            new_time,
        )
        Logger.info(text)
        submission = _prepare_submission(
            mdict=mdict,
            work_dir=work_dir,
            task_list=task_list_current_chunk,
            forward_common_files=forward_common_files,
            backward_common_files=backward_common_files,
        )
        try:
            submission.run_submission()
        except Exception as e:
            handle_submission(submission_hash=submission.get_hash(), download_finished_task=True)
            err_text = f"Machine {machine_index} has error job: \n\t{e}"
            Logger.error(text_color(err_text, color=_COLOR_MAP[machine_index]))
        old_time = new_time
    return


#####ANCHOR Asynchronous submission
_machine_locks = {}  # Dictionary to store per-machine locks


def _get_machine_lock(machine_index):
    if machine_index not in _machine_locks:
        _machine_locks[machine_index] = asyncio.Lock()
    return _machine_locks[machine_index]


async def _run_submission_wrapper(submission, Logger, check_interval=30, machine_index=0):
    """Ensure only one instance of 'submission.run_submission' runs at a time.
    - If use one global lock for all machines, it will prevent concurrent execution of submissions on different machines. Therefore, each machine must has its own lock, so different machines can process jobs in parallel.
    """
    lock = _get_machine_lock(machine_index)  # Get per-machine lock
    async with lock:  # Prevents concurrent execution
        try:
            await asyncio.to_thread(submission.run_submission, check_interval=check_interval)
        except Exception as e:
            await asyncio.to_thread(
                handle_submission,
                submission_hash=submission.get_hash(),
                download_finished_task=True,
            )
            err_text = f"Machine {machine_index} has error job: \n\t{e}"
            Logger.error(text_color(err_text, color=_COLOR_MAP[machine_index]))
        finally:
            del submission  # free up memory
    return


async def async_submit_job_chunk(
    mdict: dict,
    work_dir: str,
    task_list: list[Task],
    forward_common_files: list[str] = [],
    backward_common_files: list[str] = [],
    machine_index: int = 0,
    Logger: object = None,
):
    """Convert `submit_job_chunk()` into an async function but only need to wait for the completion of the entire `for` loop (without worrying about the specifics of each operation inside the loop)

    Note:
        - An async function normally contain a `await ...` statement to be awaited (yield control to event loop)
        - If the 'event loop is blocked' by a asynchronous function (it will not yield control to event loop), the async function will wait for the completion of the synchronous function. So, the async function will not be executed asynchronously. Try to use `await asyncio.to_thread()` to run the synchronous function in a separate thread, so that the event loop is not blocked.
    """
    if Logger is None:
        Logger = _init_jobman_logger()

    num_tasks = len(task_list)
    machine_dict = mdict["machine"]
    text = text_color(
        f"Assigned {num_tasks} jobs to Machine {machine_index} \n{_remote_info(machine_dict)}",
        color=_COLOR_MAP[machine_index],
    )
    Logger.info(text)

    ### Divide task_list into chunks
    job_limit = mdict.get("job_limit", 5)
    chunks = chunk_list(task_list, job_limit)
    timer = {f"oldtime_{machine_index}": None}  # dynamic variable name
    for chunk_index, task_list_current_chunk in enumerate(chunks):
        num_tasks_current_chunk = len(task_list_current_chunk)
        timer[f"newtime_{machine_index}"] = time.time()
        text = _info_current_dispatch(
            num_tasks,
            num_tasks_current_chunk,
            job_limit,
            chunk_index,
            timer[f"oldtime_{machine_index}"],
            timer[f"newtime_{machine_index}"],
            machine_index,
        )
        Logger.info(text)
        submission = _prepare_submission(
            mdict=mdict,
            work_dir=work_dir,
            task_list=task_list_current_chunk,
            forward_common_files=forward_common_files,
            backward_common_files=backward_common_files,
        )
        # await asyncio.to_thread(submission.run_submission, check_interval=30)  # this is old, may cause (10054) error
        await _run_submission_wrapper(submission, Logger, 30, machine_index)
        timer[f"oldtime_{machine_index}"] = timer[f"newtime_{machine_index}"]
    Logger.info(
        text_color(f"Machine {machine_index} finished all jobs.", color=_COLOR_MAP[machine_index])
    )
    return


#####!SECTION


#####SECTION Support functions used for `alff` package
def _alff_prepare_task_list(
    command_list: list[str],
    task_dirs: list[str],
    forward_files: list[str],
    backward_files: list[str],
    outlog: str,
    errlog: str,
    # delay_fail_report: bool = True,
) -> list[Task]:
    """Prepare the task list for alff package.

    The feature of jobs in `alff` package are they have the same: command_list, forward_files, backward_files. So this function is to shorthand prepare the list of Task object for `alff` package. For general usage, should prepare the task list from scratch.

    Args:
        command_list (list[str]): the list of commands to be executed on the remote machine.
        task_dirs (list[str]): the list of directories for each task. They must be relative to the `work_dir` in function `_prepare_submission`
        forward_files (list[str]): the list of files to be copied to the remote machine. These files must existed in each `task_dir`.
        backward_files (list[str]): the list of files to be copied back from the remote machine.
        outlog (str): the name of the output log file.
        errlog (str): the name of the error log file.
        # delay_fail_report (bool): whether to delay the failure report until all tasks are done. This is useful when there are many tasks, and we want to wait all tasks finished instead of "the controller interupts if one task fail".

    Returns:
        list[Task]: a list of Task objects.
    """
    command = " &&\n".join(command_list)
    # if delay_fail_report:
    #     command = f"({command}) || :"  # this treat fail jobs as finished jobs -> should not be used.

    ### Define the task_list
    task_list = [None] * len(task_dirs)
    for i, path in enumerate(task_dirs):
        task_list[i] = Task(
            command=command,
            task_work_path=path,
            forward_files=forward_files,
            backward_files=backward_files,
            outlog=outlog,
            errlog=errlog,
        )
    return task_list


#####ANCHOR Submit to multiple machines
async def alff_submit_job_multi_remotes(
    multi_mdict: dict,
    prepare_command_list: callable,
    work_dir: str,
    task_dirs: list[str],
    forward_files: list[str],
    backward_files: list[str],
    forward_common_files: list[str] = [],
    backward_common_files: list[str] = [],
    mdict_prefix: str = "dft",
    Logger: object = None,
):
    """Submit jobs to multiple machines asynchronously.

    Args:
        multi_mdict (dict): the big_dict contains multiple `mdicts`. Each `mdict` contains parameters of one remote machine, which parameters as in the [remote machine schema](https://thangckt.github.io/thkit_doc/schema_doc/config_remote_machine/).
        prepare_command_list(callable): a function to prepare the command list based on each remote machine.
        mdict_prefix(str): the prefix to select remote machines for the same purpose. Example: 'dft', 'md', 'train'.
    """
    if Logger is None:
        Logger = _init_jobman_logger()

    mdict_list = _parse_multi_mdict(multi_mdict, mdict_prefix)
    num_machines = len(mdict_list)
    Logger.info(f"Distribute {len(task_dirs)} jobs across {num_machines} remote machines")

    remain_task_dirs = deepcopy(task_dirs)
    background_runs = []
    for i, current_mdict in enumerate(mdict_list):
        current_work_load = current_mdict.get("work_load_ratio", None)

        ### Divide task_dirs
        if not current_work_load:
            current_work_load = 1.0 / num_machines
            num_jobs = ceil(len(remain_task_dirs) * current_work_load)
        else:
            num_jobs = ceil(len(task_dirs) * current_work_load)

        if num_jobs <= len(remain_task_dirs):
            current_task_dirs = remain_task_dirs[:num_jobs]
            remain_task_dirs = remain_task_dirs[num_jobs:]
            num_machines -= 1
        else:
            current_task_dirs = remain_task_dirs
            remain_task_dirs = []

        ### Prepare task_list
        command_list = prepare_command_list(current_mdict)
        task_list = _alff_prepare_task_list(
            command_list=command_list,
            task_dirs=current_task_dirs,
            forward_files=forward_files,
            backward_files=backward_files,
            outlog=f"{mdict_prefix}_out.log",
            errlog=f"{mdict_prefix}_err.log",
        )

        ### Submit jobs
        if len(current_task_dirs) > 0:
            async_task = async_submit_job_chunk(
                mdict=current_mdict,
                work_dir=work_dir,
                task_list=task_list,
                forward_common_files=forward_common_files,
                backward_common_files=backward_common_files,
                machine_index=i,
                Logger=Logger,
            )
            background_runs.append(async_task)
            # Logger.debug(f"Assigned coroutine to Machine {i}: {async_task}")
    await asyncio.gather(*background_runs)
    return


#####!SECTION
