import math
import random
import time
import configparser

config = configparser.ConfigParser()
config.read('res/config.ini')

class Pool:

    def __init__(self):

        self.species = []
        self.population = config['POPULATION'].getint('size')
        self.generation = 0
        self.innovation = 0
        self.current_species = 1
        self.current_genome = 1
        self.current_frame = 0
        self.max_fitness = 0
        self.max_staleness = config['POPULATION'].getint('max_staleness')

    def basic_generation(self):

        print("Creating first generation...")

        for i in range(self.population):
            genome = Genome()
            genome.max_neuron = Network.InputSize
            genome.mutator.mutate()
            self.add_to_species(genome)

        print("Species count: ", len(self.species))

    def add_to_species(self, new_genome):

        for species in self.species:
            if species.genomes[0].is_same_species(new_genome):
                species.genomes.append(new_genome)
                return

        new_species = Species()
        new_species.genomes.append(new_genome)
        self.species.append(new_species)

    def rank_globally(self):

        ranked = []
        for species in self.species:
            for genome in species.genomes:
                ranked.append(genome)

        ranked.sort(key=lambda x: x.fitness, reverse=True)

        for rank, genome in enumerate(ranked):
            genome.global_rank = rank

    def total_fitness(self):
        return sum(x.average_fitness for x in self.species)

    def cull_species(self, cut_to_one):
        for species in self.species:
            species.genomes.sort(key=lambda x: x.fitness, reverse=True)
            if cut_to_one:
                species.genomes = [species.genomes[0]]
                return
            else:
                species.genomes = species.genomes[0:int(math.ceil(len(species.genomes) / 2))]

    def remove_stale(self):
        survived = []
        for species in self.species:
            species.genomes.sort(key=lambda x: x.fitness, reverse=True)

            if species.genomes[0].fitness > species.top_fitness:
                species.top_fitness = 0
            else:
                species.staleness += 1

            if species.staleness < self.max_staleness or species.top_fitness >= self.max_fitness:
                survived.append(species)

        self.species = survived

    def remove_weak(self):

        survived = []
        total = self.total_fitness()
        for species in self.species:
            breed = math.floor(species.average_fitness / total * self.population)
            if breed >= 1:
                survived.append(species)

        self.species = survived

    def new_generation(self):

        self.cull_species(False)
        for species in self.species:
            species.calculate_average_fitness()
        self.remove_stale()
        self.remove_weak()
        self.rank_globally()

        # Make new children
        total = self.total_fitness()
        children = []
        for species in self.species:
            breed = math.floor(species.average_fitness / total * self.population) - 1
            for _ in range(int(breed)):
                children.append(species.breed_child())

        # Keep only best of each species for new generation
        self.cull_species(True)
        while len(children) + len(self.species) < self.population:
            species = random.choice(self.species)
            children.append(species.breed_child())

        # Add children to population
        for child in children:
            self.add_to_species(child)

        self.generation += 1

        print("Generation ", self.generation, " stats: ")
        print("Species Count: ", len(self.species))
        print("Population: ", sum(len(species.genomes) for species in self.species))
        print("Max fitness: ", self.max_fitness)
        print("Avg fitness: ", sum(species.average_fitness for species in self.species) / len(self.species), "\n")


    def all_genomes(self):
        genome_list = []
        for species in self.species:
            genome_list += species.genomes
        return genome_list

class Species:
    CrossoverChance = config['MUTATION'].getfloat('crossover_chance')

    def __init__(self):
        self.top_fitness = 0
        self.staleness = 0
        self.genomes = []
        self.average_fitness = 0

    def calculate_average_fitness(self):
        self.average_fitness = sum(genome.fitness for genome in self.genomes) / len(self.genomes)
        return self.average_fitness

    def breed_child(self):
        if random.random() < Species.CrossoverChance:
            g1 = random.choice(self.genomes)
            g2 = random.choice(self.genomes)
            child = g1.crossover(g2)
        else:
            g = random.choice(self.genomes)
            child = g.copy()

        child.mutator.mutate()
        return child


