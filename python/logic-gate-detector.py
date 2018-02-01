#! /usr/bin/python3
import RPi.GPIO as GPIO
import argparse

class GateDetector:
    GATE = {
        (0, 0, 0, 1): "AND",
        (1, 1, 1, 0): "NAND",
        (0, 1, 1, 1): "OR",
        (1, 0, 0, 0): "NOR",
        (0, 1, 1, 0): "XOR",
        (1, 0, 0, 1): "XNOR"
    }
    TRUTH = [ # a, b list of tuples
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1)
    ]

    def __init__(self, a, b, c):
        self.a_pin = a
        self.b_pin = b
        self.c_pin = c
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.a_pin, GPIO.OUT)
        GPIO.setup(self.b_pin, GPIO.OUT)
        GPIO.setup(self.c_pin, GPIO.IN)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        GPIO.cleanup()

    def _query(self, a, b):
        GPIO.output(self.a_pin, a)
        GPIO.output(self.b_pin, b)
        return GPIO.input(self.c_pin)

    def _getTruth(self):
        for truth in self.TRUTH:
            yield self._query(truth[0], truth[1])

    def getResult(self):
        result = tuple(self._getTruth())
        output = "UNKNOWN"
        try:
            output = self.GATE[result]
        except KeyError as e:
            print("Unknown truth table result of: {}".format(e))
        return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test logic gates using 3 GPIO pins")
    parser.add_argument("a", metavar="A", help="GPIO pin for input A to logic gate")
    parser.add_argument("b", metavar="B", help="GPIO pin for input B to logic gate")
    parser.add_argument("c", metavar="OUT", help="GPIO pin for output from logic gate")
    args = parser.parse_args()
    with GateDetector(int(args.a), int(args.b), int(args.c)) as gd:
        print("Gate on A={}, B={}, OUT={} is an {} gate.".format(args.a, args.b, args.c, gd.getResult()))
