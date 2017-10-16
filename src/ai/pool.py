
from src.ai.genome import Genome

Inputs = 100 * 5

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
            genome.max_neuron = Inputs
            genome.mutate()
            self.add_to_species(genome)

    def add_to_species(self, new_genome):

        for species in self.species:
            if species.genomes[0].isSameSpecies(new_genome):
                species.addGenome(new_genome)

    def rank_globally(self):

        ranked = []
        for species in self.species:
            for genome in species.genomes:
                ranked.append(genome)

        ranked.sort(self, lambda x: x.fitness, reverse=True)

        for rank, genome in enumerate(ranked):
            genome.global_rank = rank