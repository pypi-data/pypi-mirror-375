from heapq import heappop, heappush
from collections import deque
from typing import *
from functools import partial, wraps
import os


class EventInQueue:
    """
    Represents an event scheduled in the simulation environment's priority queue.
    Events are ordered by their simulation time, enabling time-based execution
    using a heap (priority queue).
    """

    def __init__(self, time: float, func_ptr: Callable, func_args: Tuple):
        """
        :param time: The simulation time when the event will be executed.
        :param func_ptr: The function (callback) to execute.
        :param func_args: The *args to give when the `func_ptr` is called.
        """
        self.time = time
        self.func_ptr = func_ptr
        self.func_args = func_args

    def __lt__(self, other: "EventInQueue"):
        """
        Usefull for the priority queue to sort EventInQueue objects.
        :param other: another  EventInQueue object
        :return: if other is superior to `self`
        """
        return self.time < other.time


class Environment:
    """
    Represents a discrete-event simulation environment.

    The environment maintains a priority queue of future events and simulates the
    progression of time by executing events in order. Processes and callbacks can be registered,
    and the environment runs until a given time.
    """

    def __init__(self, initial_time: float = 0):
        """
        Initialize the simulation environment.

        :param initial_time: The initial simulation time.
        :type initial_time: float
        """
        self.queue: List[EventInQueue] = []  # <-- heap
        self.now: float = initial_time
        self.processes: List["Process"] = []
        self._init = False
        self._num_insert = 0
        self._num_pop = 0
        self._until = 0.0

    def process(self, p: "Process"):
        """
        Register a process to the environment.

        :param p: A process object to be managed by the environment.
        :type p: Process
        """
        self.processes.append(p)
        self._init = False

    def _initialize(self):
        """
        Internal method to initialize all registered processes.
        """
        for p in self.processes:
            p.on_initialize(env=self)
        self._init = True

    def get_now(self) -> float:
        """
        Get the current simulation time.

        :return: The current simulation time.
        :rtype: float
        """
        return self.now

    def set_now(self, now: float):
        """
        Set the current simulation time.

        :param now: The new simulation time to set.
        :type now: float
        """
        self.now = now

    def run(self, until: float):
        """
        Run the simulation until the specified time.

        Events are processed in order until the current time reaches `until`.

        :param until: The simulation time to run until.
        :type until: float
        """
        if not self._init:
            self._initialize()

        func_ptr = "do_nothing"
        self._until = until

        while until > self.get_now():
            now, func_ptr, func_args = self.next_event(until)
            if until > now:
                self.set_now(now)
                func_ptr(*func_args)
            else:
                if func_ptr != "do_nothing":
                    event = EventInQueue(now, func_ptr, func_args)
                    heappush(self.queue, event)
                self.set_now(until)

    def timeout(self, t, func_ptr, func_args):
        """
        Schedule an event to occur after a delay.

        :param t: The delay (relative time) after which to schedule the event.
        :type t: float
        :param func_ptr: The function to execute at that time.
        :type func_ptr: Callable
        :param func_args: The arguments to pass to the function.
        :type func_args: tuple
        """
        event = EventInQueue(self.get_now() + t, func_ptr, func_args)
        heappush(self.queue, event)
        self._num_insert += 1

    def next_event(self, until) -> Tuple[float, Callable, Tuple[object]]:
        """
        Retrieve the next event from the queue.

        If the queue is empty, returns a "do nothing" event at the `until` time.

        :param until: The current simulation horizon.
        :type until: float
        :return: A tuple of (event time, function to call, function arguments).
        :rtype: tuple[float, Callable, tuple]
        """
        if not self.queue:
            return until, "do_nothing", tuple()
        event = heappop(self.queue)
        self._num_pop += 1
        return event.time, event.func_ptr, event.func_args


class Process:
    """
    Abstract base class for logical simulation processes.

    A process can be attached to a simulation environment and is expected to
    yield actions that schedule future events. Subclasses must implement the
    behavior for initialization and yielding.
    """

    def on_initialize(self, env: Environment) -> None:
        """
        Attach the process to a simulation environment.

        This allows the process to be moved between environments — for example,
        when composing or decomposing simulations into smaller environments.

        :param env: The environment to attach the process to.
        :type env: Environment
        :raises NotImplementedError: Must be implemented in a subclass.
        """
        raise NotImplementedError()

    def on_yield(self, *args) -> None:
        """
        Called when the process yields control to schedule events.

        The process is expected to insert one or more events into `self.env`.

        :param args: Arguments passed during the yield (can be events or commands).
        :type args: tuple
        :raises NotImplementedError: Must be implemented in a subclass.
        """
        raise NotImplementedError()


