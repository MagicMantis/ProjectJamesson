import random
import time

MutateConnectionsChance = 0.25
PerturbChance = 0.90
CrossoverChance = 0.75
LinkMutationChance = 2.0
NodeMutationChance = 0.50
BiasMutationChance = 0.40
EnableMutationChance = 0.2
DisableMutationChance = 0.4
StepSize = 0.1


class Mutator:
    def __init__(self):
        self.mutate_connections_chance = MutateConnectionsChance
        self.link_mutation_chance = LinkMutationChance
        self.bias_mutation_chance = BiasMutationChance
        self.node_mutation_chance = NodeMutationChance
        self.enable_chance = EnableMutationChance
        self.disable_chance = DisableMutationChance
        self.step_size = StepSize
        random.seed(time.time())

    @staticmethod
    def random(x):
        random.randint(x)