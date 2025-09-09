from typing import List, Self

from neuralplex.neuron import Neuron


class Layer:

    def __init__(self, neurons: List[Neuron], step: float = None):
        self.neurons = neurons
        self.step = step
        if not self.step is None:
            for neuron in self.neurons:
                if neuron.step is None:
                    neuron.step = self.step

    def connect(self, layer: Self) -> None:
        for p1 in self.neurons:
            for p2 in layer.neurons:
                p1.connectRHS(p2)
