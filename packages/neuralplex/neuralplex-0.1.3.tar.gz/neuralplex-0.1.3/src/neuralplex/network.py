from typing import List
from neuralplex import Layer


class Network:

    def __init__(self, layers: List[Layer]):
        self.layers = layers
        self.input_layer = layers[0]
        self.output_layer = layers[len(layers) - 1]
        for i in range(0, len(layers) - 1):
            l1 = layers[i]
            l2 = layers[i + 1]
            l1.connect(l2)

    def train(self, X_train: List[float], y_train: List[float]) -> None:
        if len(self.input_layer.neurons) != len(X_train):
            raise Exception(
                f"The length of the input training values, {len(X_train)}, is not equal to the length of input neurons: {len(self.input_layer.neurons)}"
            )
        if len(self.output_layer.neurons) != len(y_train):
            raise Exception(
                f"The length of the output training values, {len(y_train)}, is not equal to the length of output neurons: {len(self.output_layer.neurons)}"
            )

        # Activation Stage
        for i in range(0, len(X_train)):
            self.input_layer.neurons[i].activate(X_train[i], None)

        # Backpropagation Stage
        for i in range(0, len(y_train)):
            yi = y_train[i]
            neuron = self.output_layer.neurons[i]
            neuron.propagate(neuron.value - yi, None)

    def predict(self, X: List[float]) -> List[float]:
        if len(self.input_layer.neurons) != len(X):
            raise Exception(
                f"The length of the input values, {len(X)}, is not equal to the length of input neurons: {len(self.input_layer.neurons)}"
            )

        for i in range(0, len(X)):
            self.input_layer.neurons[i].activate(X[i])

        return [neuron.value for neuron in self.output_layer.neurons]
