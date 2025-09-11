import pathlib
import json
from ruamel.yaml import YAML
from typing import Optional, Any
import papermill as pm
import functools as ft
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from rich.progress import Progress, BarColumn, TimeRemainingColumn, TimeElapsedColumn
from rich import print
from rich.text import Text


def execute_profile(profile_path: str, selected_profiles: Optional[list[str]] = None):
    """
    Executes millrun according to the arguments provided in the profile file

    The profile is a dict in the following structure:
        {
            "profile_name1": {
                "notebook_dir_or_file": ..., # Req'd key
                "notebook_params": ..., # Req'd key
                "output_dir": ..., # Optional
                "prepend": ..., # Optional
                "append": ..., # Optional
                "recursive": ..., # Optional
                "exclude_glob_pattern": ..., # Optional
                "include_glob_pattern": ..., # Optional
                "use_multiprocessing": ..., # Optional
            },
            "profile_name2": {
                ... #same as above
            },
            "profile_name3": {
                ... # same as above
            }
        }
    """
    profile_path = pathlib.Path(profile_path)
    working_directory = profile_path.parent

    profile_data = _parse_yaml(profile_path)
    for profile_name, profile_kwargs in profile_data.items():
        if selected_profiles is not None:
            if profile_name in selected_profiles:
                execute_run(**profile_kwargs, profile_name=profile_name, working_directory=working_directory)
        else:
            execute_run(**profile_kwargs, profile_name=profile_name, working_directory=working_directory)


def execute_run(
    notebook_dir_or_file: pathlib.Path | str,
    notebook_params: list | dict | str | pathlib.Path,
    output_dir: Optional[pathlib.Path | str] = None,
    prepend: Optional[list[str]] = None,
    append: Optional[list[str]] = None,
    recursive: bool = False,
    exclude_glob_pattern: Optional[str] = None,
    include_glob_pattern: Optional[str] = None,
    use_multiprocessing: bool = False,
    **kwargs,
) -> list[pathlib.Path] | None:
    """
    Executes the notebooks contained in the notebook_dir_or_file using the parameters in
    'notebook_params'.

    'notebook_dir_or_file': If a directory, then will execute all of the notebooks
        within the directory
    'notebook_params':
        Either a dict in the following format:

        {
            "key1": ["list", "of", "values"], # All lists of values must be same length
            "key2": ["list", "of", "values"],
            "key3": ["list", "of", "values"],
            ...
        },

        -or-

        A list in the following format:

        [
            {"key1": "value", "key2": "value"}, # All keys
            {"key1": "value", "key2": "value"},
            {"key1": "value", "key2": "value"},
            ...
        ]

        -or-

        A str or pathlib.Path to a file

    'output_dir': The directory for all output files. If None,
        files will be output in the same directory as the source file.
    'prepend': A list of str representing the keys used
        in 'notebook_params'. These keys will be used to retrieve the value
        for the key in each iteration of 'notebook_params' and they will
        be used to name the output file be prepending them to the
        original filename. If a key is not found then the key will
        be interpreted as a str literal and will be added asis.
    'append': Same as the prepend components but
        these components will be used at the end of the original filename.
    'recursive': If True, and if 'notebook_dir_or_file' is a directory,
        then will execute notebooks within all sub-directories.
    'exclude_glob_pattern': A glob-style pattern of files to exclude.
        If None, then all files willbe included.
    'include_glob_pattern': A glob-style pattern of files to include. If
        None then all files will be included.
    '**kwargs': Passed on to papermill.execute_notebook
    """
    notebook_dir_or_file = pathlib.Path(notebook_dir_or_file)
    output_dir = pathlib.Path(output_dir)
    if "working_directory" in kwargs:
        notebook_dir_or_file = pathlib.Path(kwargs['working_directory']) / notebook_dir_or_file
        output_dir = pathlib.Path(kwargs['working_directory']) / output_dir
    if isinstance(notebook_params, (list, dict)):
        notebook_params_list = validate_notebook_params(notebook_params)
    elif isinstance(notebook_params, (str, pathlib.Path)):
        if "working_directory" in kwargs:
            print("HERE")
            notebook_params = pathlib.Path(kwargs['working_directory']) / notebook_params
        params_data = _parse_json(notebook_params)
        notebook_params_list = validate_notebook_params(params_data)


    notebook_dir = None
    notebook_filename = None
    if notebook_dir_or_file.is_dir():
        notebook_dir = notebook_dir_or_file
    else:
        notebook_dir = notebook_dir_or_file.parent.resolve()
        notebook_filename = notebook_dir_or_file.name

    if output_dir is None:
        output_dir = notebook_dir
    if not output_dir.exists():
        output_dir.mkdir(exist_ok=True, parents=True)
    if notebook_filename is not None:
        execute_notebooks(
            notebook_dir / notebook_filename,
            notebook_params_list,
            prepend,
            append,
            output_dir,
            use_multiprocessing,
            **kwargs,
        )
    else:
        glob_method = notebook_dir.glob
        if recursive:
            glob_method = notebook_dir.rglob

        excluded_paths = set()
        if exclude_glob_pattern is not None:
            excluded_paths = set(glob_method(exclude_glob_pattern))

        glob_pattern = include_glob_pattern
        if include_glob_pattern is None:
            glob_pattern = "*.ipynb"
        included_paths = set(glob_method(glob_pattern))

        notebook_paths = sorted(included_paths - excluded_paths)
        if "profile_name" in kwargs:
            task_name = f"Executing profile: {kwargs['profile_name']}"
            print(task_name)
        for notebook_path in notebook_paths:
            execute_notebooks(
                notebook_path,
                notebook_params_list,
                prepend,
                append,
                output_dir,
                use_multiprocessing,
                **kwargs,
            )


