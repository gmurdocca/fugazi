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


class Asset:

    """
    A class representing an crypto asset, eg. Bitcoin
    """

    def __init__(self, api_key, symbol, cache_timeout=5):
        self.api_key = api_key
        self.symbol = symbol
        self.asset_file = "./assets.json"
        self.cache_timeout = cache_timeout
        self.asset_detail = None
        self.default_headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key
                }

    @property
    def asset(self):
        return self.get_asset_by_symbol(self.symbol)

    def get_all_assets(self, refresh=False):
        if not refresh and os.path.exists(self.asset_file):
            with open(self.asset_file, "r") as asset_file:
                asset_data = json.load(asset_file) 
                assets = asset_data['assets']
        else:
            timestamp = time.time()
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
            asset_data = {
                    "timestamp": timestamp,
                    "assets": assets
                    }
            with open(self.asset_file, "w") as asset_file:
                asset_file.write(json.dumps(asset_data))
        return assets

    def get_assets_age(self):
        """
        Returns age in seconds of cached assets or None if not cached
        """
        if not os.path.exists(self.asset_file):
            return None
        with open(self.asset_file, "r") as asset_file:
            asset_data = json.load(asset_file) 
            timestamp = asset_data['timestamp']
        return time.time() - timestamp

    def is_fresh(self):
        """
        returns True if asset_detail age < self.cache_timeout
        """
        if self.asset_detail and time.time() - self.asset_detail['timestamp'] < self.cache_timeout:
            return True
        return False

    def get_asset_by_symbol(self, symbol):
        if not self.is_fresh():
            found = False
            assets = self.get_all_assets()
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
    coin = Asset(apikey, 'ETH')
    print(coin.get_ath(), coin.get_current_price(), coin.get_24hour_volume()) 


if __name__ == "__main__":
    try:
        main()
    except:
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)