class Genome:
    DeltaDisjoint = config['POPULATION'].getfloat('delta_disjoint')
    DeltaWeights = config['POPULATION'].getfloat('delta_weights')
    DeltaThreshold = config['POPULATION'].getfloat('delta_threshhold')

    def __init__(self):

        self.genes = []
        self.fitness = 0
        self.adjustedFitness = 0
        self.input_size = Network.InputSize
        self.output_size = Network.OutputSize
        self.max_neuron = 0
        self.global_rank = 0
        self.network = None
        self.mutator = Mutator(self)

    def is_same_species(self, other):

        dd = Genome.DeltaDisjoint * self.disjoints(other)
        dw = Genome.DeltaWeights * self.weights(other)
        return dd + dw < Genome.DeltaThreshold

    def disjoints(self, other):

        set1 = set(self.genes)
        set2 = set(other.genes)
        if not max(len(set1), len(set2)):
            return 0
        return len(set1 ^ set2) / max(len(set1), len(set2))

    def weights(self, other):

        weight_sum = 0
        coincident = 0
        for gene in self.genes:
            if gene.innovation in other.genes:
                weight_sum += abs(gene.weight - other.genes[gene.innovation].weight)
                coincident += 1

        if coincident == 0:
            return 0
        return weight_sum / coincident

    def generate_network(self):
        self.network = Network(self)

    def crossover(self, other):
        child = Genome()

        innovations_other = {}
        for gene in other.genes:
            innovations_other[gene.innovation] = gene

        for gene in self.genes:
            other_gene = None
            if gene.innovation in innovations_other:
                other_gene = innovations_other[gene.innovation]
            if other_gene and other_gene.enabled and random.randint(0, 1) == 1:
                child.genes.append(other_gene.copy())
            else:
                child.genes.append(gene.copy())

        child.max_neuron = max(self.max_neuron, other.max_neuron)
        child.mutator = self.mutator.copy(self)

        return child

    def random_neuron(self, non_input):

        options = set()

        if not non_input:
            for i in range(self.input_size):
                options.add(i)

        for i in range(Network.MaxNodes, Network.MaxNodes + self.output_size):
            options.add(i)

        for gene in self.genes:
            if not non_input or gene.into > self.input_size:
                options.add(gene.into)
            if not non_input or gene.out > self.input_size:
                options.add(gene.out)

        return random.choice(list(options))

    def contains_link(self, link):

        for gene in self.genes:
            if gene.into == link.into and gene.out == link.out:
                return True

    def display(self):
        print("Genome ")
        for gene in self.genes:
            gene.display()

    def copy(self):

        new_genome = Genome()
        for gene in self.genes:
            new_genome.genes.append(gene.copy())

        new_genome.input_size = self.input_size
        new_genome.output_size = self.output_size
        new_genome.max_neuron = self.max_neuron
        new_genome.mutator = self.mutator.copy(self)

        return new_genome


class Mutator:
    PerturbChance = config['MUTATION'].getfloat('perturb_chance')
    MutateConnectionsChance = config['MUTATION'].getfloat('mutate_connections_chance')
    CrossoverChance = config['MUTATION'].getfloat('crossover_chance')
    LinkMutationChance = config['MUTATION'].getfloat('link_mutation_chance')
    NodeMutationChance = config['MUTATION'].getfloat('node_mutation_chance')
    BiasMutationChance = config['MUTATION'].getfloat('bias_mutation_chance')
    EnableMutationChance = config['MUTATION'].getfloat('enable_mutation_chance')
    DisableMutationChance = config['MUTATION'].getfloat('disable_mutation_chance')
    StepSize = config['MUTATION'].getfloat('step_size')

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
        if n1 == n2 or n2 < self.genome.input_size:
            return
        if n2 < n1:
            n1, n2 = n2, n1

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

        self.genome.genes.append(new_gene1)
        self.genome.genes.append(new_gene2)
        gene.disable()

    def enable_disable_mutate(self, enable):
        candidates = []
        for gene in self.genome.genes:
            if not gene.is_enabled() == enable:
                candidates.append(gene)

        if candidates:
            random.choice(candidates).toggle()

    def rate_mutate(self):

        if random.randint(0, 1) == 1:
            self.mutate_connections_chance *= .95
        else:
            self.mutate_connections_chance *= 1.05263

        if random.randint(0, 1) == 1:
            self.link_mutation_chance *= .95
        else:
            self.link_mutation_chance *= 1.05263

        if random.randint(0, 1) == 1:
            self.bias_mutation_chance *= .95
        else:
            self.bias_mutation_chance *= 1.05263

        if random.randint(0, 1) == 1:
            self.node_mutation_chance *= .95
        else:
            self.node_mutation_chance *= 1.05263

        if random.randint(0, 1) == 1:
            self.enable_chance *= .95
        else:
            self.enable_chance *= 1.05263

        if random.randint(0, 1) == 1:
            self.disable_chance *= .95
        else:
            self.disable_chance *= 1.05263

        if random.randint(0, 1) == 1:
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


