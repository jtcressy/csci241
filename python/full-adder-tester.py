#! /usr/bin/python3
import RPi.GPIO as GPIO
import argparse
import time

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

class FullAdderTester:
    TESTS = { # (A, B, Cin): (Cout, S)
        (0, 0, 0):(0, 0),
        (0, 0, 1):(0, 1),
        (0, 1, 0):(0, 1),
        (0, 1, 1):(1, 0),
        (1, 0, 0):(0, 1),
        (1, 0, 1):(1, 0),
        (1, 1, 0):(1, 0),
        (1, 1, 1):(1, 1)
    }

    def __init__(self, a, b, cin, out, cout, slow=False, interactive=False):
        self.slow = slow
        self.interactive = interactive
        self.outpins = AttrDict({
            'a': int(a),
            'b': int(b),
            'carryin': int(cin)
        })
        self.inpins = AttrDict({
            'out': int(out),
            "carryout": int(cout)
        })

        GPIO.setmode(GPIO.BCM)
        for pin in self.outpins.values():
            GPIO.setup(pin, GPIO.OUT)
        for pin in self.inpins.values():
            GPIO.setup(pin, GPIO.IN)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        GPIO.cleanup()

    def _query(self, a, b, carry):
        GPIO.output(self.outpins.a, a)
        GPIO.output(self.outpins.b, b)
        GPIO.output(self.outpins.carryin, carry)
        return GPIO.input(self.inpins.out), GPIO.input(self.inpins.carryout)

    def getResult(self):
        return all(self._query(test[0], test[1], test[2]) == self.TESTS[test] for test in self.TESTS.keys())

    def _detailResult(self):
        for test in self.TESTS.keys():
            print(test, ":", self.TESTS[test], "Result: ", self._query(test[0], test[1], test[2]))
            if self.interactive:
                input("Press enter for next test...")
            elif self.slow:
                time.sleep(1)
            yield self._query(test[0], test[1], test[2]) == self.TESTS[test]

    def getDetailedResult(self):
        print("(A, B, Cin) : (Cout, S) Result: (Cout, S)")
        return all(self._detailResult())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test a binary full adder with 5 GPIO pins")
    parser.add_argument("a", metavar="A", help="GPIO pin for input A")
    parser.add_argument("b", metavar="B", help="GPIO pin for input B")
    parser.add_argument("carryin", metavar="CIN", help="GPIO pin for input CARRY_IN")
    parser.add_argument("out", metavar="SUM", help="GPIO pin for single bit SUM from full adder")
    parser.add_argument("carryout", metavar="COUT", help="GPIO pin for CARRY_OUT signal from full adder")
    parser.add_argument("-s", "--slow", default=False, action="store_true", help="Slowly iterate through each test (1 per second) to watch the output (useful if logic probes are attached)")
    parser.add_argument("-i", "--interactive", default=False, action="store_true", help="Iterate through each test one at a time by pressing ENTER on each one (useful for testing with logic probes)")
    args = parser.parse_args()
    with FullAdderTester(args.a, args.b, args.carryin, args.out, args.carryout, slow=args.slow, interactive=args.interactive) as fat:
        if fat.getDetailedResult():
            print("Connected circuit is a functional full-adder")
        else:
            print("Connected circuit is NOT a correctly functioning full-adder")
