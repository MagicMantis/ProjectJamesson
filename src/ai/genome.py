from src.ai.mutator import Mutator
from src.ai.network import Network

Population = 300
DeltaDisjoint = 2.0
DeltaWeights = 0.4
DeltaThreshold = 1.0


class Genome:
    def __init__(self):

        self.genes = []
        self.fitness = 0
        self.adjustedFitness = 0
        self.input_size = 0
        self.output_size = 0
        self.globalRank = 0
        self.network = None
        self.mutator = Mutator()

    def is_same_species(self, other):

        dd = DeltaDisjoint * self.disjoints(other)
        dw = DeltaWeights * self.weights(other)
        return dd + dw < DeltaThreshold

    def disjoints(self, other):

        set1 = set(self.genes)
        set2 = set(other.genes)
        return len(set1 ^ set2) / max(len(set1), len(set2))

    def weights(self, other):

        weight_sum = 0
        coincident = 0
        for innovation, gene in self.genes:
            if innovation in other.genes:
                weight_sum += abs(gene.weight - other.genes[innovation].weight)
                coincident += 1

        return weight_sum / coincident

    def generate_network(self):
        self.network = Network(self)

    def crossover(self, other):
        child = Genome()

        innovations_other = {}
        for gene in other.genes: innovations_other[gene.innovation] = gene

        for gene in self.genes:
            other_gene = innovations_other[gene.innovation]
            if other_gene and other_gene.enabled and self.mutator.random(2) == 1:
                child.genes.append(other_gene.copy())
            else:
                child.genes.append(gene.copy())

		child.mutator = self.mutator.copy()

        return child

	def random_neuron(self, non_input):

		options = set()

		if not non_input:
			for i in range(self.input_size): options.add(i)

		for i in range(MaxNodes, MaxNodes+self.output_size):
			options.add(i)

		for gene in self.genes:
			if not non_input or gene.into > self.input_size:
				options.add(gene.into)
			if not non_input or gene.out > self.input_size:
				options.add(gene.out)

		return random.choice(options)

	def copy(self):

		new_genome = Genome()
		for gene in self.genes:
			new_genome.genes.append(gene.copy())
	
		new_genome.input_size = self.input_size
		new_genome.output_size = self.output_size
		new_genome.mutator = self.mutator.copy()

		return new_genome
