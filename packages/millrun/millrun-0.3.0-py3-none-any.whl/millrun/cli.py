import json
from ruamel.yaml import YAML
from typing import Optional, Any
from typing_extensions import Annotated
import pathlib

import typer
from .millrun import execute_run, execute_profile



APP_INTRO = typer.style(
    """
Executes a notebook or directory of notebooks using the provided bulk parameters JSON file
""",
    fg=typer.colors.BRIGHT_YELLOW,
    bold=True,
)

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help=APP_INTRO,
    pretty_exceptions_show_locals=False,
)


@app.command(
    name="run",
    no_args_is_help=True,
    help="Executes a notebook or directory of notebooks using the provided bulk parameters JSON file",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def run(
    ctx: typer.Context,
    notebook_dir_or_file: Annotated[
        str,
        typer.Argument(
            help="Path to a notebook file or a directory containing notebooks.",
        ),
    ],
    notebook_params: Annotated[
        str,
        typer.Argument(
            help=(
                "JSON file that contains parameters for notebook execution. "
                "Can either be a 'list of dict' or 'dict of list'."
            ),
        ),
    ],
    output_dir: Annotated[
        Optional[str],
        typer.Option(
            help=(
                "Directory to place output files into. If not provided"
                " the current working directory will be used."
            ),
        ),
    ] = None,
    prepend: Annotated[
        Optional[str],
        typer.Option(
            help=(
                "Prepend components to use on output filename."
                "Can use dict keys from 'params' which will be evaluated."
                "(Comma-separated values)."
            ),
            callback=lambda x: x.split(",") if x else None,
        ),
    ] = None,
    append: Annotated[
        Optional[str],
        typer.Option(
            help=(
                "Append components to use on output filename."
                "Can use dict keys from 'params' which will be evaluated."
                "(Comma-separated values)."
            ),
            callback=lambda x: x.split(",") if x else None,
        ),
    ] = None,
    recursive: bool = False,
    exclude_glob_pattern: Optional[str] = None,
    include_glob_pattern: Optional[str] = None,
):
    if ctx.invoked_subcommand is None:
        if output_dir is not None:
            output_dir = pathlib.Path(output_dir)
        else:
            output_dir = pathlib.Path.cwd()

        # Typical execution

        execute_run(
            notebook_dir_or_file,
            notebook_params,
            output_dir,
            prepend,
            append,
            recursive,
            exclude_glob_pattern,
            include_glob_pattern,
            use_multiprocessing=True,
            # **kwargs
            )


@app.command(
    name="profile",
    help="Run a bulk millrun execution running against a profile YAML file",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def profile_execution(profile_filepath: str):
    profile_file = pathlib.Path.cwd() / pathlib.Path(profile_filepath)
    execute_profile(profile_file)

if __name__ == "__main__":
    app()
