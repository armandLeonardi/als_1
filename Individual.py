from __future__ import annotations

def buildCustomIndividualClass(base):

    class Individual(base):

        def __init__(self, **kwargs):
            super(Individual, self).__init__(**kwargs)
            self.score = 0

        def copy(self):

            base_indv = super(Individual, self).copy()
            return Individual(**base_indv.__dict__)

    return Individual


if __name__ == "__main__":

    class Human:

        def __init__(self, name, size):
            self.name = name
            self.size = size

        def plop(self):
            return 'plop'

        def copy(self):
            return Human(name=self.name, size=self.size)


    idv_class = buildCustomIndividualClass(Human)

    idvh = idv_class(name = 'toto', size=180)

    idvh.plop()

    idvh2 = idvh.copy()

    idvh.score = 666

    print(idvh.score)
    print(idvh2.score)
