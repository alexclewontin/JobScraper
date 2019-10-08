"""
All parser hooks shoud take the format of a function named *parse_boardname*, where boardname is the name
of the job board type in all lowercase. The function should take two arguments: the first is the data to be parsed,
in whatever format is appropriate (be it raw HTML, or JSON as a result of an API call), and the second is a string
containing the name of the company. The function should return a list of job opportunities. Each job opportunity is
a dict containing the following keys:
    corp: the company offering the job
    title: the position being offered
    loc: the location of the job
    id: a unique ID representing the job on the board. If one does not exist, generate it using a hash of the title and loc
    date: the date on which the opportunity was posted (or first seen). The value should be a datetime object

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
import hashlib
from datetime import datetime, timedelta
from dateutil import parser as dp
from bs4 import BeautifulSoup

def parse_slate(data, company):
    opps = []

    soup = BeautifulSoup(data.text, 'html.parser')
    soup = soup.find(class_='standalone-page__content')
    raw_opps = soup.find_all('a')
    for r in raw_opps:
        url = r['href']
        m = hashlib.md5()
        m.update(url.encode('utf-8'))
        r = r.string.split('-')
        if len(r) > 1:
            loc = r[1]
        else:
            loc = "None"
        o = {
            'corp' : company,
            'title' : r[0].strip(),
            'loc' : loc,
            'id' : m.hexdigest(),
            'date' : datetime.today(),
            'url' : url
        }
        opps.append(o)
    return opps