class Store:
    """Passive container for producing and consuming concrete objects.

    The store accepts items from producers and provides them to consumers via
    inserting callback events. It behaves like a LIFO queue because items are retrieved with
    ``list.pop()``. If an item is put and there are waiting consumers, consumers are
    notified immediately.
    """

    # URL in Simpy: https://simpy.readthedocs.io/en/latest/topical_guides/resources.html#stores

    def __init__(self, capacity: float = float("inf")):
        """Initialize the store.

        :param capacity: Maximum number of items that can be stored.
                         Use ``float('inf')`` for no bound.
        :type capacity: float
        """
        self.env = None
        self._capacity = capacity
        self.items = []
        self.waiting = []

    def on_initialize(self, env: Environment):
        """Attach a simulation environment to the store.

        :param env: Simulation environment.
        :type env: Environment
        """
        self.env = env

    def on_put(self, obj: Any):
        """Put an object into the store.

        If the store is not at capacity, the object is appended. If there are
        waiting consumers, their callbacks are invoked synchronously with
        available items in LIFO order until either no items or no waiters
        remain.

        .. note::
           When the store is at capacity, the store overflow, this method silently ignores the
           object (no exception is raised and nothing is queued).

        :param obj: The object to store.
        :type obj: Any
        """
        if len(self.items) < self._capacity:
            self.items.append(obj)
            if self.waiting:
                while self.waiting and self.items:
                    self.waiting.pop()(self.items.pop())

    def on_get(self, pro: Any):
        """Request an item from the store.

        If an item is available, the callback is invoked immediately with the
        retrieved item (LIFO). Otherwise, the callback is queued and will be
        invoked when a future ``on_put`` provides an item.

        :param pro: Callback taking a single argument (the retrieved item).
        :type pro: callable
        """
        if self.items:
            pro(self.items.pop())
        else:
            self.waiting.append(pro)


class Event:
    """Lightweight event system for scheduling callbacks.

    This class is conceptually similar to :class:`simpy.events.Event` from SimPy
    and can be used to model occurrences in a simulation environment that
    trigger one or more callbacks when completed or failed.

    For reference, see the original SimPy implementation:
    https://gitlab.com/team-simpy/simpy/-/blob/master/src/simpy/events.py?ref_type=heads#L51

    :ivar env: Simulation environment associated with the event.
    :vartype env: Environment
    :ivar callbacks: List of pending callbacks and their argument tuples.
    :vartype callbacks: list[tuple[Callable, tuple]]
    :ivar _ok: Boolean indicating event success (`True`), failure (`False`), or
               ``None`` if not yet triggered.
    :vartype _ok: bool | None
    """

    def __init__(self, env: Environment):
        """Initialize an event bound to a simulation environment.

        :param env: Simulation environment in which this event occurs.
        :type env: Environment
        """
        self.env = env
        self.callbacks = []
        self._ok = None

    def on_initialize(self, env):
        """Attach a simulation environment to the event.

        This replaces the current environment reference.

        :param env: Simulation environment.
        :type env: Environment
        """
        self.env = env
        # Store objects are passive and should not call callbacks

    def add_callback(self, callback: Callable, args=tuple()):
        """Register a callback to be invoked when the event is triggered.

        If the event has already succeeded (`_ok` is True), the callback is
        invoked immediately with the given arguments. Otherwise, it is queued
        for later invocation.

        :param callback: Callable to invoke upon event completion.
        :type callback: Callable
        :param args: Positional arguments to pass to the callback.
        :type args: tuple
        """
        if self._ok:
            callback(*args)
        else:
            self.callbacks.append((callback, args))

    def _call_callbacks(self):
        """Invoke all pending callbacks in LIFO order."""
        while self.callbacks:
            callback, args = self.callbacks.pop()
            callback(*args)
            # May be consider a mode where then event is scheduled
            # self.env.timeout(0, callback, args)

    def on_trigger(self):
        """Trigger the event and call all registered callbacks.

        Sets `_ok` to True and invokes all queued callbacks.
        """
        self._ok = True
        self._call_callbacks()

    def succeed(self):
        """Mark the event as successful and invoke callbacks.

        Ensures API compatibility with SimPy's :meth:`~simpy.events.Event.succeed`.

        :return: The event itself.
        :rtype: Event
        """
        self._ok = True
        self._call_callbacks()
        return self

    def fail(self):
        """Mark the event as failed and invoke callbacks.

        Ensures API compatibility with SimPy's :meth:`~simpy.events.Event.fail`.

        :return: The event itself.
        :rtype: Event
        """
        self._ok = False
        self._call_callbacks()
        return self

    def __and__(self, other: "Event") -> "Condition":
        """Return a Condition that is triggered when both events are processed.

        :param other: Another event.
        :type other: Event
        :return: A Condition that triggers when both events have occurred.
        :rtype: Condition
        """
        return Condition(self.env, Condition.all_events, [self, other])

    def __or__(self, other: "Event") -> "Condition":
        """Return a Condition that is triggered when either event is processed.

        The condition also triggers if both events occur concurrently.

        :param other: Another event.
        :type other: Event
        :return: A Condition that triggers when at least one event has occurred.
        :rtype: Condition
        """
        return Condition(self.env, Condition.any_events, [self, other])


