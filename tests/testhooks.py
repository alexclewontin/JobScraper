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

def parse_workday(data, company):
    opps = []
    soup = BeautifulSoup(data, 'html.parser')
    raw_opps = soup.find_all(attrs={'data-automation-id' : 'compositeContainer'})
    for r in raw_opps:
        print(r)
        title = r.find(attrs={'role' : 'link'}).string #.split('|')
        print(title)
        raw = r.find(attrs={'data-automation-id' : 'compositeSubHeaderOne'}).string
        print(raw)
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
            'title' : title,
            'loc' : raw[0],
            'id' : raw[1],
            'date' : date,
            'url' : 
        }
        opps.append(o)
    return opps

"""


"""