def check_unequal_value_lengths(notebook_params: dict[str, list]) -> bool | dict:
    """
    Returns False if all list values are equal length. Returns a dict
    of value lengths otherwise.
    """
    acc = {}
    for k, v in notebook_params.items():
        try:
            acc.update({k: len(v)})
        except TypeError:
            raise ValueError(
                f"The values of the bulk_param keys must be lists, not: '{k: v}'"
            )
    all_values = set(acc.values())
    if len(all_values) == 1:
        return False
    else:
        return acc


def convert_notebook_params_to_list(notebook_params: dict[str, list]):
    """
    Converts a dict of lists into a list of dicts.
    """
    iter_length = len(list(notebook_params.values())[0])
    notebook_params_list = []
    for idx in range(iter_length):
        inner_acc = {}
        for parameter_name, parameter_values in notebook_params.items():
            inner_acc.update({parameter_name: parameter_values[idx]})
        notebook_params_list.append(inner_acc)
    return notebook_params_list


def execute_notebooks(
    notebook_path: pathlib.Path,
    notebook_params_list: dict[str, Any],
    prepend: list[str],
    append: list[str],
    output_dir: pathlib.Path,
    use_multiprocessing: bool,
    **kwargs,
):
    total_variations = len(notebook_params_list)
    if not use_multiprocessing:
        with Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
            refresh_per_second=1,  # bit slower updates
        ) as progress:
            task_id = progress.add_task(notebook_path.name, total=total_variations)
            for idx, notebook_params in list(enumerate(notebook_params_list)):
                execute_notebook(
                    notebook_filename=notebook_path,
                    notebook_params=notebook_params,
                    prepend=prepend,
                    append=append,
                    output_dir=output_dir,
                    **kwargs,
                )
                progress.update(task_id, completed=idx + 2)
    else:
        with Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
            refresh_per_second=1,  # bit slower updates
        ) as progress:
            # Multiprocessing approach inspired by
            # https://www.deanmontgomery.com/2022/03/24/rich-progress-and-multiprocessing/
            futures = []  # keep track of the jobs
            with multiprocessing.Manager() as manager:
                _progress = manager.dict()
                overall_progress_task = progress.add_task(
                    f"{notebook_path.name}", visible=True, total=total_variations
                )
                with ProcessPoolExecutor() as executor:
                    for idx, notebook_params in enumerate(notebook_params_list):
                        futures.append(
                            executor.submit(
                                execute_notebook,
                                notebook_path,
                                notebook_params,
                                prepend,
                                append,
                                output_dir,
                                total_variations,
                                idx,
                                _progress,
                                overall_progress_task,
                            )
                        )

                    # monitor the progress:
                    while (
                        n_finished := sum([future.done() for future in futures])
                    ) < len(futures):
                        progress.update(overall_progress_task, completed=n_finished + 1)


def execute_notebook(
    notebook_filename: pathlib.Path,
    notebook_params: dict,
    prepend: list[str],
    append: list[str],
    output_dir: pathlib.Path,
    total_variations: Optional[int] = None,
    current_iteration: Optional[int] = None,
    _progress: Optional[dict] = None,
    _task_id: Optional[str] = None,
    **kwargs,
):
    output_name = get_output_name(
        notebook_filename, prepend, append, notebook_params, current_iteration
    )
    pm.execute_notebook(
        notebook_filename,
        output_path=output_dir / output_name,
        parameters=notebook_params,
        progress_bar=False,
        cwd=str(notebook_filename.parent),
        **kwargs,
    )
    if _progress is not None:
        _progress[_task_id] = {"progress": current_iteration, "total": total_variations}


def get_output_name(
    notebook_filename: str,
    prepend: list[str] | None,
    append: list[str] | None,
    notebook_params: dict[str, Any],
    current_index: int,
) -> str:
    """
    Returns the output name given the included components.
    """
    if prepend is None:
        prepend = [str(current_index)]
    if append is None:
        append = []
    prepends = [notebook_params.get(comp, comp) for comp in prepend]
    appends = [notebook_params.get(comp, comp) for comp in append]
    prepend_str = "-".join(prepends)
    append_str = "-".join(appends)
    notebook_filename = pathlib.Path(notebook_filename)
    output_name = (
        "-".join(
            [elem for elem in [prepend_str, notebook_filename.stem, append_str] if elem]
        )
        + notebook_filename.suffix
    )
    return output_name


def _parse_json(filepath: Optional[str] = None) -> dict:
    if filepath is None:
        return None
    filepath = pathlib.Path(filepath)
    if not filepath.exists():
        raise ValueError(
            f"The notebook parameters file does not exist: {str(filepath)}"
        )
    else:
        with open(filepath, "r") as file:
            return json.load(file)



def _parse_yaml(filepath: Optional[str] = None) -> dict:
    if filepath is None:
        return None
    filepath = pathlib.Path(filepath)
    if not filepath.exists():
        raise ValueError(f"The profile file does not exist: {str(filepath)}")
    else:
        with open(filepath, "r") as file:
            yaml = YAML(typ="safe")
            profile_data = yaml.load(file)
    return profile_data


def validate_notebook_params(params_data: list | dict) -> list:
    if isinstance(params_data, dict):
        unequal_lengths = check_unequal_value_lengths(params_data)
        if unequal_lengths:
            raise ValueError(
                f"All lists in the notebook_params dict must be of equal length.\n"
                f"The following keys have unequal length: {unequal_lengths}"
            )
        notebook_params_list = convert_notebook_params_to_list(params_data)
    elif isinstance(params_data, list):
        notebook_params_list = params_data

    return notebook_params_list
