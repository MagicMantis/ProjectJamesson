# Title: AI Library for Stock App
# Author: Joseph Savold (Adapted from Sethbling's NEATEvolve script)
# Purpose: Allow for adaptive nerual network trained through evolution

MutateConnectionsChance = 0.25
PerturbChance = 0.90
CrossoverChance = 0.75
LinkMutationChance = 2.0
NodeMutationChance = 0.50
BiasMutationChance = 0.40
EnableMutationChance = 0.2
DisableMutationChance = 0.4
StepSize = 0.1


class Neuron:

	def __init__(self):
	
		# list of incoming neuron connections (determined by genes) 
		self.incoming = {}

		# value of this neruons output
		self.value = 0.0

# unit representing a link between neurons that can be active in a given genome
class Gene:

	def __init__(self):

		# start and end neurons for this connections
		self.into = 0
		self.out = 0

		# weight to multiply value by when evaluating the network
		self.weight = 0.0

		# if this pathway is enabled
		self.enabled = true

		# I don't know what this does
		self.innovation = 0
	
	def enable(self):
		self.enabled = true

	def disable(self):
		self.enabled = false

	def isEnabled(self):
		return self.enabled


class Genome:

	def __init__(self):
	
		self.genes = {}
		self.fitness = 0
		self.adjustedFitness = 0
		self.network = None
		self.maxneuron = 0
		self.globalRank
		self.mutationProfile = MutationProfile()

	def isSameSpecies(self, other):

		dd = DeltaDisjoint * self.disjoints(other)
		dw = DeltaWeight * self.weights(other)
		return dd + dw < DeltaThreshhold

	def disjoints(self, other):
		
		set1 = set(self.genes)
		set2 = set(other.genes)
		return len(set1 ^ set2) / max(len(set1), len(set2))

	def weights(self, other):

		sum = 0
		coincident = 0
		for innovation, gene in self.genes:
			if innovation in other.genes:
				sum += abs(gene.weight - other.genes[innovation].weight)
				coincident += 1

		return sum / coincident
		

class MutationProfile:

	def __init__(self):

		self.mutate_connections_chance = MutateConnectionsChance
		self.link_mutation_chance = LinkMutationChance
		self.bias_mutation_chance = BiasMutationChance
		self.node_mutation_chance = NodeMutationChance
		self.enable_chance = EnableMutationChance
		self.disable_chance = DisableMutationChance
		self.step_size = StepSize


class Species:

	def __init__(self):
		
		self.top_fitness = 0
		self.staleness = 0
		self.genomes = []
		self.average_fitness = 0


class Pool:

	def __init__(self):
		
		self.species = []
		self.population = 1000
		self.generation = 0
		self.innovation = 0
		self.current_species = 1
		self.current_genome = 1
		self.current_frame = 0
		self.max_fitness = 0

	def generate_basic(self):

		for i in range(self.population):
			genome = Genome()
			genome.maxneuron = Inputs
			genome.mutate()
			self.add_to_species(genome)
	
	def add_to_species(self, new_genome):

		for species in self.species:
			if species.genomes[0].isSameSpecies(new_genome):
				species.addGenome(new_genome)

