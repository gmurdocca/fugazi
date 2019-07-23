#!/usr/bin/env python

import requests
import logging
import yaml
import json
import sys
import os

cryptocompare_apikey = ""
cryptoapis_apikey = ""

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class Coin:

    def __init__(self, api_key, symbol):
        self.api_key = api_key
        self.symbol = symbol
        self.default_headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key
                }
        self.asset_file = "./assets.json"
        self.asset = self._get_asset_by_symbol(self.symbol)

    def _get_all_assets(self):
        if os.path.exists(self.asset_file):
            with open(self.asset_file, "r") as asset_file:
                assets = json.load(asset_file)
        else:
            assets = []
            skip = 0
            while True:
                url = f"https://api.cryptoapis.io/v1/assets?skip={skip}&limit=100"
                response = requests.get(url, headers=self.default_headers)
                chunk = json.loads(response.text)
                logger.debug(chunk['meta'])
                assets += chunk['payload']
                index = chunk['meta']['index']
                total_count = chunk['meta']['totalCount']
                limit = chunk['meta']['limit']
                results = chunk['meta']['results']
                if index + results < total_count:
                    skip = index + results
                else:
                    break
            # write assets to file
            with open(self.asset_file, "w") as asset_file:
                asset_file.write(json.dumps(assets))
        return assets

    def _get_asset_by_symbol(self, symbol):
        assets = self._get_all_assets()
        for asset in assets:
            if 'originalSymbol' in asset and asset['originalSymbol'] == symbol:
                return asset
        raise Exception(f"Couldn't find asset with symbol: {symbol}")

#    def current_price(self):
#        #url = f"https://min-api.cryptocompare.com/data/price?fsym={self.from_sym}&tsyms={self.to_sym}"
#        headers = {"Apikey": self.api_key}
#        result = requests.get(url, headers=headers)
#        current_price = json.loads(result.text)[self.to_sym]
#        return current_price

    def get_ath(self):
        return self.asset['allTimeHigh']

    def get_current_price(self):
        return self.asset['price']

    def get_24hour_volume(self):
        return self.asset['volume']
        
        
if __name__ == "__main__":
#    coins_owned = ['BTC', 'BCH', 'ETH']
#    for coin_owned in coins_owned:
#        current_price = Coin(cryptocompare_apikey, coin_owned, 'AUD').current_price()
#        print(coin_owned, current_price)
    coin = Coin(cryptoapis_apikey, 'ETH')

    print(coin.get_ath(), coin.get_current_price(), coin.get_24hour_volume()) 


