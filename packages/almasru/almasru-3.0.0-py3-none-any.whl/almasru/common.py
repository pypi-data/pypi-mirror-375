from typing import Callable
import logging
import warnings
import functools


def check_error(fn: Callable) -> Callable:
    """Prevents operation if the record is containing an error

    :param fn: Method that should not to be executed in case of error

    :return: Wrapper function of the decorator
    """

    def wrapper(*args, **kwargs):
        """Wrapper function
        """
        rec = args[0]

        if rec.error is False and (rec.data is not None or (hasattr(rec, 'src_data') and rec.src_data is not None)):
            rec = fn(*args, **kwargs)
        else:
            logging.error(f'{repr(rec)}: due to error to the record, process "{fn.__name__}" skipped.')
        return rec

    wrapper.__doc__ = fn.__doc__

    return wrapper


def deprecated(reason: str) -> Callable:
    """
    Decorator to mark functions or classes as deprecated.

    :param reason: Explanation for the deprecation.
    :return: Decorator that issues a DeprecationWarning when the decorated object is used.
    """
    def decorator(obj: Callable) -> Callable:
        if isinstance(obj, type):
            # If decorating a class
            orig_init = obj.__init__
            @functools.wraps(orig_init)
            def new_init(self, *args, **kwargs):
                warnings.warn(
                    f"Class {obj.__name__} is deprecated: {reason}",
                    category=DeprecationWarning,
                    stacklevel=2
                )
                orig_init(self, *args, **kwargs)
            obj.__init__ = new_init
            return obj
        else:
            # If decorating a function or method
            @functools.wraps(obj)
            def wrapper(*args, **kwargs):
                warnings.warn(
                    f"{obj.__name__} is deprecated: {reason}",
                    category=DeprecationWarning,
                    stacklevel=2
                )
                return obj(*args, **kwargs)
            return wrapper  # type: ignore
    return decorator