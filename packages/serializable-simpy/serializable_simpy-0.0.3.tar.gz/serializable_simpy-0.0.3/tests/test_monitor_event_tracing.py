import os
import unittest
from functools import partial

from SerializableSimpy.core import Environment, Process
from SerializableSimpy.monitor_event_tracing import (
    monitor_list_class,
    monitor_list_func,
    monitor_list_object,
    monitor_dict_class,
    monitor_dict_func,
    monitor_dict_object,
    monitor_file_class,
    monitor_file_func,
    monitor_file_object,
    trace,
)


class Clock(Process):
    def __init__(self, env, name, tick):
        self.name = name
        self.env = env
        self.tick = tick

    def on_initialize(self, env):
        self.env = env
        self.on_tick()

    def on_tick(self):
        self.env.timeout(self.tick, self.on_tick, ())


expected_list = [
    (0.5, 0, "Clock"),
    (1.0, 1, "Clock"),
    (1.0, 2, "Clock"),
    (1.5, 3, "Clock"),
    (2.0, 4, "Clock"),
    (2.0, 5, "Clock"),
    (2.5, 6, "Clock"),
    (3.0, 7, "Clock"),
    (3.0, 8, "Clock"),
    (3.5, 9, "Clock"),
    (4.0, 10, "Clock"),
    (4.0, 11, "Clock"),
    (4.5, 12, "Clock"),
    (5.0, 13, "Clock"),
    (5.0, 14, "Clock"),
]

expected_class = {"Clock": 14}
expected_object = {"fast": 9, "slow": 5}
expected_func = {"Clock.on_tick": 14}


class MyTestCase(unittest.TestCase):
    def test_monitor_list_class(self):
        data = []
        monitor = partial(monitor_list_class, data)
        env = Environment()
        trace(env, monitor)
        env.process(Clock(env, "fast", 0.5))
        env.process(Clock(env, "slow", 1.0))
        env.run(until=5.0)

        for out_tuple, expected_tuple in zip(data, expected_list):
            self.assertTrue(out_tuple == expected_tuple)

    def test_monitor_list_object(self):
        data = []
        monitor = partial(monitor_list_object, data)
        env = Environment()
        trace(env, monitor)
        env.process(Clock(env, "fast", 0.5))
        env.process(Clock(env, "slow", 1.0))
        env.run(until=5.0)

        # Count how many entries per object name
        counts = {}
        for t, eid, obj_name in data:
            counts[obj_name] = counts.get(obj_name, 0) + 1

        self.assertTrue(counts == expected_object)

    def test_monitor_list_func(self):
        data = []
        monitor = partial(monitor_list_func, data)
        env = Environment()
        trace(env, monitor)
        env.process(Clock(env, "fast", 0.5))
        env.process(Clock(env, "slow", 1.0))
        env.run(until=5.0)

        # Check function names
        counts = {}
        for t, eid, func_name in data:
            counts[func_name] = counts.get(func_name, 0) + 1

        self.assertTrue(counts == expected_func)

    def test_monitor_file_class(self):
        path = "unit_test_tracing_class.txt"
        with open(path, "w") as file:
            monitor = partial(monitor_file_class, file)
            env = Environment()
            trace(env, monitor)
            env.process(Clock(env, "fast", 0.5))
            env.process(Clock(env, "slow", 1.0))
            env.run(until=5.0)

        with open(path, "r") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            parts = line.strip().split("\t")
            typed_line = float(parts[0]), int(parts[1]), parts[2]
            self.assertTrue(expected_list[i] == typed_line)
        os.remove(path)

    def test_monitor_file_object(self):
        path = "unit_test_tracing_object.txt"
        with open(path, "w") as file:
            monitor = partial(monitor_file_object, file)
            env = Environment()
            trace(env, monitor)
            env.process(Clock(env, "fast", 0.5))
            env.process(Clock(env, "slow", 1.0))
            env.run(until=5.0)

        # Count objects
        counts = {}
        with open(path, "r") as f:
            for line in f:
                parts = line.strip().split("\t")
                obj_name = parts[2]
                counts[obj_name] = counts.get(obj_name, 0) + 1

        self.assertTrue(counts == expected_object)
        os.remove(path)

    def test_monitor_file_func(self):
        path = "unit_test_tracing_func.txt"
        with open(path, "w") as file:
            monitor = partial(monitor_file_func, file)
            env = Environment()
            trace(env, monitor)
            env.process(Clock(env, "fast", 0.5))
            env.process(Clock(env, "slow", 1.0))
            env.run(until=5.0)

        counts = {}
        with open(path, "r") as f:
            for line in f:
                parts = line.strip().split("\t")
                func_name = parts[2]
                counts[func_name] = counts.get(func_name, 0) + 1

        self.assertTrue(counts == expected_func)
        os.remove(path)

    def test_monitor_dict_class(self):
        data = {}
        monitor = partial(monitor_dict_class, data)
        env = Environment()
        trace(env, monitor)
        env.process(Clock(env, "fast", 0.5))
        env.process(Clock(env, "slow", 1.0))
        env.run(until=5.0)

        self.assertTrue(data == expected_class)

    def test_monitor_dict_object(self):
        data = {}
        monitor = partial(monitor_dict_object, data)
        env = Environment()
        trace(env, monitor)
        env.process(Clock(env, "fast", 0.5))
        env.process(Clock(env, "slow", 1.0))
        env.run(until=5.0)

        self.assertTrue(data == expected_object)

    def test_monitor_dict_func(self):
        data = {}
        monitor = partial(monitor_dict_func, data)
        env = Environment()
        trace(env, monitor)
        env.process(Clock(env, "fast", 0.5))
        env.process(Clock(env, "slow", 1.0))
        env.run(until=5.0)

        self.assertTrue(data == expected_func)


if __name__ == "__main__":
    unittest.main()
