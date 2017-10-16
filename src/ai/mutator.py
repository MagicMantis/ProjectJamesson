from src.ai.gene import Gene
import random
import time


class Mutator:
    PerturbChance = 0.90
    MutateConnectionsChance = 0.25
    CrossoverChance = 0.75
    LinkMutationChance = 2.0
    NodeMutationChance = 0.50
    BiasMutationChance = 0.40
    EnableMutationChance = 0.2
    DisableMutationChance = 0.4
    StepSize = 0.1

    def __init__(self, genome):
        self.genome = genome
        self.mutate_connections_chance = Mutator.MutateConnectionsChance
        self.link_mutation_chance = Mutator.LinkMutationChance
        self.bias_mutation_chance = Mutator.BiasMutationChance
        self.node_mutation_chance = Mutator.NodeMutationChance
        self.enable_chance = Mutator.EnableMutationChance
        self.disable_chance = Mutator.DisableMutationChance
        self.step_size = Mutator.StepSize
        random.seed(time.time())

    def mutate(self):

        self.rate_mutate()
        if random.random() < self.mutate_connections_chance:
            self.point_mutate()

        # Link mutations
        p = self.link_mutation_chance
        while p > 0:
            if random.random() < p:
                self.link_mutate(False)
            p -= 1

        # Bias link mutations
        p = self.bias_mutation_chance
        while p > 0:
            if random.random() < p:
                self.link_mutate(True)
            p -= 1

        # Bias link mutations
        p = self.node_mutation_chance
        while p > 0:
            if random.random() < p:
                self.node_mutate()
            p -= 1

        # Bias link mutations
        p = self.enable_chance
        while p > 0:
            if random.random() < p:
                self.enable_disable_mutate(True)
            p -= 1

        # Bias link mutations
        p = self.disable_chance
        while p > 0:
            if random.random() < p:
                self.enable_disable_mutate(False)
            p -= 1

    def point_mutate(self):
        for gene in self.genome.genes:
            if random.random() <= .9:
                gene.weight += random.random() * (self.step_size * 2) - self.step_size
            else:
                gene.weight = random.random() * 4 - 2

    def link_mutate(self, force_bias):
        n1 = self.genome.random_neuron(False)
        n2 = self.genome.random_neuron(True)
        if n1 < self.genome.input_size and n2 < self.genome.input_size:
            return

        new_link = Gene()
        new_link.into = n1
        new_link.out = n2
        if force_bias:
            new_link.into = self.genome.input_size - 1

        if self.genome.contains_link(new_link):
            return

        new_link.innovation = Gene.innovate()
        new_link.weight = random.random() * 4 - 2

        self.genome.genes.append(new_link)

    def node_mutate(self):
        # Return if list is empty
        if not self.genome.genes:
            return

        self.genome.max_neuron += 1
        gene = random.choice(self.genome.genes)
        if not gene.is_enabled():
            return

        new_gene1 = gene.copy()
        new_gene1.out = self.genome.max_neuron
        new_gene1.weight = 1.0
        new_gene1.innovation = Gene.innovate()

        new_gene2 = gene.copy()
        new_gene2.into = self.genome.max_neuron
        new_gene2.weight = 1.0
        new_gene2.innovation = Gene.innovate()

        self.genome.genes.append(new_gene1, new_gene2)
        gene.disable()

    def enable_disable_mutate(self, enable):
        candidates = []
        for gene in self.genome.genes:
            if not gene.is_enabled() == enable:
                candidates.append(gene)

        random.choice(candidates).toggle()

    def rate_mutate(self):

        if random.randint(2) == 1:
            self.mutate_connections_chance *= .95
        else:
            self.mutate_connections_chance *= 1.05263

        if random.randint(2) == 1:
            self.link_mutation_chance *= .95
        else:
            self.link_mutation_chance *= 1.05263

        if random.randint(2) == 1:
            self.bias_mutation_chance *= .95
        else:
            self.bias_mutation_chance *= 1.05263

        if random.randint(2) == 1:
            self.node_mutation_chance *= .95
        else:
            self.node_mutation_chance *= 1.05263

        if random.randint(2) == 1:
            self.enable_chance *= .95
        else:
            self.enable_chance *= 1.05263

        if random.randint(2) == 1:
            self.disable_chance *= .95
        else:
            self.disable_chance *= 1.05263

        if random.randint(2) == 1:
            self.step_size *= .95
        else:
            self.step_size *= 1.05263

    def copy(self, genome):
        new_mutator = Mutator(genome)
        new_mutator.mutate_connections_chance = self.mutate_connections_chance
        new_mutator.link_mutation_chance = self.link_mutation_chance
        new_mutator.bias_mutation_chance = self.bias_mutation_chance
        new_mutator.node_mutation_chance = self.node_mutation_chance
        new_mutator.enable_chance = self.enable_chance
        new_mutator.disable_chance = self.disable_chance

        return new_mutator
