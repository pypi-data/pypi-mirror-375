import subprocess as sp

import simplejson as json
from flask import current_app as app

from ..exceptions import ProcessingError


def execute_sandbox(script_name, json_input=None):
    """Execute the script in a sandbox.

    Args:
        script_name -- The filename of the script.
        json_input -- The data the use as input in the script.
    """
    # TODO: Whitelist the modules the user is allowed to import in the rules
    # TODO: Add a time out for the execution of the user's code
    # TODO: Limit the memory allowed for the user's code execution
    # TODO: Prevent the user to writing to stdout
    p = sp.Popen(
        [
            "docker",
            "run",
            "--rm",
            "-i",
            "registry.gitlab.com/decide.imt-atlantique/deseasion/sandbox",
            script_name,
        ],
        stdin=sp.PIPE,
        stdout=sp.PIPE,
        stderr=sp.PIPE,
    )
    result, _ = p.communicate(input=json_input.encode())
    return result


def load_json_bytes(bytes_data):
    """Loads a json bytes object.

    Raises:
        ProcessingError if the json data has an 'error' key or an unknown key.
    """
    if not bytes_data:
        raise ProcessingError("Unknown error in the data rule")
    try:
        result = json.loads(bytes_data.decode())
    except ValueError as err:
        app.logger.info("Error while parsing text: {}".format(bytes_data))
        raise err
    if "error" in result:
        raise ProcessingError(result["error"])
    elif "data" in result:
        return result["data"]
    else:
        raise ProcessingError(
            "Unknown error during the processing of the data"
        )


def evaluate_discrete_rule(data, rule, stats=None):
    """Evaluate the discrete model rule with the data.

    Args:
        data (list): A JSON-serializable list of dict to use as the input for
            the rules.
        rule (str): A Python code.

    Returns:
        A list of booleans.
    """
    data_dict = {"data": data, "code": rule}
    if stats is not None:
        data_dict["statistics"] = stats
    json_input = json.dumps(data_dict, ignore_nan=True)
    result = execute_sandbox("process_category.py", json_input)
    result_list = load_json_bytes(result)
    # Verify that all the processed values are boolean
    if not all([isinstance(value, bool) for value in result_list]):
        raise ProcessingError(
            "The result of a rule evaluation should be a boolean"
        )
    return [value is True for value in result_list]


def evaluate_continuous_rule(data, rule, stats=None):
    """Evaluate the continuous model rule with the data.

    Args:
        data (list): A JSON-serializable list of dict to use as the input for
            the rules.
        rule (str): A Python code.
        stats (dict): A dictionary with the statistics on the global attributes

    Returns:
        A list of dict.
    """
    data_dict = {"data": data, "code": rule}
    if stats is not None:
        data_dict["statistics"] = stats
    json_input = json.dumps(data_dict, ignore_nan=True)
    result = execute_sandbox("process_rule.py", json_input)
    result_list = load_json_bytes(result)
    return result_list
