"""
changes
    * rename "searchAreaByZip" -> "getZpidByZip"
    * rename "searchAreaByCityState" -> "getZpidByCityState"
    * TODO: use multithreading to add searched properties to the queue
"""

import os, sys
import pyjsonrpc
import json
import re
import time

from bson.json_util import dumps

# import common package in parent dir
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import mongodb_client

SERVER_HOST = 'localhost'
SERVER_PORT = 4040

PROPERTY_TABLE_NAME = 'property'


def searchArea(text):
    zpids = [] # why zpids???
    if text.isdigit():
        zpids = searchAreaByZip(text)
    else:
        city = text.split(',')[0].strip()
        state = text.split(', ')[1].strip()
        zpids = searchAreaByCityState(city, state)
    print "zpids: ", zpids

    res = []
    update_list = []
    db = mongodb_client.getDB()
    for zpid in zpids:
        record = db[PROPERTY_TABLE_NAME].find_one({'zpid': zpid})
        if record != None:
            res.append(record)
        else:
            property_detail = getDetailsByZpid(zpid, False)
            res.append(property_detail)
            update_list.append(property_detail)

    res = []
    db = mongodb_client.getDB()
    if query.isdigit():
        res = db[PROPERTY_TABLE_NAME].find({'zipcode': query})
        res = json.loads(dumps(res)) # BSON -> string -> JSON
    else:

        city, state = query_split[0].strip(), query_split[1].strip()
        # use regexp to do case-insensitive search
        res = db[PROPERTY_TABLE_NAME].find({'city': re.compile(city, re.IGNORECASE),
                                            'state': res.compile(state, re.IGNORECASE)})
        res = json.loads(dumps(res))
    return res

"""Search properties by zip code"""
def searchAreaByZipcode(zipcode):
    print "searchAreaByZip() gets called with zipcode=[%s]" % str(zipcode)
    properties = findProperyByZipcode(zipcode) #rename
    if len(properties) == 0:
        zpids = zillow_web_scraper_client.get_zpid_by_zipcode() #rename
        for zpid in zpids:
            property_detail = zillow_web_scraper_client.get_property_by_zpid(zpid)
            properties.append(property_detail)

    return properties

"""Find property by zipcode"""
def findProperyByZipcode(zipcode):
    db = mongodb_client.getDB()
    properties = list(db[PROPERTY_TABLE_NAME].find({'zipcode': zipcode, 'is_for_sale': True}))
    return properties

"""Find property by city state"""
def findProperyByCityState(city, state):
    db = mongodb_client.getDB()
    properties = list(db[PROPERTY_TABLE_NAME].find({'city': city, 'state': state, 'is_for_sale': True}))
    return properties

"""Update doc in db"""
def storeUpdates(properties):
    print "updating properties in db after searching..."
    db = mongodb_client.getDB()
    for perperty_detail in properties:
        zpid = property_detail['zpid']
        property_detail['last_update'] = time.time()
        db[PROPERTY_TABLE_NAME].replace_one({'zpid': zpid}, property_detail, upsert=True)