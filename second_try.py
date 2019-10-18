import os
import requests
import time
import json
import sqlite3
from datetime import date
import twitter

APP_KEY = os.environ.get('TWITTER_APP_KEY')
APP_SECRET = os.environ.get('TWITTER_APP_SECRET')
OAUTH_TOKEN = os.environ.get('OAUTH_TOKEN')
OAUTH_TOKEN_SECRET = os.environ.get('OAUTH_TOKEN_SECRET')

api = twitter.Api(consumer_key=APP_KEY,
                  consumer_secret=APP_SECRET,
                  access_token_key=OAUTH_TOKEN,
                  access_token_secret=OAUTH_TOKEN_SECRET)


def get_contracts():
    today = date.today()
    endpoint = f'https://data.ledgerx.com/json/{today}.json'
    response = requests.get(endpoint)
    if response.status_code == 200:
        contracts = response.json()['report_data']
        return contracts
    elif response.status_code == 404:
        return 404


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

    return highest_volume, winners, total_volume


def post_to_twitter(highest_volume, winners, total_volume):
    # TODO: handle the case where there's more than one winner
    length = len(winners)

    most_message = f'The {winners[0]} was the most active contract  on today; {highest_volume} contracts traded. \n'
    total_message = f'{total_volume} options contracts traded in total.'
    message = most_message + '\n' + total_message
    api.PostUpdates(message)


def main():
    # initialize DB
    print('Initializing database connection.')
    conn = sqlite3.connect('contracts.db',
                           detect_types=sqlite3.PARSE_DECLTYPES)

    # intialize cursor
    c = conn.cursor()
    c.execute('DELETE FROM contracts')
    # query ledgerx
    print('Querying ledgerx.')
    contracts = get_contracts()

    # handle 404
    if contracts == 404:
        return "The report has not yet been posted."

    # store contracts
    print('Saving contracts to database.')
    load_contracts_into_db(contracts, conn)

    # pull the correct ones
    print('Querying database for info.')
    [highest_volume,
     winners,
     total_volume] = pull_most_active_contracts_from_db(c)

    # close db connection
    print('Closing database connection.')
    conn.close()

    print('Posting to Twitter.')
    post_to_twitter(highest_volume, winners, total_volume)


main()
