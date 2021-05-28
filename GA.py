import numpy as np
from Kernel import Kernel, Message

class GeneticAlgorithm(Kernel):

    def __init__(self, functions=None, verbose=True, debug=False):
        super(GeneticAlgorithm, self).__init__(verbose=verbose, debug=debug)
        self.__version__ = "1.0.6"
        self.functions = functions # object which contain mandatory functions
        self.population = []
        self.retain_values = []

    def check_functions(self):
        # vérifier sir l'objet fonction est présent et s'il possèbe bien les fonctions requises.

        out = True
        funcs = ['generate_population', 'crossover', 'mutate', 'retain', 'fitness', 'stop', 'display_score']

        if self.functions is not None:
            for func in funcs:
                message = Message(10, "Check if '{func}' is present".format(func=func))
                self.display(message)
                try:
                    exec("self.functions.{func}".format(func=func))
                except Exception as error:
                    message = Message(40, error)
                    raise Exception(message)
        else:
            raise Exception("functions attribute should be set")

    def run(self):

        self.check_functions()

        result = []

        population = self.functions.generate_population()
        population = self.functions.fitness(population)

        T = self.functions.params["T"]

        for t in range(T):

            self.functions.params['t'] = t

            message = Message(20, "search... {pct}".format(pct=t / T))
            self.display(message, end="\r")

            self.retain_values.append(self.functions.retain(population))
            # population = self.functions.crossover(population)
            population = self.functions.mutate(population)
            population = self.functions.fitness(population)
            self.functions.display_score(population)

            if self.functions.stop(population):

                message = Message(20, "stop criteria true")
                self.display(message)

                result = min(population, key=lambda x: x.score)
                break
        
            self.population = population
        return result

    def to_dict(self):
        out = {"populasion": [indiv.to_dict() for indiv in self.population]}
        return out