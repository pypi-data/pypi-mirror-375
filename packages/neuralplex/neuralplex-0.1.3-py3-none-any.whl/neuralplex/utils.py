from neuralplex.network import Network


def get_edge_data(network: Network):

    records = []
    for layer in network.layers:
        for neuron1 in layer.neurons:
            if len(neuron1.neuronsRHS) != 0:
                for neuron2 in neuron1.neuronsRHS:
                    records.append({"source": neuron1.name, "target": neuron2.name, "weight": neuron1.m})
            else:
                records.append({"source": neuron1.name, "target": None, "weight": neuron1.m})
    return records
