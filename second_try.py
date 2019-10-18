import requests
import time
import json
import sqlite3
from datetime import date

# https://data.ledgerx.com/json/2019-10-17.json

count = 0


def get_contracts():
    today = '2019-10-17'
    endpoint = f'https://data.ledgerx.com/json/{today}.json'
    raw_data = requests.get(endpoint).json()
    contracts = raw_data['report_data']
    return contracts


def load_contracts_into_db(contracts, conn):

    for contract in contracts:

        # for all contracts that traded
        if contract['volume'] != 0:
            # parse object to insert into DB
            descrip_arr = contract['contract_label'].split(' ')
            today = date.today()
            expiry = descrip_arr[1]
            strike = None if len(descrip_arr) < 4 else descrip_arr[3]
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
                         (today,
                          expiry,
                          strike,
                          contract_type,
                          option_type,
                          volume,
                          vwap))
    conn.commit()


def pull_most_active_contracts_from_db(c):
    today = date.today()
    active_contracts = c.execute(
        '''SELECT volume, expiry, strike, option_type FROM contracts
        WHERE date=? and contract_type=? ORDER BY volume''',
        (today, 'options_contract'))
    contracts = []
    for row in active_contracts:
        contracts.append(row)
    highest_volume = None
    total_volume = 0
    for contract in contracts:
        if highest_volume is None:
            highest_volume = contract[0]
            total_volume += contract[0]
        elif contract[0] > highest_volume:
            highest_volume = contract[0]
            total_volume += contract[0]
        else:
            total_volume += contract[0]
    winners = []
    for contract in contracts:
        if contract[0] == highest_volume:
            expiry = contract[1]
            winners.append(
                f'{contract[2]} Bitcoin {contract[3]} expiring {expiry}')

    print(highest_volume, winners, total_volume)




def main():
    # initialize DB
    conn = sqlite3.connect('contracts.db',
                           detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("DELETE FROM contracts")
    # c.execute('''CREATE TABLE contracts
    #                         (id integer primary key,
    #                         date date,
    #                         expiry date,
    #                         strike text,
    #                         contract_type text,
    #                         option_type text,
    #                         volume integer,
    #                         vwap real)''')

    # query ledgerx
    contracts = get_contracts()

    # store contracts
    load_contracts_into_db(contracts, conn)

    # pull the correct ones
    pull_most_active_contracts_from_db(c)



    # close db connection
    conn.close()


main()
