#!/usr/bin/env python

import traceback
import requests
import logging
import yaml
import time
import json
import sys
import pdb
import os


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

config_file = ".config"
with open(config_file, "r") as config_file:
    config = yaml.load(config_file.read(), Loader=yaml.Loader)


class Coin:

    def __init__(self, api_key, symbol, freshness=5):
        """
        freshness in seconds
        """
        self.api_key = api_key
        self.symbol = symbol
        self.default_headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key
                }
        self.asset_file = "./assets.json"
        self.freshness = freshness
        self.asset_detail = None

    @property
    def asset(self):
        return self._get_asset_by_symbol(self.symbol)

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

    def is_fresh(self):
        """
        returns True if asset_detail age < self.freshness
        """
        if self.asset_detail and time.time() - self.asset_detail['timestamp'] < self.freshness:
            return True
        return False

    def _get_asset_by_symbol(self, symbol):
        if not self.is_fresh():
            found = False
            assets = self._get_all_assets()
            for asset in assets:
                if 'originalSymbol' in asset and asset['originalSymbol'] == symbol:
                    found = True
                    url = f'https://api.cryptoapis.io/v1/assets/{asset["_id"]}'
                    response = requests.get(url, headers=self.default_headers)
                    data = json.loads(response.text)['payload']
                    self.asset_detail = {
                            'timestamp': time.time(),
                            'asset': data
                            }
                    break
            if not found:
                raise Exception(f"Couldn't find asset with symbol: {symbol}")
        return self.asset_detail['asset']

    def get_ath(self):
        return self.asset['allTimeHigh']

    def get_current_price(self):
        return self.asset['price']

    def get_24hour_volume(self):
        return self.asset['volume']
        
        

def main():
    apikey = config['apikeys']['cryptoapi']
    coin = Coin(apikey, 'ETH')
    print(coin.get_ath(), coin.get_current_price(), coin.get_24hour_volume()) 



if __name__ == "__main__":
    try:
        main()
    except:
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)


