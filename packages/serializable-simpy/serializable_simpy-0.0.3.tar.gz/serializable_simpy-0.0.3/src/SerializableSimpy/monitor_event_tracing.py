"""Event tracing utilities for SerializableSimpy.

This module provides helpers to *trace* the event loop by wrapping
:py:meth:`Environment.next_event` and recording which callback (event function)
is executed at which simulation time.

Reference (SimPy equivalent):
    https://simpy.readthedocs.io/en/latest/topical_guides/monitoring.html#event-tracing
"""

from SerializableSimpy.core import Environment, Process, Event
from functools import wraps
from typing import Callable


def trace(env: Environment, callback: Callable) -> None:
    """Enable event tracing on an environment.

    This function wraps ``env.next_event`` so that every time the environment
    fetches the next scheduled event, ``callback`` is invoked with the tuple
    ``(t, eid, func)`` where:

    - ``t`` is the event's scheduled time,
    - ``eid`` is the zero-based index of the event pop operation
      (derived from ``env._num_pop - 1``),
    - ``func`` is the function (callback) that will be executed for the event.

    The wrapper *does not* change the event selection; it only observes it.

    :param env: The simulation environment to instrument.
    :type env: Environment
    :param callback: A function called as ``callback(time, event_id, func)``.
    :type callback: Callable
    """

    def get_wrapper(env_step, callback: Callable):
        @wraps(env_step)
        def tracing_step(until):
            t, f, a = env_step(until)
            callback(t, env._num_pop - 1, f)
            return t, f, a

        return tracing_step

    env.next_event = get_wrapper(env.next_event, callback)


#: ---------------------------------------------------------------------------
#: Name extraction helpers
#: ---------------------------------------------------------------------------


def _from_func2func_name(event: Callable) -> str:
    """Return the function name for an *event* method.

    Example: ``on_tick``.

    :param event: Bound method representing the event callback.
    :type event: Callable
    :return: The qualified function name.
    :rtype: str
    """
    return event.__func__.__qualname__


def _from_func2class_name(event: Callable) -> str:
    """Return the class name of the object owning the *event* method.

    Example: ``Clock``.

    :param event: Bound method representing the event callback.
    :type event: Callable
    :return: The class name.
    :rtype: str
    """
    return type(event.__self__).__name__


def _from_func2object_name(event: Callable) -> str:
    """Return an object's ``name`` attribute or ``"noname"`` if absent.

    Example: ``clock.name`` → ``"fast"``; if missing, returns ``"noname"``.

    :param event: Bound method representing the event callback.
    :type event: Callable
    :return: Object name or ``"noname"``.
    :rtype: str
    """
    obj = event.__self__
    return getattr(obj, "name", "noname")


#: ---------------------------------------------------------------------------
#: List-backed monitors (chronological view)
#: ---------------------------------------------------------------------------


def monitor_list_class(data: list, t: float, eid: int, event: Callable) -> None:
    """Append ``(t, eid, class_name)`` to a list-backed log.

    :param data: Target list to append to.
    :type data: list
    :param t: Event time.
    :type t: float
    :param eid: Event identifier (zero-based pop count).
    :type eid: int
    :param event: Event callback (bound method).
    :type event: Callable
    """
    txt = _from_func2class_name(event)
    data.append((t, eid, txt))


def monitor_list_object(data: list, t: float, eid: int, event: Callable) -> None:
    """Append ``(t, eid, object_name)`` to a list-backed log.

    :param data: Target list to append to.
    :type data: list
    :param t: Event time.
    :type t: float
    :param eid: Event identifier (zero-based pop count).
    :type eid: int
    :param event: Event callback (bound method).
    :type event: Callable
    """
    txt = _from_func2object_name(event)
    data.append((t, eid, txt))


def monitor_list_func(data: list, t: float, eid: int, event: Callable) -> None:
    """Append ``(t, eid, func_name)`` to a list-backed log.

    :param data: Target list to append to.
    :type data: list
    :param t: Event time.
    :type t: float
    :param eid: Event identifier (zero-based pop count).
    :type eid: int
    :param event: Event callback (bound method).
    :type event: Callable
    """
    txt = _from_func2func_name(event)
    data.append((t, eid, txt))


#: ---------------------------------------------------------------------------
#: Dict-backed monitors (aggregated counts)
#: ---------------------------------------------------------------------------


def _plus_one(data: dict, k: str) -> None:
    """Increment the counter for key ``k`` in a dict-backed accumulator.

    :param data: Mapping of keys to occurrence counts.
    :type data: dict
    :param k: Key to increment.
    :type k: str
    """
    data[k] = data.get(k, 0) + 1


def monitor_dict_class(data: dict, t: float, eid: int, event: Callable) -> None:
    """Increment the count for ``class_name`` in a dict-backed log.

    :param data: Dict accumulator of counts.
    :type data: dict
    :param t: Event time (unused).
    :type t: float
    :param eid: Event identifier (unused).
    :type eid: int
    :param event: Event callback (bound method).
    :type event: Callable
    """
    txt = _from_func2class_name(event)
    _plus_one(data, txt)


def monitor_dict_object(data: dict, t: float, eid: int, event: Callable) -> None:
    """Increment the count for ``object_name`` in a dict-backed log.

    :param data: Dict accumulator of counts.
    :type data: dict
    :param t: Event time (unused).
    :type t: float
    :param eid: Event identifier (unused).
    :type eid: int
    :param event: Event callback (bound method).
    :type event: Callable
    """
    txt = _from_func2object_name(event)
    _plus_one(data, txt)


def monitor_dict_func(data: dict, t: float, eid: int, event: Callable) -> None:
    """Increment the count for ``func_name`` in a dict-backed log.

    :param data: Dict accumulator of counts.
    :type data: dict
    :param t: Event time (unused).
    :type t: float
    :param eid: Event identifier (unused).
    :type eid: int
    :param event: Event callback (bound method).
    :type event: Callable
    """
    txt = _from_func2func_name(event)
    _plus_one(data, txt)


#: ---------------------------------------------------------------------------
#: File-backed monitors (tab-separated chronological log)
#: ---------------------------------------------------------------------------


def monitor_file_class(file, t: float, eid: int, event: Callable) -> None:
    """Write ``t<TAB>eid<TAB>class_name`` to a file-like object.

    :param file: Writable file-like object with ``write(str)``.
    :type file: IO[str]
    :param t: Event time.
    :type t: float
    :param eid: Event identifier.
    :type eid: int
    :param event: Event callback (bound method).
    :type event: Callable
    """
    txt = _from_func2class_name(event)
    file.write(f"{t}\t{eid}\t{txt}\n")


def monitor_file_object(file, t: float, eid: int, event: Callable) -> None:
    """Write ``t<TAB>eid<TAB>object_name`` to a file-like object.

    :param file: Writable file-like object with ``write(str)``.
    :type file: IO[str]
    :param t: Event time.
    :type t: float
    :param eid: Event identifier.
    :type eid: int
    :param event: Event callback (bound method).
    :type event: Callable
    """
    txt = _from_func2object_name(event)
    file.write(f"{t}\t{eid}\t{txt}\n")


def monitor_file_func(file, t: float, eid: int, event: Callable) -> None:
    """Write ``t<TAB>eid<TAB>func_name`` to a file-like object.

    :param file: Writable file-like object with ``write(str)``.
    :type file: IO[str]
    :param t: Event time.
    :type t: float
    :param eid: Event identifier.
    :type eid: int
    :param event: Event callback (bound method).
    :type event: Callable
    """
    txt = _from_func2func_name(event)
    file.write(f"{t}\t{eid}\t{txt}\n")