class Condition(Event):
    """Composite event depending on other events.

    A ``Condition`` succeeds when a given evaluation function
    (such as :meth:`all_events` or :meth:`any_events`) applied
    to a set of sub-events returns ``True``. Sub-events must
    belong to the same :class:`Environment`.

    The ``Condition`` class extends :class:`Event`, so it can be
    yielded, combined with other events, and will trigger its own
    callbacks once the condition is satisfied.

    :param env: The simulation environment in which the condition is evaluated.
    :type env: Environment
    :param evaluate: Predicate function of the form
                     ``evaluate(events: tuple[Event, ...], count: int) -> bool``
                     that decides when the condition is met.
    :type evaluate: Callable
    :param events: Iterable of sub-events to be monitored.
    :type events: Iterable[Event]

    :raises ValueError: If the sub-events do not belong to the same environment.

    **Example**::

        cond = Condition(env, Condition.all_events, [evt1, evt2])
        cond.add_callback(lambda: print("Both events completed!"))

    .. note::
       This class is conceptually similar to :class:`simpy.events.Condition`.
    """

    def __init__(
        self,
        env: Environment,
        evaluate: Callable[[Tuple[Event, ...], int], bool],
        events: Iterable[Event],
    ):
        """Initialize a new condition event.

        :param env: The simulation environment in which the condition is evaluated.
        :type env: Environment
        :param evaluate: Predicate function deciding when the condition is met.
        :type evaluate: Callable[[tuple[Event, ...], int], bool]
        :param events: Iterable of sub-events to monitor.
        :type events: Iterable[Event]
        """
        super().__init__(env)
        self._evaluate = evaluate
        self._events = events
        self._count = 0

        # Immediately succeed if no events are provided.
        if not self._events:
            self.succeed()
            return

        # Check if events belong to the same environment.
        for event in self._events:
            if self.env != event.env:
                raise ValueError(
                    "It is not allowed to mix events from different environments"
                )

        # Attach a checker callback to each event.
        for event in self._events:
            event.callbacks.append((self._check, (event,)))

    def _check(self, event: Event) -> None:
        """Evaluate the condition when a sub-event triggers.

        Called whenever one of the monitored events is processed.
        If the evaluation function returns ``True``, the condition
        is marked successful.

        :param event: The event that has just been triggered.
        :type event: Event
        """
        self._count += 1

        if self._evaluate(self._events, self._count):
            self.succeed()

    @staticmethod
    def all_events(events: Tuple[Event, ...], count: int) -> bool:
        """Return ``True`` if all provided events have been triggered.

        :param events: Tuple of events to evaluate.
        :type events: tuple[Event, ...]
        :param count: Number of events that have been triggered so far.
        :type count: int
        :return: ``True`` if ``count`` equals the total number of events.
        :rtype: bool
        """
        return len(events) == count

    @staticmethod
    def any_events(events: Tuple[Event, ...], count: int) -> bool:
        """Return ``True`` if at least one of the provided events has been triggered.

        :param events: Tuple of events to evaluate.
        :type events: tuple[Event, ...]
        :param count: Number of events that have been triggered so far.
        :type count: int
        :return: ``True`` if ``count`` > 0 or if ``events`` is empty.
        :rtype: bool
        """
        return count > 0 or len(events) == 0


