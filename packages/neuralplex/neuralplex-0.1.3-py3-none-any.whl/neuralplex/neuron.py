import math
import statistics
from typing import Dict, List, Self
from scipy.stats import linregress


class Neuron:

    def __init__(self, m: float, b: float = 0, step: float = None, name=None):
        self.m = m  # weight
        self.b = b  # lift
        self.name = name
        self.step = step
        self.value = 0
        self.activation_count = 0
        self.neuronsRHS: List[Self] = []
        self.neuronsLHS: List[Self] = []
        self.activation: Dict[Self, float] = {}
        self.propagation: Dict[Self, float] = {}

    def connectRHS(self, neuronRHS: Self) -> None:
        if neuronRHS not in self.neuronsRHS:
            self.neuronsRHS.append(neuronRHS)
        if self not in neuronRHS.neuronsLHS:
            neuronRHS.connectLHS(self)

    def connectLHS(self, neuronLHS: Self) -> None:
        if neuronLHS not in self.neuronsLHS:
            self.neuronsLHS.append(neuronLHS)
        if self not in neuronLHS.neuronsRHS:
            neuronLHS.connectRHS(self)

    def disconnectRHS(self, neuronRHS: Self) -> None:
        if neuronRHS in self.neuronsRHS:
            self.neuronsRHS.remove(neuronRHS)
        if self in neuronRHS.neuronsLHS:
            neuronRHS.disconnectLHS(self)
        if len(self.neuronsRHS) == 0:
            for neuron in self.neuronsLHS:
                neuron.disconnectRHS(self)

    def disconnectLHS(self, neuronLHS: Self) -> None:
        if neuronLHS in self.neuronsLHS:
            self.neuronsLHS.remove(neuronLHS)
        if self in neuronLHS.neuronsRHS:
            neuronLHS.disconnectRHS(self)
        if len(self.neuronsLHS) == 0:
            for neuron in self.neuronsRHS:
                neuron.disconnectLHS(self)

    def activate(self, value: float, neuron: Self = None) -> None:
        if self.activation_count == 0:
            self.activation = {}
        self.activation_count = self.activation_count + 1
        self.activation.update({neuron: value})
        if len(self.neuronsLHS) == 0 or self.activation_count == len(self.neuronsLHS):
            self.value = self.m * sum(self.activation.values())
            for neuron in self.neuronsRHS:
                neuron.activate(self.value, self)
                # Under what conditions should a numeric activation value be propagated?
            self.activation_count = 0

    def propagate(self, error: float, neuron: Self = None) -> None:
        self.propagation.update({neuron: error})
        if len(self.neuronsRHS) == 0 or len(self.propagation) == len(self.neuronsRHS):
            for error in self.propagation.values():
                self.m = self.m - (error * self.step)
                # This is a primitive implementation; however, I have some ideas for how to improve it.
                # Please let me know if you have any thoughts on how this should be implemented.
            error_total = sum(self.propagation.values())
            for neuron in self.neuronsLHS:
                neuron_activation_value = self.activation[neuron]
                if neuron_activation_value > 0 and error_total > 0 or neuron_activation_value < 0 and error_total < 0:
                    neuron.propagate(error_total, self)
                else:
                    neuron.propagate(math.copysign(1, error_total), self)
                # Likewise, the "backpropagation" still needs a lot of work.
            self.propagation = {}