class Network:
    InputSize = config['NETWORK'].getint('inputs')
    OutputSize = config['NETWORK'].getint('outputs')
    MaxNodes = config['NETWORK'].getint('max_nodes')

    def __init__(self, genome):
        self.genome = genome
        self.neurons = {}

        for i in range(genome.input_size):
            self.neurons[i] = Neuron()

        for i in range(Network.MaxNodes, Network.MaxNodes + self.genome.output_size):
            self.neurons[i] = Neuron()

        for gene in sorted(genome.genes, key=lambda x: x.out):
            if gene.enabled:
                if gene.out not in self.neurons:
                    self.neurons[gene.out] = Neuron()
                self.neurons[gene.out].incoming.append(gene)
                if gene.into not in self.neurons:
                    self.neurons[gene.into] = Neuron()

    def evaluate(self, inputs, debug=False):
        inputs.append(1)

        if len(inputs) != self.genome.input_size:
            if debug: print("Incorrect number of inputs: ", len(inputs), "; expected ", self.genome.input_size)
            return []

        for i in range(len(inputs)):
            self.neurons[i].value = inputs[i]

        for i, neuron in self.neurons.items():
            if i < self.genome.input_size:
                continue
            if debug: print(i, list(x.into for x in neuron.incoming))
            if not neuron.incoming:
                continue
            val = sum(x.weight * self.neurons[x.into].value for x in neuron.incoming)
            if debug: print(list((x.into, self.neurons[x.into].value) for x in neuron.incoming))
            if debug: print(list(x.weight for x in neuron.incoming))

            neuron.value = self.sigmoid(val)

        outputs = []
        for i in range(Network.MaxNodes, Network.MaxNodes + self.genome.output_size):
            outputs.append(self.neurons[i].value)

        if debug: print("values:", list((i,x.value) for i,x in self.neurons.items()))
        return outputs

    @staticmethod
    def sigmoid(x):
        return 2 / (1 + math.exp(-4.9 * x)) - 1


# unit representing a link between neurons that can be active in a given genome
class Gene:
    Innovation = 0

    def __init__(self):
        # start and end neurons for this connections
        self.into = 0
        self.out = 0

        # weight to multiply value by when evaluating the network
        self.weight = 0.0

        # if this pathway is enabled
        self.enabled = True

        # I don't know what this does
        self.innovation = 0

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def toggle(self):
        self.enabled = not self.enabled

    def is_enabled(self):
        return self.enabled

    def copy(self):
        new_gene = Gene()
        new_gene.into = self.into
        new_gene.out = self.out
        new_gene.weight = self.weight
        new_gene.enabled = self.enabled
        new_gene.innovation = self.innovation
        return new_gene

    def display(self):
        print("Gene ", self.into, " -> ", self.out,"(", self.weight, ")")

    @staticmethod
    def innovate():
        Gene.Innovation += 1
        return Gene.Innovation


class Neuron:
    def __init__(self):
        # list of incoming neuron connections (determined by genes)
        self.incoming = []

        # value of this neurons output
        self.value = 0.0
