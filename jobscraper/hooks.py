"""This module supplies JobScraper with the format and source specific hooks for acquiring data."""

import time
from datetime import datetime, timedelta
import requests
from dateutil import parser as dp
from bs4 import BeautifulSoup
from selenium import webdriver


def get_raw(url, cmd):
    options = webdriver.ChromeOptions()
    #options.binary_location = 'chromedriver'
    options.add_argument('--window-size=1200x800')
    options.add_argument('--headless')

    browser = webdriver.Chrome(options=options)

    browser.implicitly_wait(30)
    browser.get(url)
    time.sleep(5)
    browser.execute_script(cmd)
    time.sleep(5)
    raw = browser.execute_script("return document.body.innerHTML")

    browser.quit()

    return raw

def get_json(url, cmd):
    json = requests.get(url)
    return json

def parse_ultipro(data, company):
    opps = []
    soup = BeautifulSoup(data, 'html.parser')
    raw_opps = soup.find_all(class_='opportunity')
    for r in raw_opps:
        date = r.find(attrs={"data-automation":"opportunity-posted-date"}).string
        if date == 'Today':
            date = datetime.today()
        else:
            date = datetime.strptime(date, '%b %d, %Y')
        o = {
            'corp' : company,
            'title' : r.find(attrs={"data-automation":"job-title"}).string,
            'loc' : r.find(attrs={"data-automation":"city-state-zip-country-label"}).string,
            'id' : r.find(attrs={"data-bind":"text: RequisitionNumber()"}).string,
            'date' : date
        }
        opps.append(o)
    return opps

def parse_workday(data, company):
    opps = []
    soup = BeautifulSoup(data, 'html.parser')
    raw_opps = soup.find_all(class_='WPYF')
    for r in raw_opps:
        raw = r.find(class_='WD0F').string.split('|')
        raw = [i.strip() for i in raw]
        raw[2] = raw[2].split(' ', 1)[1]
        raw[2] = raw[2].split(' ')[0]
        if raw[2] == 'Today':
            date = datetime.today().strftime('%Y-%m-%d')
        elif raw[2] == 'Yesterday':
            date = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
        elif raw[2] == '30+':
            date = None
        else:
            date = datetime.strftime(datetime.now() - timedelta(int(raw[2])), '%Y-%m-%d')
        o = {
            'corp' : company,
            'title' : r.find(class_='WA0O').string,
            'loc' : raw[0],
            'id' : raw[1],
            'date' : date
        }
        opps.append(o)
    return opps

def parse_greenhouse(data, company):
    opps = []
    data = data.json()
    for j in data['jobs']:
        date = dp.parse(j['updated_at'])
        o = {
            'corp' : company,
            'title' : j['title'],
            'loc': j['location']['name'],
            'id' : j['id'],
            'date' : date
        }
        opps.append(o)

    return opps
