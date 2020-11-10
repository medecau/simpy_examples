from itertools import count

import simpy
from simpy.resources.resource import Resource


def task_generator(env, supervisor):
    for num in count():
        task = dict(id=num, done=False)
        env.process(supervisor.handle(task))

        yield env.timeout(10)


class Alice:
    def __init__(self, env, colleague):
        self.env = env
        self.colleague = colleague
        self.attention = Resource(env, capacity=1)

    def handle(self, task):
        with self.attention.request() as focus:
            yield focus
            print(self.env.now, "handling", task)
            yield self.env.timeout(1)
            task["signoff"] = self.signoff

            self.env.process(self.colleague.work(task))

    def signoff(self, task):
        with self.attention.request() as focus:
            yield focus
            print(self.env.now, "signing off", task)
            yield self.env.timeout(1)


class Bob:
    def __init__(self, env):
        self.env = env
        self.attention = Resource(env, capacity=1)

    def work(self, task):
        signoff = task["signoff"]
        del task["signoff"]

        with self.attention.request() as focus:
            yield focus
            print(self.env.now, "working", task)
            yield self.env.timeout(5)
            task["done"] = True

            self.env.process(signoff(task))


env = simpy.Environment()

bob = Bob(env)
alice = Alice(env, bob)
env.process(task_generator(env, alice))

env.run(until=20)
