import unittest

from SerializableSimpy.core import Environment, Process, Store, Event, Resource


class MyTestCase(unittest.TestCase):

    def test_process(self):
        out = set([])

        class Clock(Process):
            def on_initialize(self, env):
                self.env = env
                self.on_yield()

            def on_yield(self):
                out.add("It is " + str(int(self.env.get_now())))
                self.env.timeout(
                    1, self.on_yield, ()
                )  # `tuple()` means no argument for `on_yield()`

        env = Environment()
        env.process(Clock())
        env.run(until=3)

        expected_set = set(["It is 0", "It is 1", "It is 2"])
        self.assertTrue(out == expected_set)

    def test_event(self):
        out = set([])

        class Machine(Process):
            def __init__(self, name):
                self.name = name

            def on_initialize(self, env):
                self.env = env
                self.state = "IDLE"
                self.on_yield()

            def on_yield(self):
                out.add(
                    f"{self.name} time: {int(self.env.get_now())} state: {self.state}"
                )
                self.env.timeout(
                    1, self.on_yield, tuple()
                )  # `tuple()` means no argument for `on_yield()`

            def on_wake_up(self):
                self.state = "WORKING"

        env = Environment()
        alarm = Event(env)
        env.process(alarm)

        for i in range(3):
            m = Machine("m" + str(i))
            alarm.add_callback(m.on_wake_up)
            env.process(m)

        env.run(until=2)
        alarm.on_trigger()
        env.run(until=4)

        s = set([])
        s.add("m0 time: 0 state: IDLE")
        s.add("m1 time: 0 state: IDLE")
        s.add("m2 time: 0 state: IDLE")
        s.add("m0 time: 1 state: IDLE")
        s.add("m1 time: 1 state: IDLE")
        s.add("m2 time: 1 state: IDLE")
        s.add("m1 time: 2 state: WORKING")
        s.add("m2 time: 2 state: WORKING")
        s.add("m0 time: 2 state: WORKING")
        s.add("m1 time: 3 state: WORKING")
        s.add("m2 time: 3 state: WORKING")
        s.add("m0 time: 3 state: WORKING")

        self.assertTrue(s == out)

    def test_event_fail(self):
        """Test that Event.fail() sets _ok=False and triggers callbacks."""
        env = Environment()
        ev = Event(env)

        results = []

        def cb():
            results.append("failed")

        ev.add_callback(cb)
        ev.fail()  # Should call cb and set _ok=False

        self.assertFalse(ev._ok)
        self.assertTrue("failed" in results)

    def test_event_add_callback_immediate(self):
        """Test add_callback calls callback immediately when _ok=True."""
        env = Environment()
        ev = Event(env)
        ev._ok = True  # Simulate event already triggered

        results = []

        def cb(val):
            results.append(val)

        # Because _ok=True, callback should be called immediately
        ev.add_callback(cb, args=("immediate",))
        self.assertTrue("immediate" in results)

    def test_resource(self):
        out = set([])

        class MyProcess(Process):
            def __init__(self, env: Environment, resource: Resource):
                self.env = env
                self.resource = resource

            def on_initialize(self, env: Environment):
                self.env = env
                self.run()

            def run(self):
                out.add(
                    f"Process started at time {self.env.get_now()}. Request resource"
                )
                self.resource.on_request(self.use_resource)

            def use_resource(self):
                out.add(
                    f"Resource acquired at time {self.env.get_now()}. Released in 5min."
                )
                self.env.timeout(
                    5, self.resource.on_release, tuple([self.use_resource, ()])
                )

        env = Environment()
        r = Resource(env, capacity=2)
        env.process(r)

        for i in range(5):
            p = MyProcess(env, r)
            env.process(p)

        env.run(until=20)

        s = set([])
        s.add("Process started at time 0. Request resource")
        s.add("Resource acquired at time 0. Released in 5min.")
        s.add("Process started at time 0. Request resource")
        s.add("Resource acquired at time 0. Released in 5min.")
        s.add("Process started at time 0. Request resource")
        s.add("Process started at time 0. Request resource")
        s.add("Process started at time 0. Request resource")
        s.add("Resource acquired at time 5. Released in 5min.")
        s.add("Resource acquired at time 5. Released in 5min.")
        s.add("Resource acquired at time 10. Released in 5min.")

        self.assertTrue(s == out)

    def test_store(self):
        # s=set([])
        class Producer:
            def __init__(self, store: Store, cycle_time: float):
                self.env = None
                self.store = store
                self.item_id = 0
                self.cycle_time = cycle_time

            def on_initialize(self, env):
                self.env = env
                self.env.timeout(
                    self.cycle_time, self.on_yield, tuple()
                )  # launch the producing loop

            def on_yield(self):
                self.store.on_put(f"item{self.item_id}")
                self.env.timeout(
                    self.cycle_time, self.on_yield, tuple()
                )  # loop on itself every 5
                self.item_id += 1

        class Consumer(Process):
            def __init__(self, store: Store, cycle_time: float):
                self.env = None
                self.store = store
                self.cycle_time = cycle_time

            def on_initialize(self, env):
                self.env = env
                self.store.on_get(
                    self.on_yield
                )  # the consumer is immediately ready to receive a new item

            def on_yield(self, msg):
                # s.add(f'Consumer receives {msg} at {self.env.now}')
                # self.store.on_get(self.on_yield)
                self.env.timeout(
                    self.cycle_time, self.store.on_get, tuple([self.on_yield])
                )

        env = Environment()
        store = Store(capacity=2)
        env.process(Producer(store, cycle_time=1))
        env.process(Consumer(store, cycle_time=2))  # consumer is slower
        env.run(until=10)

        self.assertTrue(len(store.items) == 2)

    def test_conditional_events(self):
        from SerializableSimpy.core import Environment, Event

        expected_logs = []
        logs = []

        env = Environment()

        def cond1_callback():
            logs.append(f"One driver is arrived at {env.get_now()}")

        def cond2_callback():
            logs.append(f"The race is finished at {env.get_now()}")

        def cond3_callback():
            logs.append(
                f"The expression `(ev1 & ev4) | ev3` is true at {env.get_now()}"
            )

        ev1 = Event(env)
        ev2 = Event(env)
        ev3 = Event(env)

        cond1 = ev1 | ev2 | ev3
        cond2 = ev1 & ev2 & ev3
        cond3 = (ev1 & ev2) | ev3

        cond1.add_callback(cond1_callback)
        cond2.add_callback(cond2_callback)
        cond3.add_callback(cond3_callback)

        env.timeout(1, ev1.on_trigger, tuple())
        env.timeout(2, ev2.on_trigger, tuple())
        env.timeout(3, ev3.on_trigger, tuple())

        env.run(10)

        for out, expected in zip(logs, expected_logs):
            self.assertTrue(out == expected)

    def test_conditional_events_edge_cases(self):
        from SerializableSimpy.core import Condition

        env = Environment()
        c = Condition(env, Condition.all_events, [])
        env.timeout(1, c, ())
        self.assertTrue(c._ok == True)

        from SerializableSimpy.core import Condition

        env1 = Environment()
        env2 = Environment()
        ev1 = Event(env1)
        ev2 = Event(env2)

        with self.assertRaises(ValueError):
            c = Condition(env1, Condition.any_events, [ev1, ev2])

    def test_interruption(self):
        from SerializableSimpy.core import Environment, Process, Interruption

        expected_count = 6

        class Clock(Process):
            def __init__(self, env):
                self.env = env
                self.count = 0

            def on_initialize(self, env):
                self.env = env

                # schedule an interuption after 5.5
                self._interuption = Interruption(env)
                self._interuption.add_interruption(self.on_yield)
                self.env.timeout(5.5, self._interuption.on_interruption, tuple())

                self.on_yield()

            def on_yield(self):
                self.count += 1
                self.env.timeout(
                    1, self.on_yield, tuple()
                )  # `tuple()` means no argument for `on_yield()`

        env = Environment()
        clock = Clock(env)
        env.process(clock)
        env.run(until=10)

        self.assertTrue(clock.count == expected_count)

    def test_container(self):
        from SerializableSimpy.core import Environment, Container

        logs = []
        log_expected = [
            "[1] Consumed 2 units (level=3)",
            "[3] Producer added 2 units (level=5)",
            "[9] Producer added 4 units (level=9)",
            "[9] Consumed 8 units (level=1)",
            "pause/resume",
            "[15] Producer added 5 units (level=6)",
            "[15] Consumed 2 units (level=0)",
            "[15] Consumed 4 units (level=0)",
        ]

        env = Environment()
        container = Container(env, capacity=10, initial=5)

        def consumer(amount):
            logs.append(
                f"[{env.get_now()}] Consumed {amount} units (level={container.level})"
            )

        def producer_done(amount):
            logs.append(
                f"[{env.get_now()}] Producer added {amount} units (level={container.level})"
            )

        self.assertTrue(container.level == 5)

        # scenario A: produce/consume

        # at 1 -> -2 (before: 5, after 3)
        env.timeout(1, container.get, (2, consumer))

        # at 3 -> +2 (before: 3, after 5)
        env.timeout(3, container.put, (2, producer_done))

        # scenario B: consume but not enough for the consumer

        # at 5 -> try to -8 (before: 5, after 5 and 1 consumer waiting)
        env.timeout(5, container.get, (8, consumer))

        # scenario C: at 9 -> +4, wake up the consumer (after: 1)

        env.timeout(9, container.put, (4, producer_done))

        # Lancer la simulation
        env.run(until=10)

        logs.append("pause/resume")
        self.assertTrue(container.level == 1)

        # at 5 -> try to -8 (before: 5, after 5 and 3 consumers waiting)
        env.timeout(1, container.get, (2, consumer))
        env.timeout(1, container.get, (3, consumer))
        env.timeout(1, container.get, (4, consumer))

        env.timeout(
            2, container.get, (5, consumer)
        )  # fifo, so it would not be scheduled

        env.timeout(5, container.put, (5, producer_done))

        env.run(until=20)

        self.assertTrue(container.level == 0)

        self.assertTrue(len(logs) == len(log_expected))
        for out, expected in zip(logs, log_expected):
            self.assertTrue(out == expected)

    def test_container_producers_faster(self):
        from SerializableSimpy.core import Environment, Container

        logs = []
        log_expected = [
            "[1] Producer added 2 units (level=7)",
            "[2] Producer added 2 units (level=9)",
            "[7] Consumed 2 units (level=7)",
            "[7] Producer added 2 units (level=9)",
        ]

        env = Environment()
        container = Container(env, capacity=10, initial=5)

        def consumer(amount):
            logs.append(
                f"[{env.get_now()}] Consumed {amount} units (level={container.level})"
            )

        def producer_done(amount):
            logs.append(
                f"[{env.get_now()}] Producer added {amount} units (level={container.level})"
            )

        for i in range(1, 5):
            env.timeout(i, container.put, (2, producer_done))

        env.timeout(7, container.get, (2, consumer))

        env.run(until=10)

        self.assertTrue(container.level == 9)

        self.assertTrue(len(logs) == len(log_expected))
        for out, expected in zip(logs, log_expected):
            self.assertTrue(out == expected)

    def test_priority_resource(self):
        from SerializableSimpy.core import Environment, PriorityResource

        logs = []
        env = Environment()
        res = PriorityResource(env, capacity=1)

        # Request resources with different priorities
        env.timeout(0, res.on_request, (lambda: logs.append("A got"), (), 0))
        env.timeout(0, res.on_request, (lambda: logs.append("B got"), (), 0))
        env.timeout(0, res.on_request, (lambda: logs.append("C got"), (), -1))
        env.timeout(0, res.on_request, (lambda: logs.append("D got"), (), 1))

        env.run(until=10)

        # First release (C should get because -1 is highest priority)
        res.on_release()
        # Second release (B should get next)
        res.on_release()

        self.assertTrue("A got" in logs)
        self.assertTrue("C got" in logs)
        self.assertTrue("B got" in logs)
        self.assertTrue(len(logs) == 3)

    def test_preemptive_resource(self):
        from SerializableSimpy.core import Environment, PreemptiveResource

        logs = []
        expected_log = ["pA got", "pA preempted", "pC got", "pB got"]

        env = Environment()
        res = PreemptiveResource(env, capacity=1)

        # Requests: C has higher priority and should preempt
        pA = (
            "pA",
            lambda: logs.append("pA got"),
            (),
            0,
            True,
            lambda: logs.append("pA preempted"),
        )
        pB = (
            "pB",
            lambda: logs.append("pB got"),
            (),
            0,
            True,
            lambda: logs.append("pB preempted"),
        )
        pC = (
            "pC",
            lambda: logs.append("pC got"),
            (),
            -1,
            True,
            lambda: logs.append("pC preempted"),
        )

        env.timeout(0, res.on_request, pA)
        env.timeout(0, res.on_request, pB)
        env.timeout(0, res.on_request, pC)

        env.run(until=10)

        env.timeout(5, res.on_release, ("pC",))

        env.run(until=20)

        self.assertTrue(len(logs) == len(expected_log))
        for out, expected in zip(logs, expected_log):
            self.assertTrue(out == expected)

    def test_filter_store(self):
        from SerializableSimpy.core import Environment, FilterStore
        from collections import namedtuple

        logs = []
        expected_log = [
            "user 1 got Machine(memory=2, cpu=1)  at 1",
            "returned Machine(memory=2, cpu=1)  at 1",
            "user 4 got Machine(memory=2, cpu=2)  at 1",
            "user 0 got Machine(memory=2, cpu=3)  at 1",
            "user 2 got Machine(memory=2, cpu=1)  at 1",
            "returned Machine(memory=2, cpu=1) at 2",
            "user 3 got Machine(memory=2, cpu=1)  at 2",
        ]

        env = Environment()

        Machine = namedtuple("Machine", ["memory", "cpu"])
        m1 = Machine(2, 1)
        m2 = Machine(2, 2)
        m3 = Machine(2, 3)

        machine_shop = FilterStore(env, capacity=3)
        machine_shop.items = [m1, m2, m3]

        # Return a machine at time 0
        env.timeout(
            0,
            machine_shop.put,
            (m1, lambda x: logs.append(f"returned {x}  at {env.get_now()}")),
        )

        # 5 users request machines at time 1
        for user_i in range(5):
            env.timeout(
                1,
                machine_shop.get,
                (
                    lambda m: m.memory >= 1,
                    lambda m, ui=user_i: logs.append(
                        f"user {ui} got {m}  at {env.get_now()}"
                    ),
                ),
            )

        # Return a machine at time 2
        env.timeout(
            2,
            machine_shop.put,
            (m1, lambda x: logs.append(f"returned {x} at {env.get_now()}")),
        )

        env.run(until=10)

        self.assertTrue(len(logs) == len(expected_log))
        for out, expected in zip(logs, expected_log):
            self.assertTrue(out == expected)

    def test_priority_store(self):
        from SerializableSimpy.core import Environment, PriorityStore, PriorityItem

        logs = []
        expected_log = [
            "add low",
            "add high",
            "add medium",
            "get high",
            "add urgent",
            "get urgent",
            "get medium",
            "get low",
        ]

        env = Environment()
        store = PriorityStore(env, capacity=3)

        store.put(PriorityItem(5, "low"), lambda x: logs.append(f"add {x.item}"))
        store.put(PriorityItem(1, "high"), lambda x: logs.append(f"add {x.item}"))
        store.put(PriorityItem(3, "medium"), lambda x: logs.append(f"add {x.item}"))

        # cannot be added. Waiting. The priority does not apply right now.
        store.put(PriorityItem(0, "urgent"), lambda x: logs.append(f"add {x.item}"))

        store.get(lambda x: logs.append(f"get {x.item}"))
        store.get(lambda x: logs.append(f"get {x.item}"))
        store.get(lambda x: logs.append(f"get {x.item}"))
        store.get(lambda x: logs.append(f"get {x.item}"))
        store.get(lambda x: logs.append(f"get {x.item}"))  # waiting

        env.run(until=5)

        self.assertTrue(len(logs) == len(expected_log))
        for out, expected in zip(logs, expected_log):
            self.assertTrue(out == expected)

    def test_priority_store_get_before_put(self):
        """Test that PriorityStore._try_release_getters is called when get is waiting before put."""
        from SerializableSimpy.core import Environment, PriorityStore

        env = Environment()
        ps = PriorityStore(env, capacity=1)

        results = []

        # First, request an item (store is empty, should queue the getter)
        ps.get(lambda item: results.append(item))

        # Now, put an item; this should trigger the waiting getter immediately
        ps.put((1, "item1"))  # item is (priority, value)

        self.assertTrue(results == [(1, "item1")])


if __name__ == "__main__":
    unittest.main()
