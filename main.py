#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" Leroy Merlin Price Finder """

import sys
import csv
import requests
from multiprocessing import Pool


def headers() -> dict:
    return {
        'Application-Version': '7.14.2',
        'X-ClientApiKey': 'uogU1bPWRlxuoafYaFswiGfHo8UsWGPe',
        'Operating-System': 'ios',
        'Accept': 'application/json',
        'Accept-Language': 'en',
        'X-BU-Code': 'LMFR',
        'User-Agent': 'Leroy Merlin/7.14.2 (com.keyneosoft.leroymerlin; build:1049; iOS 15.4.1) Alamofire/5.4.4'
    }


def list_stores(headers) -> list:
    endpoint = 'https://api.leroymerlin.fr/backend-amgp-lmfr/v3/stores/api/v1/stores?countryISO=FR'
    r = requests.get(url=endpoint, headers=headers)

    if r.status_code == 200:
        stores = list(map(lambda x: x.get('id'), r.json()))
        return stores if len(stores) else []

    return []


def find_price(storeId, productId):
    endpoint = f'https://api.leroymerlin.fr/backend-amgp-lmfr/v3/product-details/api/v1/products/{productId}'
    parameters = {'storeId': storeId}
    r = requests.get(url=endpoint, params=parameters, headers=headers())

    output = []

    if r.status_code == 200:
        results = r.json()
        if results.get('offers'):
            try:
                price = results.get('offers').get('items')[0].get(
                    'pricing').get('displayPrice').get('amount')
                store = results.get('offers').get('items')[0].get(
                    'availabilityStore').get('store').get('name')
                output = [price, store, storeId, productId]
            except:
                pass

    return output


if __name__ == '__main__':
    productId = None
    if len(sys.argv) > 1:
        productId = sys.argv[1]

    if productId:
        stores = list_stores(headers())

        with Pool(10) as p:
            rows = p.starmap(find_price, zip(
                stores, [productId for i in range(len(stores))]))

        # Remove empty
        rows = [t for t in rows if t]
        # Sort by price
        rows = sorted(rows, key=lambda row: row[0])

        print(f"✅: {rows[0] if rows else None}")
        print(f"❌: {rows[-1] if rows else None}")

        with open(f'./{productId}.csv', 'w', encoding='UTF8') as f:
            writer = csv.writer(f)

            # write header
            writer.writerow(["price", "store", "id", "item"])

            # write rows
            writer.writerows(rows)
