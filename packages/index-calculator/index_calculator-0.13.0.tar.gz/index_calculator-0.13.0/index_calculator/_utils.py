import re
import warnings

from pyhomogenize import basics


def object_attrs_to_self(obj, slf, overwrite=True):
    """Copy object attributes to new object."""
    for attr in dir(obj):
        if attr[0] == "_":
            continue
        if overwrite is False and hasattr(slf, attr):
            continue
        if attr[0].isalpha():
            setattr(slf, attr, getattr(obj, attr))


def kwargs_to_self(kwargs, slf):
    """Write kwargs to new object."""
    if not hasattr(slf, "kwargs"):
        setattr(slf, "kwargs", kwargs)
    else:
        slf.kwargs.update(kwargs)
    for key, value in kwargs.items():
        if not hasattr(slf, key):
            setattr(slf, key, value)
        if getattr(slf, key) is None:
            setattr(slf, key, value)


def check_existance(attr_dict, slf):
    """Check existance of values."""
    for key, value in attr_dict.items():
        test = False
        if value is None:
            method = "raise"
            test = True
        if value == "N/A":
            method = "warn"
            test = True
        if value is True:
            method = ""
            test = True
        if test:
            if hasattr(slf, key):
                return getattr(slf, key)
            else:
                msg = f"No {key} is selected. '{key}=...'"
                if method == "raise":
                    raise ValueError(msg)
                elif method == "warn":
                    warnings.warn(msg)
        return value


def get_time_range_as_str(time, fmt):
    ts = time[0]
    te = time[-1]
    if not isinstance(ts, str):
        ts = basics().date_to_str(ts, fmt)
    if not isinstance(te, str):
        te = basics().date_to_str(te, fmt)
    return [ts, te]


def get_alpha_name(var_name):
    return "".join(filter(lambda x: x.isalpha(), var_name))


def get_numb_name(var_name):
    return "".join(filter(lambda x: x.isdigit(), var_name))


def get_replace_name(var_name):
    return re.sub(r"\d+", "YY", var_name)
