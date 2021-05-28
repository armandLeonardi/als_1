from GA import GeneticAlgorithm
import matplotlib.pyplot as plt
import numpy as np
from argparse import ArgumentParser
import os
from datetime import datetime
import json
from Kernel import Message


if __name__ == "__main__":

    parser = ArgumentParser("Heuristic porforlio")
    parser.add_argument("-f", "--func_obj", type=str, help="current function python object to take in accoun", default="")
    parser.add_argument("-c", "--config", type=str, help="configuration for function object", default="")
    parser.add_argument("-p", "--plot", type=bool, help="true if you want plot result. False otherwise", default=False)
    parser.add_argument("-s", "--save", type=bool, help="true if you want to save you results as json", default=False)
    parser.add_argument("-v", "--verbose", type=bool, help="true if you want display current computing", default=False)
    parser.add_argument("-d", "--debug", type=bool, help="true if you want display more precise information on current computing", default=False)

    args =parser.parse_args()

    func_obj_str = args.func_obj.strip()
    config_path = args.config.strip()
    ploting = args.plot
    saving = args.save
    verbose = args.verbose
    debug = args.debug

    exec("from {func_obj_str} import {func_obj_str}".format(func_obj_str=func_obj_str))
    exec("func = {func_obj_str}(config_path=\"{config_path}\", debug={debug}, verbose={verbose})".format(func_obj_str=func_obj_str, config_path=config_path, debug=debug, verbose=verbose))

    func.load_config()

    T = func.params["T"]

    ga = GeneticAlgorithm(functions=func, debug=debug, verbose=verbose)

    result = ga.run()

    if result != []:
        message = Message(10, result)
        ga.display(message)

    if ploting:

        retain_values = ga.retain_values

        values = []
        for gen in retain_values:
            values += gen

        t, ret, vol, score = zip(*values)

        avg_score = []
        avg_ret = []
        avg_sig = []
        for i in range(T):
            _tmp_sc = []
            _tmp_re = []
            _tmp_si = []
            for tpl in values:
                if tpl[0] == i:
                    _tmp_re.append(tpl[1])
                    _tmp_si.append(tpl[2])
                    _tmp_sc.append(tpl[3])
            avg_score.append(np.min(_tmp_sc))
            avg_ret.append(np.min(_tmp_re))
            avg_sig.append(np.min(_tmp_si))


        plt.subplot(121)
        plt.scatter(avg_sig, avg_ret, s=25, c=range(T), cmap='gray')
        plt.plot(func.params["fitness"]["volatility"], func.params["fitness"]["return"], "rx")
        plt.xlabel("$\sigma$")
        plt.ylabel("r")
        plt.subplot(122)
        plt.scatter(range(T), avg_score, s=25, c=range(T), cmap='Greens')
        plt.ylabel("score")
        plt.xlabel("generation")

        plt.show()

    if saving:

        now = datetime.now().strftime("%m%d%Y%H%M%S")
        with open("heuristoc_port_{time}".format(time=now), "w", encoding="utf8") as f:
            json.dump(ga.to_dict(), f)