import numpy as np

"""
Misc. functions for general use
"""


def ensure_sequence(x):
    """Ensure given object is in the form of a sequence

    If object is scalar, return as length-1 list
    """
    if isinstance(x, (list, tuple, np.ndarray)):
        return x
    else:
        return [x, ]


def find_nearest_idx(array, value):
    """Return idx for the array element nearest to the given value
    """
    idx = np.searchsorted(array, value)
    if np.abs(value - array[idx - 1]) < np.abs(value - array[idx]):
        return idx - 1
    else:
        return idx


def str_to_bool(string, true_options=("yes", "y", "true"),
                false_options=("no",  "n", "false")):
    """Converts string to boolean, e.g. for parsing shell input

    parameters
    ----------
    string : str
        string to convert to bool (case insensitive)
    true_options : [str]
        (lowercase) strings which evaluate to True
    false_options : [str]
        (lowercase) strings which evaluate to False
    """
    if string.lower() in true_options:
        return True
    elif string.lower() in false_options:
        return False
    else:
        raise Exception(f'Undefined string for boolean conversion: {string}')
