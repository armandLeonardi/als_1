from Kernel import Kernel, Message
import numpy as np
from PgSqlMgt import PgSqlMgt
from Individual import buildCustomIndividualClass
from PortFolio import PortFolio, Asset

# global variable
# dynamic class creation (from Portfolio)
Individual_portfolio = buildCustomIndividualClass(PortFolio)


class Functions_1(Kernel):

    def __init__(self, config_path, verbose=True, debug=True):
        super(Functions_1, self).__init__(verbose=verbose, debug=debug, config_path=config_path)
        self.__version__ = "1.0.0"
        self.params = {}
        self.pgmg = None

    def load_config(self):
        params = super(Functions_1, self).load_config()
        self.params = params

        message = Message(10, "Current config: {config}".format(config=params))
        self.display(message)

    def create_pgmg_connection(self):
        # get params for connection
        params = self.params["connection"]
        host = params["host"]
        port = params["port"]
        user = params["user"]
        password = params["password"]
        database = params["database"]
        encoded = params["encoded"]

        pgmg = PgSqlMgt(host=host,
                        port=port,
                        user=user,
                        password=password,
                        database=database,
                        encoded=encoded)

        pgmg.connect()

        message = Message(10, pgmg.version())
        self.display(message)

        self.pgmg = pgmg

    def generate_population(self):
        
        # get params for generation
        params = self.params["generate"]
        nb_indiv = params["nb_indiv"]
        min_share = params["min_share"]
        max_share = params["max_share"]
        nb_asset = params["nb_asset"]
        
        schema = self.params["schema"]

        if self.pgmg is None:
            self.create_pgmg_connection()

        tickers = self.pgmg.select("select distinct v_ticker from {schema}.pi2_a5_cac_returns".format(schema=schema))
        tickers = np.array(tickers).ravel()
        self.params["generate"]["tickers"] = tickers

        message = Message(10, "Current tickers: {tickers}".format(tickers=tickers))
        self.display(message)

        population = []
        for i in range(nb_indiv):
            p = self.generate_portfolio(tickers, nb_asset, min_share, max_share)
            population.append(p)

        return population

    def generate_portfolio(self, tickers, nb_asset, min_share, max_share):

        selected_tickers = np.random.choice(tickers, size=nb_asset, replace=False)
        selected_nb_shares = np.random.randint(min_share, max_share, size=nb_asset)
        p = Individual_portfolio()
        for ticker, nb_share in zip(selected_tickers, selected_nb_shares):
            # p.append(ticker, nb_share)
            asset = Asset(ticker=ticker, nb_shares=nb_share)
            p.append(asset)

        return p

    def random_f(self, x, sig):
        y = x + x * np.random.normal() * sig
        return y if y > 0 else 0

    def mutate(self, population):

        params = self.params["mutate"]
        n_random_select = params["n_random_select"]
        n_random_tickers = params["n_random_tickers"]
        sig0 = params["sig0"]
        t = self.params["t"]
        T = self.params["T"]


        n_random_select = int(n_random_select * (1 - (t - 1) / T))
        n_random_tickers = int(n_random_tickers * (1 - (t - 1) / T))
        sig = sig0 * (1 - (t - 1) / T)

        n_random_select = 2 if n_random_select == 0 else n_random_select
        n_random_tickers = 2 if n_random_tickers == 0 else n_random_tickers

        # should be develop a method random_indiv_choice which return given random selected indivs 
        selected_indiv = self.random_choice(population, size=n_random_select)

        for indiv in selected_indiv:

            selected_tickers = np.random.choice(indiv.tickers(), size=n_random_tickers)
            for ticker in selected_tickers:
                new_nb_share = int(self.random_f(indiv[ticker].nb_shares, sig))
                indiv.update(ticker, nb_shares=new_nb_share)
    
        return population

    def random_choice(self, population, size):
        # shoud be completed -> return selected indiv
        idxs = list(range(len(population)))
        selected_indivs = []

        if idxs != []:
            selected_idxs = np.random.choice(idxs, size=size)
            selected_indivs = [population[idx] for idx in selected_idxs]

        return selected_indivs

    def crossover(self, population):

        params = self.params["crossover"]
        nb_asset_select = params["nb_asset_select"]
        T = self.params["T"]
        t = self.params["t"]

        new_population = []
        nb_asset_select = int(round(nb_asset_select * (1 - (t - 1) / T)))

        if nb_asset_select > 0:
            while len(new_population) < 2 * len(population):
                portfolio_1, portfolio_2 = self.random_choice(population, 2)
                child = self.crossover_portfolios(portfolio_1, portfolio_2, nb_asset_select)
                new_population.append(child.copy())
        else:
            new_population = population.copy()

        return new_population

    def sort_select(self, population):

        new_population = sorted(population, key = lambda x: x.score)
        size = self.params["generate"]["nb_indiv"]

        if len(new_population) > size:
            new_population = new_population[:size]

        return new_population

    def empty_porfolio_score_0(self, population):

        for indiv in population:
            if indiv.assets == []:
                print(indiv)
                indiv.score = 0

        return population

    def crossover_portfolios(self, portfolio_1, portfolio_2, nb_asset_select):

        selected_assets_1 = np.random.choice(portfolio_1.tickers(), size=nb_asset_select, replace=False)
        selected_assets_2 = np.random.choice(portfolio_2.tickers(), size=nb_asset_select, replace=False)

        child_portfolio = Individual_portfolio()

        for selected_ticker in selected_assets_1:
            asset = portfolio_1[selected_ticker]
            child_portfolio.append(asset)

        for selected_ticker in selected_assets_2:
            asset = portfolio_2[selected_ticker]
            child_portfolio.append(asset)

        return child_portfolio

    def retain(self, population):
        
        params = self.params["fitness"]
        start_date = params["start_date"]
        end_date = params['end_date']
        t = self.params["t"]

        values = []
        for indiv in population:
            ret, vol = self.compute_return_std(indiv, start_date, end_date)
            values.append((t, ret, vol, indiv.score))

        return values

    def fitness(self, population):

        if self.pgmg is None:
            self.create_pgmg_connection()

        for indiv in population:
            self.fitness_portfolio(indiv)

        population = self.sort_select(population)

        return population

    def fitness_portfolio(self, portfolio):
        params = self.params["fitness"]
        start_date = params["start_date"]
        end_date = params['end_date']
        ret_objectiv = params['return']
        vol_objectiv = params['volatility']
        max_share = params["max_share"]
        min_share = params["min_share"]
        nb_asset = params["nb_asset"]
        score = 0

        
        for asset in portfolio.assets:
            if not (min_share <= asset.nb_shares <= max_share):
                score += 1
        
        if len(portfolio) != nb_asset:
            score += 0.5
        

        ret, vol = self.compute_return_std(portfolio, start_date, end_date)

        if vol == 0:
            score += 10
        else:
            score += ((ret / vol) - (ret_objectiv / vol_objectiv)) ** 2
    
        portfolio.score = score

    def compute_return_std(self, portfolio, start_date, end_date):

        if self.pgmg is None:
            self.create_pgmg_connection()

        schema = self.params["schema"]

        R = []
        for ticker, weight in zip(portfolio.tickers(), portfolio.weights()):
            query = """select f_return
                    FROM {schema}.pi2_a5_cac_returns
                    where v_ticker = '{ticker}'
                    and t_date >= '{start_date}'
                    and t_date <= '{end_date}'
                    """.format(schema=schema, ticker=ticker, start_date=start_date, end_date=end_date)

            returns = self.pgmg.select(query)
            returns = np.array(returns).ravel()
            R.append([weight * r_i for r_i in returns])

        R = np.sum(np.array(R), axis=1)

        var = np.std(R)
        ret = np.prod(1 + R)

        return ret, var

    def stop(self, population):
        out = False
        params = self.params["stop"]
        epsilon = params["epsilon"]
        t = self.params['t']

        if t > 0:
            for indiv in population:
                if 0 < indiv.score <= epsilon:
                    out = True

        return out

    def display_score(self, population):
        out_values = ()
        t = self.params["t"]

        min_score = min(population, key=lambda x: x.score)    
        max_score = max(population, key=lambda x: x.score)    
        avg_score = np.mean([indiv.score for indiv in population])

        message = Message(10, "{t} | {min} | {avg} | {max}".format(t=t, min=min_score.score, avg=avg_score, max=max_score.score))
        self.display(message)

if __name__ == "__main__":

    f1 = Functions_1('./function_1_config.json')
    f1.load_config()
    population = f1.generate_population()
    population = f1.crossover(population)
    population = f1.mutate(population)
    f1.fitness(population)

    f1.display_score(population)
        