class Resource:
    """Counting resource with bounded capacity and a waiting queue.

    Requests are granted immediately while ``users < capacity``. Otherwise,
    requests are queued and granted later upon release.

    .. note::
       With the current implementation (``deque.append()`` + ``deque.pop()``),
       queued requests are served in **LIFO** order. If you want **FIFO**
       semantics, replace ``pop()`` with ``popleft()``.

    :param env: Simulation environment that manages time and scheduling.
    :type env: Environment
    :param capacity: Maximum number of concurrent users.
    :type capacity: int

    :ivar env: Simulation environment reference.
    :vartype env: Environment
    :ivar capacity: Maximum number of concurrent users.
    :vartype capacity: int
    :ivar users: Current number of active users holding the resource.
    :vartype users: int
    :ivar queue: Waiting requests as ``(callback, args)`` tuples.
    :vartype queue: collections.deque[tuple[Callable, tuple]]
    """

    def __init__(self, env: "Environment", capacity: int = 1):
        """Initialize the resource with a given capacity.

        :param env: Simulation environment.
        :type env: Environment
        :param capacity: Maximum number of concurrent users (``>= 1``).
        :type capacity: int
        """
        self.env = env
        self.capacity = capacity
        self.users = 0
        self.queue = deque()

    def on_initialize(self, env: "Environment") -> None:
        """Attach (or reattach) a simulation environment.

        :param env: Simulation environment.
        :type env: Environment
        """
        self.env = env
        # Resource objects are passive and should not call callbacks here.

    def on_request(
        self, what_to_do_when_release: Callable, args: Tuple = tuple()
    ) -> None:
        """Request access to the resource.

        If capacity is available, the request is granted immediately and the
        callback is invoked. Otherwise, the request is queued.

        :param what_to_do_when_release: Callback to execute once access is granted.
        :type what_to_do_when_release: Callable
        :param args: Positional arguments passed to the callback.
        :type args: tuple
        """
        if self.capacity > self.users:
            self.users += 1
            # self.users.append((what_to_do_when_release, args))  # if tracking holders
            what_to_do_when_release(*args)
        else:
            self.queue.append((what_to_do_when_release, args))

    def on_release(
        self, what_to_do_when_release: Callable, args: Tuple = tuple()
    ) -> None:
        """Release one unit of the resource and serve waiting requests.

        Decrements the active user count and grants access to queued requests
        while capacity is available. Requests are served in **LIFO** order with
        the current implementation.

        :param what_to_do_when_release: (Unused) callback from the releasing user.
                                        Included for interface symmetry.
        :type what_to_do_when_release: Callable
        :param args: (Unused) arguments from the releasing user.
        :type args: tuple
        """
        self.users -= 1

        # Move queued requests into active users as capacity allows.
        while self.queue and self.users < self.capacity:
            self.users += 1
            call, args = self.queue.pop()  # For FIFO, use: self.queue.popleft()
            call(*args)


class Interruption:
    """Utility to cancel scheduled callbacks in the environment's queue.

    This helper maintains a list of callbacks to interrupt. When
    :meth:`on_interruption` is called, it scans the environment's future-event
    queue and removes any queued events whose ``func_ptr`` matches a registered
    callback.

    .. note::
       - This only removes **scheduled** events; it does not affect callbacks
         that are already running.
       - Matching is done by function identity (``event.func_ptr is callback``).
       - The operation runs in :math:`O(n)` over ``env.queue``.
    """

    def __init__(self, env):
        """Initialize the interruption helper.

        :param env: The simulation environment providing the future-event queue.
        :type env: Environment
        """
        self.env = env
        self.callbacks_to_interrupt = []

    def on_init(self, env):
        """Attach or reattach a simulation environment.

        :param env: The simulation environment.
        :type env: Environment
        """
        self.env = env

    def add_interruption(self, callback_to_interupt):
        """Register a callback to be removed from the queue when interrupting.

        :param callback_to_interupt: The callback function to cancel if found
                                     among queued events.
        :type callback_to_interupt: Callable
        """
        self.callbacks_to_interrupt.append(callback_to_interupt)

    def on_interruption(self):
        """Remove all queued events whose callback matches a registered one.

        Iterates over ``env.queue`` and removes entries whose ``func_ptr`` is
        in ``callbacks_to_interrupt``. Does nothing for callbacks that are not
        currently scheduled in the queue.
        """
        for c in self.callbacks_to_interrupt:
            for e in list(self.env.queue):  # iterate over a snapshot to allow removal
                if e.func_ptr == c:
                    self.env.queue.remove(e)


