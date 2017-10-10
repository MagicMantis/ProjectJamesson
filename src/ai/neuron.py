

class Neuron:
    def __init__(self):
        # list of incoming neuron connections (determined by genes)
        self.incoming = []

        # value of this neurons output
        self.value = 0.0