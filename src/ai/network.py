from src.ai.neuron import Neuron
from src.ai.genome import Genome
import math


class Network:

    MaxNodes = 10000

    def __init__(self, genome):
        self.genome = genome
        self.neurons = {}

        for gene in sorted(genome.genes, lambda x: x.out, reverse=True):
            if gene.enabled:
                if gene.out not in self.neurons:
                    self.neurons[gene.out] = Neuron()
                self.neurons[gene.out].incoming.append(gene)
                if gene.into not in self.neurons:
                    self.neurons[gene.into] = Neuron()

    def evaluate(self, inputs):

        if len(inputs) != self.genome.input_size:
            print("Incorrect number of inputs: ", len(inputs), "; expected ", self.genome.input_size)
            return []

        for i in range(len(input)):
            self.neurons[i].value = inputs[i]

        for _, neuron in self.neurons:
            val = sum(neuron.incoming, lambda x: x.weight * x.into.value)

            if val > 0: neuron.value = self.sigmoid(val)

        outputs = []
        for i in range(Network.MaxNodes, Network.MaxNodes + self.genome.output_size):
            outputs.append(self.neurons[i].value)

        return outputs

    @staticmethod
    def sigmoid(x):
        return 2 / (1 + math.exp(-4.9 * x)) - 1
