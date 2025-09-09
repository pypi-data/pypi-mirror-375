import unittest
import json
from random import random, randint
from sklearn.metrics import r2_score
from neuralplex import Network, Layer, Neuron

class Test(unittest.TestCase):

    def test_nibbles(self):

        ITERATION = int(1e4)
        STEP = 1e-4

        l1 = Layer(neurons=[Neuron(m=random()) for i in range(0, 4)], step=STEP)

        l2 = Layer(neurons=[Neuron(m=random()) for i in range(0, 8)], step=STEP)

        l3 = Layer(neurons=[Neuron(m=random())], step=STEP)

        n1 = Network(
            [
                l1,
                l2,
                l3,
            ]
        )

        print("Training the model.")
        for i in range(0, ITERATION):

            if i % 1e3 == 0:
                print(f"Training iteration: {i}")

            rn = randint(1, 15)

            b = [int(n) for n in bin(rn)[2:]]

            while len(b) < 4:
                b = [0] + b

            n1.train(b, [rn])


        ys = []
        ys_predicted = []
        for i in range(1, 16):

            b = [int(n) for n in bin(i)[2:]]

            while len(b) < 4:
                b = [0] + b

            pn = n1.predict(b)

            ys.append(i)
            ys_predicted.append(pn[0])

            print(f"{i} input: {json.dumps(b)}, truth: {i} prediction: {json.dumps(pn)}")

        R2 = r2_score(ys, ys_predicted)

        print(f"R2: {R2}")

        self.assertGreaterEqual(R2, .9)

if __name__ == '__main__':
    unittest.main()
