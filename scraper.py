#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 17:23:04 2021

@author: podolnik
"""

import json
import requests
import datetime

def get_stock(store_id, item_id, country_code = 'cz', language_code = 'cs'):
    item_id = item_id.replace('.', '')
    
    url = "https://iows.ikea.com/retail/iows/{}/{}/stores/{}/availability/ART/{}".format(
        country_code, language_code, store_id, item_id)
    
    item = requests.get(
         url,
         headers={
             "Accept": "application/vnd.ikea.iows+json;version=1.0",
             "Contract": "37249",
             "Consumer": "MAMMUT",
         },
     )
    return json.loads(item.text)

def get_availabilities(store_ids, item_ids):    
    availabilities = {store_id: {item_id: {'count': 0, 'restock': None} for item_id in item_ids} for store_id in store_ids}
    
    for store_id in store_ids:
        for item_id in item_ids:
            item = get_stock(store_id, item_id)
            count = int(item['StockAvailability']['RetailItemAvailability']['AvailableStock']['$'])
            restock = datetime.datetime.strptime(item['StockAvailability']['RetailItemAvailability']['RestockDateTime']['$'], '%Y-%m-%d') if 'RestockDateTime' in item['StockAvailability']['RetailItemAvailability'] else datetime.datetime.now()
            availabilities[store_id][item_id]['count'] = count
            availabilities[store_id][item_id]['restock'] = restock
    
    return availabilities

def get_summary(availabilities, requirements):
    summary = {store_id: {} for store_id in availabilities}
    for store_id in availabilities:
        for item_id in availabilities[store_id]:
            if availabilities[store_id][item_id]['count'] < requirements[item_id]:
                summary[store_id][item_id] = availabilities[store_id][item_id]['restock']
            
    return summary

def get_item_info(item_id):
    item_id = item_id.replace('.', '')
    url = "https://www.ikea.com/cz/cs/products/{}/{}.json".format(item_id[-3:], item_id)
    
    item = requests.get(
         url,
         headers={
             "Accept": "application/vnd.ikea.iows+json;version=1.0",
             "Contract": "37249",
             "Consumer": "MAMMUT",
         },
     )
    return json.loads(item.text)

def get_item_descriptions(item_ids):
    descriptions = {}
    for item_id in item_ids:
        info = get_item_info(item_id)
        descriptions[item_id] = {
            'name': info['name'],
            'description': info['typeName']
        }
    return descriptions
