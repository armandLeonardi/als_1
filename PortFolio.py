"""
Asset and Porfolio object. Use it to store and work with financial assets.
Usage in __main__ part (end of script).

History:
    - 18MAY21: Asset, creation of V 1.0.0
    - 18MAY21: Portfolio, creation of v 1.0.0
    - 21MAY21: add tickers method
    - 22MAY21: add weights method

Future features:
    - Porfolio: for append method, check if the asset already exist. Update nb_shares if yes. Add if no.

"""

class Asset(object):
    """
    Finance asset object. Basic model of an asset.

    Attributes:
    - ticker (str)  : title of the asset
    - spot (float)  : current spot on market
    - nb_share (int): current amout of hold shares
    """

    def __init__(self, ticker: str = "", spot:float = 0.0, nb_shares:int = -1, **kwagrs) -> None:
        """Asset constructor

        Args:
            ticker (str, optional): name of the asset. Defaults to "".
            spot (float, optional): current spot of the asset. Defaults to 0.0.
            nb_shares (int, optional): ammout hold share. Defaults to -1.
        """

        self.__version__ = "1.0.0"
        self.ticker = ticker
        self.spot = spot
        self.nb_shares = nb_shares

    def __gt__(self, asset:"Asset") -> bool:
        """Compare two assets under amount (nb_share * spot)
        Return True if the amount is greater than the other asset.
        """

        out = False
        if self() > asset():
            out = True
        return True

    def __call__(self) -> float:
        "Return the amount of asset (nb_shares * spot)"

        return self.nb_shares * self.spot

    def __repr__(self) -> str:
        "Confort displaying. Use it in interativ mode or for debug."

        outStr = "<Asset({ticker: <25} | {value: <8} | {nbShare})>".format(ticker=self.ticker, value=self.spot, nbShare=self.nb_shares)
        return outStr

    def copy(self) -> "Asset":
        "Return a copy of current asset"
        return Asset(ticker=self.ticker, spot=self.spot, nb_shares=self.nb_shares)

    def to_dict(self):
        out = {"ticker": self.ticker, "spot": self.spot, "nb_share": self.nb_shares}
        return out

class PortFolio:
    """
    Simple model of a portfolio. Compose by a list of assets (Asset object)
    """

    def __init__(self, assets:list = [], **kwargs) -> None:
        """Porfolio constructor.

        Args:
            assets (list, optional): list of assets holded . Defaults to [].
        """

        self.__version__ = "1.0.0"
        self.assets = [assets.copy() for assets in assets]

    def __repr__(self) -> str:
        "Confort displaying. Use it in interativ mode or for debug."

        outStr = ",\n".join(asset.__repr__() for asset in self.assets)
        outStr = "<Portfolio[\n{outStr}]>".format(outStr=outStr)
        return outStr

    def tickers(self):
        return [asset.ticker for asset in self.assets]

    def weights(self):
        total_share = sum([asset.nb_shares for asset in self.assets])

        weights = [asset.nb_shares / total_share for asset in self.assets]

        return weights

    def append(self, asset:Asset) -> None:
        """Add a copy of asset input to the portfolio. 

        Args:
            asset (Asset): asset to add
        """

        ticker = asset.ticker
        _asset = self._find(ticker)

        if _asset is None:
            self.assets.append(asset.copy())
        else:
            _asset.nb_shares += asset.nb_shares

    def pop(self, ticker:str) -> None:
        ticker_idx = self.assets.find(ticker)
        _asset = self.assets.pop(ticker_idx)

    def __len__(self) -> int:
        "Return the number of asset"
        return len(self.assets)

    def amount(self) -> float:
        "Return the total amout of the portfolio. sum of nb_asset * spot"
        A = sum([asset() for asset in self.assets])
        return A

    def __getitem__(self, ticker: str) -> Asset:
        "Return the given asset"
        return self._find(ticker)

    def update(self, ticker:str, spot:float= -1, nb_shares:int= -1) -> None:
        """Update the number of share of spot of given asset.
            -1 mean, there is not update to do.

        Args:
            ticker (str): asset ticker to update 
            spot (float, optional): new market spot to update. Defaults to -1.
            nb_shares (int, optional): new number of asset to update. Defaults to -1.
        """

        asset = self._find(ticker)

        if spot >= 0:
            asset.spot = spot
        if nb_shares >= 0:
            asset.nb_shares = nb_shares

    def _find(self, ticker:str) -> Asset:
        """Return asset corresponding to given ticket. If it's exist in portfolio.
        Return None otherwise.

        Args:
            ticker (str): ticker of the asset to search

        Returns:
            Asset: asset corresponding to given ticker.
        """

        _asset = None
        for asset in self.assets:
            if asset.ticker == ticker:
                _asset = asset
                break
        return _asset

    def copy(self):
        return PortFolio(assets=self.assets) # copy already take in account in Portfolio constructor

    def to_dict(self):
        out = {"assets": [asset.to_dict() for asset in self.assets]}
        return out

if __name__ == "__main__":
    
    a1 = Asset("cac40",5141,3)
    a2 = Asset("Oil brent",98,100)
    a3 = Asset("Silver", 2000,50)

    print(a1 > a2)

    assets = [a1, a2, a3]

    P = PortFolio(assets)

    print(P)

    print(len(P))

    print(P.amount())

    print(P["cac40"])

    P.update('Silver', spot=2020.45)
    P.update('Oil brent', nb_shares=76)

    print(P.amount())

    a4 = Asset("Arcelor Mittal", 34.72, 76)

    P.append(a4)

    print(P)