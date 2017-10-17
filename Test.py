from src.ai import Genome
from src.ai import Network
from src.ai import Pool

import random
import time

random.seed(time.time())

# genome = Genome()
# genome.mutator.mutate()
# genome.display()

pool = Pool()
pool.basic_generation()
max_genome = None

thing = []
for i in range(20):
    for species in pool.species:
        for genome in species.genomes:
            n = Network(genome)
            inputs = [[0, 0], [0, 1], [1, 0], [1, 1], [-1, 0], [0, -1], [1, -1], [-1, -1]]
            targets = [(x + y) / 2 for x, y in inputs]
            results = []
            fs = []
            for i in range(len(inputs)):
                results.append(abs(n.evaluate(inputs[i][:])[0] - targets[i]))
                fs.append(n.evaluate(inputs[i][:])[0])
            fitness = 2 - sum(results) / len(results)
            print(results, " Stuff: ", fs, "Fitness: ", fitness)
            genome.fitness = fitness
            if fitness > pool.max_fitness:
                pool.max_fitness = fitness
                max_genome = genome
    thing.append(pool.max_fitness)
    pool.new_generation()
print(thing)

#print("")
#Network(max_genome).evaluate([-1,-1], True)
#print("")
#max_genome.display()
# print("")
