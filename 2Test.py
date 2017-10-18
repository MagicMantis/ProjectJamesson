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
            inputs = [[random.random()*2-1, random.random()*2-1] for i in range(100)]
            targets = [(x + y) / 2 for x, y in inputs]
            results = []
            fs = []
            for i in range(len(inputs)):
                results.append(abs(n.evaluate(inputs[i][:])[0] - targets[i])**2)
                fs.append(n.evaluate(inputs[i][:])[0])
            fitness = 1 - sum(results) / len(results)
            print(results, " Stuff: ", fs, "Fitness: ", fitness)
            genome.fitness = fitness
            if fitness > pool.max_fitness:
                pool.max_fitness = fitness
                max_genome = genome
    thing.append(pool.max_fitness)
    pool.new_generation()

print("")
Network(max_genome).evaluate([-1,-1], True)
print(Network(max_genome).evaluate([0,0],False))
print(Network(max_genome).evaluate([1,1],False))
print(Network(max_genome).evaluate([0,1],False))
print(Network(max_genome).evaluate([1,0],False))
print("")
max_genome.display()
print("")
print(thing)
