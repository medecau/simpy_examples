from itertools import count

import simpy
from simpy.resources.store import Store


def task_generator(env, supervisor):
    for num in count():
        task = dict(id=num, done=False)
        supervisor.inbox.put(task)

        yield env.timeout(10)


class Alice:
    def __init__(self, env, colleague):
        self.env = env
        self.colleague = colleague
        self.inbox = Store(env)

        env.process(self.run(env))

    def run(self, env):
        while True:
            task = yield self.inbox.get()
            yield from self.handle(task)

    def handle(self, task):
        if not task["done"]:
            print(self.env.now, "handling", task)
            yield self.env.timeout(1)
            task["reply to"] = self
            self.colleague.inbox.put(task)

        else:
            print(self.env.now, "signing off", task)
            yield self.env.timeout(2)


class Bob:
    def __init__(self, env):
        self.env = env
        self.inbox = Store(env)

        env.process(self.run(env))

    def run(self, env):
        while True:
            task = yield self.inbox.get()
            yield from self.handle(task)

    def handle(self, task):
        reply_to = task["reply to"]
        del task["reply to"]

        print(self.env.now, "working", task)
        yield self.env.timeout(5)
        task["done"] = True

        reply_to.inbox.put(task)


env = simpy.Environment()

bob = Bob(env)
alice = Alice(env, bob)
env.process(task_generator(env, alice))

env.run(until=20)
