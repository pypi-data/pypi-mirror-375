# Millrun

## A Python library and CLI tool for automating the execution of papermill

### Motivation

Papermill is great: it parameterizes a single notebook for you. Ok, so what about this whole directory of notebooks that I would like to execute with this list of different parameters?

**Millrun** Will execute either a single notebook or all of the notebooks in a directory (recursively, if you want) and using either a list of alternative parameter dictionaries or a dictionary with a list of variations.

In short, it iterates both over notebooks in a directory AND over lists of parameters.

_When executed as a CLI tool, notebooks are executed in parallel using multi-processing_.

## Installation

`pip install millrun`

## Usage: Python Library

```python
import millrun

millrun.execute_run(
    notebook_dir_or_file: pathlib.Path | str,
    bulk_params: list | dict,
    output_dir: Optional[pathlib.Path | str] = None,
    output_prepend_components: Optional[list[str]] = None,
    output_append_components: Optional[list[str]] = None,
    recursive: bool = False,
    exclude_glob_pattern: Optional[str] = None,
    include_glob_pattern: Optional[str] = None,
    use_multiprocessing: bool = False,
    **kwargs, # kwargs are passed through to papermill
)
```

## Usage: CLI tool

```
millrun --help
                                                                                                       
 Usage: millrun [OPTIONS] NOTEBOOK_DIR_OR_FILE PARAMS                                                  
                                                                                                       
 Executes a notebook or directory of notebooks using the provided bulk parameters JSON file            
                                                                                                       
                                                                                                       
╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────╮
│ *    notebook_dir_or_file      TEXT  Path to a notebook file or a directory containing notebooks.   │
│                                      [default: None]                                                │
│                                      [required]                                                     │
│ *    params                    TEXT  JSON file that contains parameters for notebook execution. Can │
│                                      either be a 'list of dict' or 'dict of list'.                  │
│                                      [default: None]                                                │
│                                      [required]                                                     │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────╮
│ --output-dir                                TEXT  Directory to place output files into. If not      │
│                                                   provided the file directory will be used.         │
│                                                   [default: None]                                   │
│ --prepend                                   TEXT  Prepend components to use on output filename.Can  │
│                                                   use dict keys from 'params' which will be         │
│                                                   evaluated.(Comma-separated values).               │
│                                                   [default: None]                                   │
│ --append                                    TEXT  Append components to use on output filename.Can   │
│                                                   use dict keys from 'params' which will be         │
│                                                   evaluated.(Comma-separated values).               │
│                                                   [default: None]                                   │
│ --recursive               --no-recursive          [default: no-recursive]                           │
│ --exclude-glob-pattern                      TEXT  [default: None]                                   │
│ --include-glob-pattern                      TEXT  [default: None]                                   │
│ --help                                            Show this message and exit.                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

### Example

While the `prepend` argument is optional, it is highly recommend you take advantage of it. If not, your output file names will be automatically prepended with an integer index to differentiate the output files.

```
millrun ./Notebooks_Dir params.json --prepend id_key_in_params
```

Where `id_key_in_params` is one of the keys in your params.json that you can use to uniquely identify each iteration. If you do not have a single unique key, you can provide a list of keys and they will all be prepended:

Lets say my params.json looked like this:

```json
{
    "x_values": [0, 1, 2],
    "y_values": [45, 32, 60],
}

```

I could execute like this:

```
millrun ./Notebooks_Dir params.json --prepend x_values,y_values,results
```

And my output files would look like:

```
0-45-results-special_calculation.ipynb
1-32-results-special_calculation.ipynb
2-60-results-special_calculation.ipynb
```

**Notice**: Since "results" was not a key in my params.json, it gets passed through as a string literal.

## Organizing your parameters

You can have your parameters dictionary/JSON in one of two formats:

### Format 1: A list of dicts

```python
[
    {"param1": 0, "param2": "hat", "param3": 21.2},
    {"param1": 1, "param2": "cat", "param3": 34.3},
    {"param1": 2, "param2": "bat", "param3": 200.0}
]
```

Where each notebook given to millrun will execute against each dictionary in the list.


### Format 2: A dict of lists

```python
{
    "param1": [0, 1, 2],
    "param2": ["hat", "cat", "bat"],
    "param3": [21.2, 34.3, 200.0]
}
```

This format is offered as a convenience format. Internally, it is converted into "Format 1" prior to execution.


## CLI parallel execution

Since millrun iterates over two dimensions (each notebook and then dict of parameters in the list), there are two ways of parellelizing: 

1. Execute each notebook in sequence and parallelize the execution of the different parameter variations
2. Execute each notebook in parallel and sequentialize the execution of the different parameter variations

Because of my own personal use cases, it is more efficient for me to use **1.** because I have way more parameter variations than I do notebooks. 

However, this method becomes inefficient if you have MANY notebooks and only 1-3 variations. In that case, you would probably prefer the method **2.**. It is still faster than single-process execution (like you get )

If you need this use case then feel free to raise an issue and/or contribute a PR to implement it as an option for execution.


## Troubleshooting

There seems to be an un-planned-for behaviour (by me) with the parallel execution where if there is an error in the execution process, that iteration is simply skipped. I don't have any `try`/`except` in the code that causes this. 

So, if you are finding that execution seems to happen "too quickly" or you have missing files, try executing your run in single-process mode as a Python library and see if you get any errors. Then correct and re-run in CLI mode.