# URL: https://gitlab.com/team-simpy/simpy/-/blob/master/src/simpy/resources/container.py?ref_type=heads#L55
class Container:
    """Simulated storage container for continuous quantities.

    This resource models a container with a finite (or infinite) capacity
    that holds a certain *level* of a continuous quantity (e.g., liters of
    water, units of material). Producers can **put** amounts into the container
    and consumers can **get** amounts from it.

    If a request cannot be immediately satisfied (e.g., a put would overflow,
    or a get would underflow), the request is queued until it becomes possible.

    .. note::
       This is similar to :class:`simpy.resources.container.Container` in SimPy.
    """

    def __init__(
        self, env: Environment, capacity: float = float("inf"), initial: float = 0.0
    ):
        """Initialize the container.

        :param env: The simulation environment.
        :type env: Environment
        :param capacity: Maximum amount that can be stored (``float('inf')`` for unlimited).
        :type capacity: float
        :param initial: Initial level of stored quantity.
        :type initial: float
        """
        self.env = env
        self.capacity = capacity
        self.level = initial
        self.put_waiters = []  # [(amount, callback)]
        self.get_waiters = []  # [(amount, callback)]

    def on_initialize(self, env):
        """Attach or reattach a simulation environment.

        :param env: The simulation environment.
        :type env: Environment
        """
        self.env = env

    def put(self, amount: float, callback: Callable = None):
        """Attempt to put an amount into the container.

        If there is enough remaining capacity, the amount is added immediately
        and the optional callback is invoked. If the put cannot be satisfied
        (because it would exceed capacity), the request is queued in
        ``put_waiters`` for later execution.

        After a successful put, this method tries to release any waiting
        getters that may now be satisfied.

        :param amount: Amount to add.
        :type amount: float
        :param callback: Optional callable to invoke after the put succeeds.
        :type callback: Callable or None
        """
        if self.level + amount <= self.capacity:
            self.level += amount
            if callback:
                callback(amount)
            self._try_release_getters()
        else:
            self.put_waiters.append((amount, callback))

    def get(self, amount: float, callback: Callable):
        """Attempt to get an amount from the container.

        If there is enough quantity available, the amount is removed immediately
        and the callback is invoked. If not enough is available, the request
        is queued in ``get_waiters`` for later execution.

        After a successful get, this method tries to release any waiting
        putters that may now be satisfied.

        :param amount: Amount to remove.
        :type amount: float
        :param callback: Callable to invoke after the get succeeds.
        :type callback: Callable
        """
        if self.level >= amount:
            self.level -= amount
            callback(amount)
            self._try_release_putters()
        else:
            self.get_waiters.append((amount, callback))

    def _try_release_getters(self):
        """Try to satisfy waiting get requests.

        Iterates over ``get_waiters`` and executes any requests that can be
        fulfilled with the current level. Removes satisfied requests from
        the waiting list.
        """
        ready = []
        for amount, callback in list(self.get_waiters):
            if self.level >= amount:
                self.level -= amount
                ready.append((amount, callback))
                self.get_waiters.remove((amount, callback))
        for amount, callback in ready:
            callback(amount)

    def _try_release_putters(self):
        """Try to satisfy waiting put requests.

        Iterates over ``put_waiters`` and executes any requests that can be
        fulfilled without exceeding capacity. Removes satisfied requests from
        the waiting list.
        """
        ready = []
        for amount, callback in list(self.put_waiters):
            if self.level + amount <= self.capacity:
                self.level += amount
                ready.append((amount, callback))
                self.put_waiters.remove((amount, callback))
        for amount, callback in ready:
            if callback:
                callback(amount)


class PriorityResource:
    """Resource with capacity and priority-based access.

    This resource grants access to at most ``capacity`` users at a time.
    Requests beyond the current capacity are queued in a priority queue
    (lowest numerical priority value is served first).

    Within the same priority, requests are served in the order they arrived
    (FIFO) using a tie-breaker counter.

    .. note::
       This is conceptually similar to :class:`simpy.resources.resource.PriorityResource`
       in SimPy.
    """

    def __init__(self, env: "Environment", capacity: int = 1):
        """Initialize the priority resource.

        :param env: The simulation environment.
        :type env: Environment
        :param capacity: Maximum number of concurrent users.
        :type capacity: int
        """
        self.env = env
        self.capacity = capacity
        self.users = 0
        self.queue = []  # heapq: (priority, order, callback, args)
        self._counter = 0  # tie-breaker for FIFO in same priority

    def on_initialize(self, env):
        """Attach or reattach a simulation environment.

        :param env: The simulation environment.
        :type env: Environment
        """
        self.env = env

    def on_request(self, callback: callable, args: tuple = tuple(), priority: int = 0):
        """Request access to the resource.

        If the resource has available capacity, the request is granted
        immediately and the callback is executed. Otherwise, the request
        is queued with the given priority.

        :param callback: Function to call when the resource becomes available.
        :type callback: callable
        :param args: Positional arguments for the callback.
        :type args: tuple
        :param priority: Request priority (lower values served first).
        :type priority: int
        """
        if self.users < self.capacity:
            self.users += 1
            callback(*args)
        else:
            heappush(self.queue, (priority, self._counter, callback, args))
            self._counter += 1

    def on_release(self):
        """Release the resource and serve the next queued request.

        If there are waiting requests, the highest-priority one is granted
        access immediately. Within the same priority, requests are served
        in FIFO order.
        """
        self.users -= 1
        while self.queue and self.users < self.capacity:
            priority, _, callback, args = heappop(self.queue)
            self.users += 1
            callback(*args)


