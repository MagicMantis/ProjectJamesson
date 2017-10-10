# unit representing a link between neurons that can be active in a given genome
class Gene:
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

    def isEnabled(self):
        return self.enabled

	def copy(self):

		new_gene = Gene()
		new_gene.into = self.into
		new_gene.out = self.out
		new_gene.weight = self.weight
		new_gene.enabled = self.enabled
		new_gene.innovation = self.innovation
		return new_gene
