
from millrun.millrun import execute_profile, _parse_yaml
import pathlib

TEST_DATA_DIR = pathlib.Path(__file__).parent / "test_data"


def test__parse_yaml():
    yaml_data = _parse_yaml(TEST_DATA_DIR / "profiles.yaml")
    assert yaml_data == {
        "notebook1": {
            "notebook_dir_or_file": "./notebook1/notebook1.ipynb",
            "notebook_params": "./notebook1/notebook1_params.json",
            "output_dir": "./notebook1/output",
            "prepend": ["name", "design"],
            "append": ["executed"],
        },
        "notebook2": {
            "notebook_dir_or_file": "./notebook2",
            "notebook_params": "./notebook2/notebook2_params.json",
            "output_dir": "./notebook2/output",
            "prepend": ["tester"]
        },
    }

def test_execute_profile():
    yaml_file = TEST_DATA_DIR / "profiles.yaml"
    execute_profile(yaml_file)
    # If there are no errors, then the assert statement gets hit
    assert True