class PreemptiveResource:
    """Resource with capacity, priority scheduling, and preemption.

    This resource grants access to at most ``capacity`` users at a time.
    Requests beyond the current capacity are queued in a priority queue
    (lowest numerical priority value is served first). Within the same priority,
    requests are served in the order they arrived (FIFO).

    Unlike :class:`PriorityResource`, this resource supports **preemption**:
    a higher-priority request may force an active user to release the resource
    immediately, depending on the preemption rules.

    .. note::
       This is conceptually similar to :class:`simpy.resources.resource.PreemptiveResource`
       in SimPy.
    """

    def __init__(self, env, capacity=1):
        """Initialize the preemptive resource.

        :param env: The simulation environment.
        :type env: Environment
        :param capacity: Maximum number of concurrent users.
        :type capacity: int
        """
        self.env = env
        self.capacity = capacity
        #: List of active users.
        #: Each tuple: (priority, order, name, preemptable, on_preempted_callback)
        self.users = []
        #: Waiting requests in the priority queue.
        #: Each tuple: (priority, order, preemptable, name, callback, args, on_preempted_callback)
        self.queue = []
        self._counter = 0  # tie-breaker for FIFO ordering

    def on_initialize(self, env):
        """Attach or reattach a simulation environment.

        :param env: The simulation environment.
        :type env: Environment
        """
        self.env = env

    def on_request(
        self, name, callback, args=(), priority=0, preempt=True, on_preempted=None
    ):
        """Request access to the resource.

        If the resource has capacity, the request is granted immediately.
        Otherwise, if ``preempt`` is ``True`` and there is an active user
        with lower priority, that user may be preempted. If no preemption
        occurs, the request is queued.

        :param name: Identifier for the requesting user.
        :type name: str
        :param callback: Function to call when the resource is granted.
        :type callback: callable
        :param args: Positional arguments for the callback.
        :type args: tuple
        :param priority: Request priority (lower values served first).
        :type priority: int
        :param preempt: Whether this request can preempt an active user.
        :type preempt: bool
        :param on_preempted: Callback executed if this request is later preempted.
        :type on_preempted: callable | None
        """
        if len(self.users) < self.capacity:
            self._grant(name, priority, preempt, callback, args, on_preempted)
        else:
            if preempt and self._can_preempt(priority):
                self._do_preempt(name, priority, preempt, callback, args, on_preempted)
            else:
                heappush(
                    self.queue,
                    (
                        priority,
                        self._counter,
                        preempt,
                        name,
                        callback,
                        args,
                        on_preempted,
                    ),
                )
                self._counter += 1

    def _grant(self, name, priority, preempt, callback, args, on_preempted):
        """Grant the resource to a user immediately.

        :param name: User identifier.
        :type name: str
        :param priority: Request priority.
        :type priority: int
        :param preempt: Whether this user can be preempted by others.
        :type preempt: bool
        :param callback: Function to execute upon grant.
        :type callback: callable
        :param args: Arguments for the callback.
        :type args: tuple
        :param on_preempted: Callback if the user is later preempted.
        :type on_preempted: callable | None
        """
        self.users.append((priority, self._counter, name, preempt, on_preempted))
        self._counter += 1
        callback(*args)

    def _can_preempt(self, priority):
        """Determine if an active user can be preempted.

        Preemption is possible only if:
        - No non-preemptable request is already queued.
        - There exists at least one active user with **worse** priority.

        :param priority: Priority of the incoming request.
        :type priority: int
        :return: ``True`` if preemption can occur, otherwise ``False``.
        :rtype: bool
        """
        if any(not q[2] for q in self.queue):  # q[2] = preempt flag
            return False

        worst_user = max(self.users, key=lambda u: (u[0], u[1]))
        return priority < worst_user[0] and worst_user[3]  # user[3] = preemptable

    def _do_preempt(self, name, priority, preempt, callback, args, on_preempted):
        """Preempt the worst active user and grant resource to new request.

        :param name: New user's identifier.
        :type name: str
        :param priority: Priority of new request.
        :type priority: int
        :param preempt: Whether new request is itself preemptable.
        :type preempt: bool
        :param callback: Function to call upon grant.
        :type callback: callable
        :param args: Arguments for callback.
        :type args: tuple
        :param on_preempted: Callback if this new request is preempted later.
        :type on_preempted: callable | None
        """

        def f(u):
            return (u[0], u[1])

        worst_user = max(self.users, key=f)
        self.users.remove(worst_user)
        _, _, preempted_name, _, preempted_cb = worst_user

        if preempted_cb:
            preempted_cb()

        self._grant(name, priority, preempt, callback, args, on_preempted)

    def on_release(self, name):
        """Release resource held by a given user and assign to next queued request.

        :param name: Identifier of the user releasing the resource.
        :type name: str
        """
        self.users = [u for u in self.users if u[2] != name]

        while self.queue and len(self.users) < self.capacity:
            priority, _, preempt, q_name, cb, args, preempted_cb = heappop(self.queue)
            self._grant(q_name, priority, preempt, cb, args, preempted_cb)


