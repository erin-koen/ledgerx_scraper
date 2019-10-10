import os
import lxml
import json
from selenium import webdriver
from bs4 import BeautifulSoup
from twython import Twython


def ledger_x_daily():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    # navigate to daily page
    driver.get(f'https://data.ledgerx.com/')

    # get the source
    source_overview = driver.page_source

    # make the soup
    soup = BeautifulSoup(source_overview, features="lxml")
    # get the table
    table = soup.find("table")
    # get an array of rows sans header and swaps
    table_rows = table.find_all("tr")[2:]
    trades = []
    for tr in table_rows:
        td = tr.find_all('td')
        row = [i.text for i in td]
        if row[4] != '0':
            trade = {}
            trade['date'] = row[0]
            trade['contract'] = row[1]
            trade['volume'] = int(row[4])
            trade['open_interest'] = int(row[5])
            trade['contract_type'] = row[7]
            trades.append(trade)

    total_contracts = 0
    for trade in trades:
        total_contracts += trade['volume']
    most_traded = trades[0]
    contract = most_traded['contract']
    volume = most_traded['volume']

    line_1 = f'{total_contracts} contracts traded on Ledger X today. \n'
    line_2 = f'{contract} was the most active contract, trading {volume} times.'

    # twitter dets
    # APP_KEY = os.environ.get(TWITTER_APP_KEY)
    # APP_SECRET = os.environ.get(TWITTER_APP_SECRET)
    # OAUTH_TOKEN = os.environ.get(OAUTH_TOKEN)
    # OAUTH_TOKEN_SECRET = os.environ.get(OAUTH_TOKEN_SECRET)
    # twitter = Twython(APP_KEY, APP_SECRET, OATUH_TOKEN, OAUTH_TOKEN_SECRET)

    return line_1 + line_2


print(ledger_x_daily())
