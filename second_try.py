import requests
import time
import json
import sqlite3
from datetime import date

# https://data.ledgerx.com/json/2019-10-17.json

count = 0


def get_contracts():
    today = date.today()
    endpoint = f'https://data.ledgerx.com/json/{today}.json'
    raw_data = requests.get(endpoint).json()
    contracts = raw_data['report_data']
    return contracts


def load_contracts_into_db(contracts):
    conn = sqlite3.connect('contracts.db', detect_types=PARSE_DECLTYPES)
    # c = conn.cursor()

    for contract in contracts:

        # for all contracts that traded
        if contract['volume'] != 0:
            # parse object to insert into DB
            descrip_arr = contract['contract_label'].split(' ')
            date = date.today()
            expiry = descrip_arr[0]
            strike = descrip_arr[2]
            contract_type = contract['contract_type']
            option_type = None
            if contract_type == 'options_contract':
                if contract['contract_is_call']:
                    option_type = 'call'
                else:
                    option_type = 'put'
            vwap = int(contract['vwap'])
            volume = contract['volume']
            conn.execute('''INSERT INTO contracts(date,
                                                expiry,
                                                strike,
                                                contract_type,
                                                option_type,
                                                volume,
                                                vwap) values(?,?,?,?,?,?,?)''',
                         (date,
                          expiry,
                          strike,
                          contract_type,
                          option_type,
                          vwap,
                          volume))


'''
{
    'contract_id': 21466146, 
    'contract_label': '2019-10-17 Next-Day BTC', 
    'open_interest': 1, 
    'contract_type': 'day_ahead_swap', 
    'last_ask': 806475, 
    'last_bid': 804600, 
    'vwap': 796000.0, 
    'volume': 1
}

{
    'contract_id': 21467086, 
    'contract_label': 'BTC 2019-10-17 Put $7,800.00',
    'open_interest': 0,
    'contract_type': 'options_contract',
    'last_ask': 3000,
    'last_bid': 25,
    'vwap': 0,
    'volume': 0,
    'contract_is_call': False
}
'''
