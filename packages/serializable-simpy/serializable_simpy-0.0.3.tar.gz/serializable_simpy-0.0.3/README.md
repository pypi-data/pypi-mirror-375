# SerializableSimpy 

SerializableSimpy Project aims to extends the capabilities of traditional SimPy by introducing *serializability* and *parallelism*. 

Standard SimPy uses Python's `yield` keyword to implement events, which prevents object serialization and limits scalability. SerializableSimpy provides a "**yield-less**" implementation of DES logic, enabling:
* **Simulation state checkpointing**: pause/resume/rollback 
* **Parallelism**: Multiprocessing and MPI-based

**Full API Documentation**: [https://serializablesimpy.readthedocs.io](https://serializablesimpy.readthedocs.io)

## Why a new Discrete Event Simulator?

We designed SerializableSimpy around SimPy’s proven and intuitive API, which has a strong and active user base. However, SimPy’s reliance on generator-based coroutines limits its applicability in modern simulation workflows.

While inspired by SimPy, SerializableSimpy is **not a drop-in replacement** and does not implement all of SimPy’s API.


## Installation & Dependencies

SerializableSimpy can be installed as a standalone Python module.

```
pip install serializable-simpy
```

To enable distributed execution via MPI, install:
```
pip install mpi4py
```

No other dependency is needed.

## API difference with Simpy

This code pattern with Simpy
```python
do_something_before(a,b,c)
yield env.timeout(10)
do_something_after(d,e,f)
```

In SerializableSimpy becomes:
```python
do_something_before(a,b,c)
env.timeout(10, do_something_after, (d,e,f))
```

You can find many other Simpy examples converted in SerializableSimy here: [URL here]

## Checkpointing Example

Here's an example to demonstrate how to use the objects

```python
from SerializableSimpy.core import Environment, Process


class Clock(Process):
    def __init__(self, env, name, tick):
        self.name = name
        self.env = env
        self.tick = tick

    def on_initialize(self, env):
        self.env = env
        self.on_tick()

    def on_tick(self):
        print(self.name, self.env.now)
        self.env.timeout(self.tick, self.on_tick,
                         ())  # `yield env.timeout(tick)` becomes `env.timeout(tick, on_tick, ())`


env = Environment()
env.process(Clock(env, 'fast', 0.5))
env.process(Clock(env, 'slow', 1))

env.run(until=2)

# Saving/Restoring with pickle is possible
import pickle

with open("checkpoint.pkl", "wb") as f:
    pickle.dump(env, f)
del env
print("Restoring")
with open("checkpoint.pkl", "rb") as f:
    env = pickle.load(f)

env.run(until=4)
```

Prints:
```commandline
fast 0
slow 0
fast 0.5
slow 1
fast 1.0
fast 1.5
fast 2.0
slow 2
fast 2.5
slow 3
fast 3.0
fast 3.5
```


Inspired from the official Simpy code: https://gitlab.com/team-simpy/simpy.
Simpy in its current shape cannot serialize objects. Let's take the simplest example of the homepage.

```python
import simpy
def clock(env, name, tick):
    while True:
        print(name, env.now)
        yield env.timeout(tick)

env = simpy.Environment()
env.process(clock(env, 'fast', 0.5))
env.process(clock(env, 'slow', 1))
env.run(until=2)

import pickle
with open("checkpoint.pkl","wb") as f:
    pickle.dump(env, f) # ❌ TypeError: cannot pickle 'generator' object
```



## Using Parallel Environments

SerializableSimpy supports multiple runtime backends. Choose based on your use case:
```python
# Sequential environemnt:
from SerializableSimpy.core import Environment 
env=Environment(initial_time=0.) 
env.run(until=1.)

# MPI (Message Passing Interface) environemnt :
from SerializableSimpy.MPI_core import MPIGlobalEnv
env=MPIGlobalEnv(initial_time=0.) 
env.run(until=1., delta=0.1)

# Multiprocessing environemnt (Shared memory):
from SerializableSimpy.MP_core import MPGlobalEnv
env=MPGlobalEnv(initial_time=0.) 
env.run(until=1., delta=0.1)
```

Note: Parallel simulation requires setting a delta time step to synchronize local environments. A small delta may improve accuracy at the cost of communication/synchronization overhead.

## Parallel Simulation Benchmark

In the folder `./application/tuto/parallelism/`, you'll find three implementations of a producer-consumer model—a common DES pattern in manufacturing and logistics.

**Execution Comparison**

| Parallel Method   | User Code Lines | Time (sec.) | Consumed Items  | Multi-Machine Compatible |
|-------------------|-----------------|----------------------|------------------------------|--------------------------|
| Sequential        | 54              | 40.04                | 20                           | ❌                       |
| Multiprocessing   | 63              | 20.05                | 19                           | ❌                       |
| MPI               | 67              | 20.02                | 18                           | ✅                      |

**Observations**:

* MPI introduces lower overhead than multiprocessing for producer-consumer setups. However, when delta becomes too small, synchronization overhead increases significantly hurting MPI performance more than multiprocessing.
* Multiprocessing may yield final state closer to sequential. It is because they are not only synchronized every delta, but exchange through a shared memory during simulation. In the wost case, Multiprocessing processes are synchronized every delta. In the best case, computation time matches simulation time.


## Running on MeluXina Supercomputer

See [MeluXinaREADME.md](MeluXinaREADME.md) for a detailed walkthrough on deploying SerializableSimpy on the MeluXina EuroHPC system.

## Acknowledgment

SerializeSimpy contributor(s) would like to express their gratitude for the fruitful discussions and the collaboration that made this project possible between Goodyear company and the University of Luxembourg.

Supported by the Luxembourg National Research Fund 17941664

Supported by the Ministry of Economy (MECO) 17941664

## Contact
For any questions or suggestions, please contact <mailto:pierrick.pochelu@gmail.com>.


