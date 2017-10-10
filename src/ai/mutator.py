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

	def copy(self):

		new_mutator = Mutator()
		new_mutator.mutate_connections_chance = self.mutate_connections_chance
		new_mutator.link_mutation_chance = self.link_mutation_chance
		new_mutator.bias_mutation_chance = self.bias_mutation_chance
		new_mutator.node_mutation_chance = self.node_mutation_chance
		new_mutator.enable_chance = self.enable_chance
		new_mutator.disable_chance = self.disable_chance

		return new_mutator

    @staticmethod
    def random(x):
        random.randint(x)
