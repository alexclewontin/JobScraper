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
import hashlib

from dateutil import parser as dp
from bs4 import BeautifulSoup

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
            'date' : date,
            'url' : 'https://recruiting.ultipro.com' + r.find(attrs={"data-automation":"job-title"})['href']
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
            'date' : date,
            'url' : j['absolute_url']
        }
        opps.append(o)

    return opps

def parse_applytojob(data, company):
    opps = []
    soup = BeautifulSoup(data.text, 'html.parser')
    raw_opps = soup.find_all(class_='list-group-item')
    for r in raw_opps:
        title = r.find(class_='list-group-item-heading').a.string
        loc = r.ul.li.contents[1]
        m = hashlib.md5()
        m.update(title.encode('utf-8'))
        m.update(loc.encode('utf-8'))
        o = {
            'corp' : company,
            'title' : title,
            'loc' : loc,
            'id' : m.hexdigest(),
            'date' : datetime.today(),
            'url' : r.find(class_='list-group-item-heading').a['href']
        }
        opps.append(o)
    return opps