import numpy as np
from time import time
import hashlib
from Kernel import Kernel

# reversible cellular automata
class CaR(Kernel):

    def __init__(self, rules_path="", verbose = False, debug=False):
        super(CaR, self).__init__(verbose=verbose, debug=debug, heritate_class=self.__class__.__name__)
        self.__version__ = "1.0.0"
        self.X = []
        self.Y = []
        self.rules_path = rules_path
        self.rules = {}
        self.nb_rules = 65536 # default total number of rules
        self.q = -1
        self.T = -1

    def get_values(self, k):
        n = len(self.X)
        return (self.X[k], self.Y[k - 1], self.Y[k], self.Y[(k + 1) % n])

    def format_key(self, key_tpl):
        return "".join(str(e) for e in key_tpl)

    def apply_rule(self, k):

        key = self.get_values(k)
        new_value = self.rules[self.q][self.format_key(key)]

        return new_value

    def gen_random_vector(self, n):
        np.random.seed(self.T)
        return np.random.choice(a=[0, 1], size= 25, p = [1 - 0.52, 0.52])

    def get_random_rule(self):

        sha = hashlib.sha256(self.X)
        hash_X = sha.hexdigest()
        
        q = sum([ord(str(e)) for e in hash_X]) % self.nb_rules

        self.q = q

    def get_random_steps(self):
        self.T = int(str(time())[-3:])

    def run(self, X):
        self.X = X
        self.get_random_steps()
        self.get_random_rule()
        self.set_rules()

        M = self._run()

        return M

    def set_rules(self):
        if self.rules == {}:
            if self.rules_path == "":
                self.gen_rules()
            else:
                self.rules = self.load_json(self.rules_path)

    def _run(self):
        
        nX = len(self.X)
        self.Y = self.gen_random_vector(nX)
        nY = len(self.Y)

        M = [self.X.copy(), self.Y.copy()]
        if nX == nY:
            for t in range(self.T):
                Z = []
                for k in range(nX):
                    Z.append(self.apply_rule(k))
                M.append(np.array(Z.copy()))
                self.X = self.Y.copy()
                self.Y = Z.copy()           

        else:
            raise Exception("Lenght of vectors are different (X: {nX}, y: {nY}".format(nx=nX, nY=nY))

        M = np.matrix(M)

        return M

    def get_last_vectors(self, M):
        return M[-2:,:]

    def gen_rules(self):
        A = [0, 1]
        rules = []
        for i in range(2 ** 16):
            outputs = [int(elem) for elem in np.binary_repr(i, 16)]
            j = 0
            rule = {}
            for a in A:
                for l in A:
                    for c in A:
                        for r in A:
                            rule["{a}{l}{c}{r}".format(a=a, l=l, c=c, r=r)] = outputs[j]
                            j += 1
            rules.append(rule)

        self.rules = rules


car = CaR(r"C:\Users\GDognin\DATA\Informatique\alpha_lambda_software\ca_cryptor\als_1\rules.json")

X = np.random.choice(a=[0, 1], size= 25, p = [1 - 0.52, 0.52])

car.run(X)