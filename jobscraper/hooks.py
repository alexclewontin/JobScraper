"""This module supplies JobScraper with the format and source specific hooks for acquiring data.

All parser hooks shoud take the format of a function named *parse_boardname*, where boardname is the name
of the job board type in all lowercase. The function should take two arguments: the first is the data to be parsed,
in whatever format is appropriate (be it raw HTML, or JSON as a result of an API call), and the second is a string
containing the name of the company. The function should return a list of job opportunities. Each job opportunity is
a dict containing the following keys:
    corp: the company offering the job
    title: the position being offered
    loc: the location of the job
    id: a unique ID If one does not exist, generate it using a hash of the title and loc
    date: the date on which the opportunity was posted (or first seen) The value should be a datetime object
    url: a link to the specific job posting (preferably not the general job board)

The following is a skeleton that can be used to build parser hooks:

def parse_skeleton(data, company):
    '''TODO: add docstring'''
    opps = []
    # some code here
    for r in raw_opps:
        #some more code here

        date = 'convert to a datetime'
        o = {
            'corp' : company,
            'title' : '#find the title',
            'loc' : '#find the location',
            'id' : ' #find the id',
            'date' : date,
            'url' : '#find the url'
        }
        opps.append(o)
    return opps
"""

from datetime import datetime, timedelta
import pathlib

import requests
from dateutil import parser as dp
from bs4 import BeautifulSoup

def fuzzy_loc_match(loc):
    '''TODO: add docstring'''
    if loc == 'Remote':
        return 'Remote'

    path = pathlib.Path(__file__).absolute().parent.parent / 'config'
    with open(path.as_posix() + '/google_api_key', 'r') as f:
        key = f.read()

    endpoint = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s'
    loc = loc.replace('.', '')
    loc = loc.replace(' ', '+')
    endpoint = endpoint % (loc, key)

    response = requests.get(endpoint)
    response = response.json()
    #for r in response['results']:


#fuzzy_loc_match('New York, Washington, D.C., Remote')

def parse_ultipro(data, company):
    '''TODO: add docstring'''
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
            'date' : date,
            'url' : 'https://recruiting.ultipro.com' + r.find(attrs={"data-automation":"job-title"})['href']
        }
        opps.append(o)
    return opps

def parse_greenhouse(data, company):
    '''TODO: add docstring'''
    opps = []
    data = data.json()
    for j in data['jobs']:
        date = dp.parse(j['updated_at'])
        o = {
            'corp' : company,
            'title' : j['title'],
            'loc': j['location']['name'],
            'id' : j['id'],
            'date' : date,
            'url' : j['absolute_url']
        }
        opps.append(o)

    return opps

def parse_applytojob(data, company):
    '''TODO: add docstring'''
    opps = []
    soup = BeautifulSoup(data.text, 'html.parser')
    raw_opps = soup.find_all(class_='list-group-item')
    for r in raw_opps:
        title = r.find(class_='list-group-item-heading').a.string
        loc = r.ul.li.contents[1]
        o = {
            'corp' : company,
            'title' : title,
            'loc' : loc,
            'date' : datetime.today(),
            'url' : r.find(class_='list-group-item-heading').a['href']
        }
        opps.append(o)
    return opps

def parse_workday(data, company):
    '''TODO: add docstring'''
    opps = []
    soup = BeautifulSoup(data, 'html.parser')
    raw_opps = soup.find_all(attrs={'data-automation-id' : 'compositeContainer'})
    for r in raw_opps:
        title = r.find(attrs={'role' : 'link'}).string
        raw = r.find(attrs={'data-automation-id' : 'compositeSubHeaderOne'}).string.split('|')
        raw = [i.strip() for i in raw]
        raw[2] = raw[2].split(' ', 1)[1].split(' ')[0]
        #raw[2] = raw[2].split(' ')[0]
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
            'title' : title,
            'loc' : raw[0],
            'id' : raw[1],
            'date' : date,
            'url' : "about:blank"
        }
        opps.append(o)
    return opps

def parse_slate(data, company):
    '''TODO: add docstring'''
    opps = []

    soup = BeautifulSoup(data.text, 'html.parser')
    soup = soup.find(class_='standalone-page__content')
    raw_opps = soup.find_all('a')
    for r in raw_opps:
        url = r['href']
        r = r.string.split('-')
        if len(r) > 1:
            loc = r[1]
        else:
            loc = "None"
        o = {
            'corp' : company,
            'title' : r[0].strip(),
            'loc' : loc,
            'date' : datetime.today(),
            'url' : url
        }
        opps.append(o)
    return opps
