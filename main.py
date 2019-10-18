import os
import lxml
import json
import twitter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def ledger_x_daily(request):

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    caps = {'browserName': 'chrome'}
    driver = webdriver.Chrome()

    # navigate to daily page
    driver.get(f'https://data.ledgerx.com/')
    # print('driver initialized')
    # try:
    #     element = WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.CLASS_NAME, "App-table"))
    #     )
    # finally:
    #     print('could not find the table')
    #     driver.quit()
    #     return

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

    line_1 = f'{total_contracts} contracts traded on @ledgerx today. \n'
    line_2 = f'{contract} was the most active, with {volume} contracts trading.'
    message = line_1 + line_2
    print(message)
    APP_KEY = os.environ.get('TWITTER_APP_KEY')
    APP_SECRET = os.environ.get('TWITTER_APP_SECRET')
    OAUTH_TOKEN = os.environ.get('OAUTH_TOKEN')
    OAUTH_TOKEN_SECRET = os.environ.get('OAUTH_TOKEN_SECRET')

    api = twitter.Api(consumer_key=APP_KEY,
                      consumer_secret=APP_SECRET,
                      access_token_key=OAUTH_TOKEN,
                      access_token_secret=OAUTH_TOKEN_SECRET)

    api.PostUpdates(message)
    return'Post Successful'


print(ledger_x_daily('t'))