class FilterStore:
    """Store for items retrievable by a filter function.

    Similar to SimPy's :class:`simpy.resources.store.FilterStore`, this store
    holds items up to a maximum capacity. Consumers request items by providing
    a *filter function* which decides whether an available item matches.

    If no matching item is available, the request is queued until a future
    ``put()`` adds an item that passes the filter.

    :param env: Simulation environment.
    :type env: Environment
    :param capacity: Maximum number of items in the store. Defaults to infinity.
    :type capacity: float
    """

    def __init__(self, env, capacity=float("inf")):
        """Initialize the filter store.

        :param env: Simulation environment.
        :type env: Environment
        :param capacity: Maximum store size, or ``float("inf")`` for unbounded.
        :type capacity: float
        """
        self.env = env
        self.capacity = capacity
        #: Items currently in the store.
        self.items = []
        #: Queue of pending puts when the store is full.
        #: Each entry is ``(item, callback)``.
        self.put_queue = deque()
        #: Queue of pending gets with filters when no matching item is available.
        #: Each entry is ``(filter_fn, callback)``.
        self.get_queue = deque()

    def on_initialize(self, env):
        """Attach or reattach a simulation environment.

        :param env: Simulation environment.
        :type env: Environment
        """
        self.env = env

    def put(self, item, callback=None):
        """Insert an item into the store.

        If the store has free capacity, the item is stored immediately and
        any waiting getter whose filter matches it is served. Otherwise, the
        put request is queued until space becomes available.

        :param item: The item to store.
        :type item: Any
        :param callback: Optional function to call when the put succeeds.
        :type callback: callable | None
        """
        if len(self.items) < self.capacity:
            self.items.append(item)
            if callback:
                callback(item)
            self._try_release_getters()
        else:
            self.put_queue.append((item, callback))

    def get(self, filter_fn, callback):
        """Retrieve an item matching a filter function.

        If an item in the store satisfies ``filter_fn(item) == True``, it is
        removed and returned immediately to the consumer via the callback.
        Otherwise, the get request is queued until such an item is put.

        :param filter_fn: A callable that takes an item and returns ``True`` if
                          it should be retrieved.
        :type filter_fn: callable
        :param callback: Function to call with the retrieved item.
        :type callback: callable
        """
        for idx, item in enumerate(self.items):
            if filter_fn(item):
                chosen = self.items.pop(idx)
                callback(chosen)
                self._try_release_putters()
                return

        self.get_queue.append((filter_fn, callback))

    def _try_release_getters(self):
        """Serve any waiting gets whose filter matches an available item."""
        ready = []
        for filter_fn, callback in list(self.get_queue):
            for idx, item in enumerate(self.items):
                if filter_fn(item):
                    chosen = self.items.pop(idx)
                    ready.append((callback, chosen))
                    self.get_queue.remove((filter_fn, callback))
                    break

        for callback, chosen in ready:
            callback(chosen)
            self._try_release_putters()

    def _try_release_putters(self):
        """Serve any queued puts if store space is available."""
        while self.put_queue and len(self.items) < self.capacity:
            item, callback = self.put_queue.popleft()
            self.items.append(item)
            if callback:
                callback(item)
            self._try_release_getters()


