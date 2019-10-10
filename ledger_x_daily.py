import lxml
import json
from selenium import webdriver
from bs4 import BeautifulSoup


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

    table = soup.find("table")
    table_rows = table.find_all("tr")[1:]
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
        if trade['contract_type'] != 'Day ahead swap':
            total_contracts += trade['volume']
    
    return total_contracts


print(ledger_x_daily())