class PriorityItem:
    """Wrapper for items stored with an associated priority.

    Used by :class:`PriorityStore` to order items in a heap-based priority queue.
    Lower ``priority`` values indicate higher priority.

    :param priority: The item's priority. Lower values are retrieved first.
    :type priority: int | float
    :param item: The actual item to store.
    :type item: Any
    """

    def __init__(self, priority, item):
        """Initialize a priority item.

        :param priority: The item's priority. Lower values are retrieved first.
        :type priority: int | float
        :param item: The actual object or data to wrap.
        :type item: Any
        """
        self.priority = priority
        self.item = item

    def __lt__(self, other):
        """Compare two priority items for ordering.

        Returns ``True`` if this item's priority is less than the other's.

        :param other: Another :class:`PriorityItem` instance.
        :type other: PriorityItem
        :return: ``True`` if this item has higher priority (lower value).
        :rtype: bool
        """
        return self.priority < other.priority


class PriorityItem:
    """Wrapper for items stored with an associated priority.

    Used by :class:`PriorityStore` to order items in a heap-based priority queue.
    Lower ``priority`` values indicate higher priority.

    :param priority: The item's priority. Lower values are retrieved first.
    :type priority: int | float
    :param item: The actual item to store.
    :type item: Any
    """

    def __init__(self, priority, item):
        """Initialize a priority item.

        :param priority: The item's priority. Lower values are retrieved first.
        :type priority: int | float
        :param item: The actual object or data to wrap.
        :type item: Any
        """
        self.priority = priority
        self.item = item

    def __lt__(self, other):
        """Compare two priority items for ordering.

        Returns ``True`` if this item's priority is less than the other's.

        :param other: Another :class:`PriorityItem` instance.
        :type other: PriorityItem
        :return: ``True`` if this item has higher priority (lower value).
        :rtype: bool
        """
        return self.priority < other.priority


class PriorityStore:
    """Store that serves items by priority using a heap.

    Items are kept in a min-heap so that the **lowest** priority value is
    retrieved first. When the store is full, puts are queued; when it is
    empty, gets are queued. Each successful put/get attempts to unblock the
    opposite side.

    .. note::
       Items must be **comparable** for heap ordering. You can store plain
       numbers/tuples, or wrap arbitrary objects in :class:`PriorityItem`.
       (``PriorityItem`` implements ``__lt__`` on its ``priority``.)

    :param env: Simulation environment.
    :type env: Environment
    :param capacity: Maximum number of items in the store (``float('inf')`` for unbounded).
    :type capacity: float
    """

    def __init__(self, env, capacity=float("inf")):
        """Initialize the priority store.

        :param env: Simulation environment.
        :type env: Environment
        :param capacity: Store capacity, or ``float("inf")`` for unbounded.
        :type capacity: float
        """
        self.env = env
        self.capacity = capacity
        #: Internal heap that maintains priority order.
        self._heap = []  # expects items with a valid __lt__
        #: Waiting puts when the store is full: list of ``(item, callback)``.
        self.put_queue = []
        #: Waiting gets when the store is empty: list of callbacks.
        self.get_queue = []

    def on_initialize(self, env):
        """Attach or reattach a simulation environment.

        :param env: Simulation environment.
        :type env: Environment
        """
        self.env = env

    def put(self, item, callback=None):
        """Put an item in the store or wait if full.

        If capacity allows, the item is pushed on the heap and the optional
        callback is invoked. Afterwards, any waiting getter is served (highest
        priority item first). If the store is full, the put is queued.

        :param item: The item to store (must be heap-orderable).
        :type item: Any
        :param callback: Optional function called after the put succeeds.
        :type callback: callable | None
        """
        if len(self._heap) < self.capacity:
            heappush(self._heap, item)
            if callback:
                callback(item)
            self._try_release_getters()
        else:
            self.put_queue.append((item, callback))

    def get(self, callback):
        """Get the highest-priority item or wait if empty.

        If the store is non-empty, pops the minimal item from the heap and
        invokes the callback. Otherwise, queues the callback until an item
        becomes available.

        :param callback: Function to call with the retrieved item.
        :type callback: callable
        """
        if self._heap:
            item = heappop(self._heap)
            callback(item)
            self._try_release_putters()
        else:
            self.get_queue.append(callback)

    def _try_release_getters(self):
        """Serve waiting getters while items are available."""
        while self._heap and self.get_queue:
            callback = self.get_queue.pop(0)  # FIFO for waiting getters
            item = heappop(self._heap)
            callback(item)
            self._try_release_putters()

    def _try_release_putters(self):
        """Serve waiting puts while capacity is available."""
        while self.put_queue and len(self._heap) < self.capacity:
            item, callback = self.put_queue.pop(0)  # FIFO for waiting putters
            heappush(self._heap, item)
            if callback:
                callback(item)
            self._try_release_getters()
