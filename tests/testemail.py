import pathlib
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import sqlite3 as db
import pystache as ps
import yaml
import premailer


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class JobScraperEmailTest:
    """Encapsulates all the methods and data needed by JobScraper"""
    
    def __init__(self, cfg, src):
        print('Initializing...')
                #options.binary_location = 'chromedriver'
        self.opps = []
        self.cfg = cfg
        self.src = src
        # self.cnx = mdb.connect(user=self.cfg['db']['user'], password=self.cfg['db']['passwd'], database=self.cfg['db']['db'])
        self.cnx = db.connect("jobscraper.db")
        self.cnx.row_factory = dict_factory
        self.cur = self.cnx.cursor()
        self.cur.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';")
        names = self.cur.fetchall()
        tables = [d['name'] for d in names]

        if 'jobs' not in tables:
            spec = '''(odate DATE,
                        seen BIT,
                        corp VARCHAR(255),
                        title VARCHAR(255),
                        loc VARCHAR(255),
                        id VARCHAR(255),
                        url VARCHAR(255),
                        status VARCHAR(255))'''
            self.cur.execute('CREATE TABLE jobs' + spec)
            self.cur.execute('INSERT INTO jobs VALUES (NULL, 0, NULL, NULL, NULL, \'TRACKER\', NULL, NULL)')
            self.cnx.commit()
        if 'outlets' not in tables:
            spec = '''(name VARCHAR(255))'''
            self.cur.execute('CREATE TABLE outlets' + spec)
            self.cnx.commit()

        self.cur.execute('SELECT seen FROM jobs WHERE id = \'TRACKER\'')
        seen = self.cur.fetchone()
        if seen['seen'] == 1:
            self.next_seen = 0
        else:
            self.next_seen = 1
    def __del__(self):
        try:
            self.cnx.close()
        except Exception:
            pass


    def send_email(self, text, html):
        """TODO: add docstring"""
        self.cur.execute('SELECT * FROM jobs WHERE id != \'TRACKER\'')
        new_opps = self.cur.fetchall()
        self.cur.execute('SELECT * FROM jobs WHERE id != \'TRACKER\'')
        old_opps = self.cur.fetchall()


        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Job updates!'

        html = ps.render(html, {'new': new_opps, 'old': old_opps})
        text = ps.render(text, {'new': new_opps, 'old': old_opps})
        
        html = premailer.transform(html)

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        msg.attach(part1)
        msg.attach(part2)

        msg['From'] = self.cfg['smtp']['user']
        msg['To'] = self.cfg['recipient']['email']
        
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(self.cfg['smtp']['url'], self.cfg['smtp']['port'], context=context) as server:
            server.login(self.cfg['smtp']['user'], self.cfg['smtp']['passwd'])
            server.sendmail(self.cfg['smtp']['user'], self.cfg['recipient']['email'], msg.as_string())

        print('Database updated, email sent')


path = pathlib.Path(__file__).absolute().parent.parent / 'config'

with open(path.as_posix() + '/sources.yaml', 'r') as f:
    sources = yaml.full_load(f)
with open(path.as_posix() + '/config.yaml', 'r') as f:
    config = yaml.full_load(f)
with open(path.as_posix() + '/email.txt', 'r') as f:
    tmpl_text = f.read()
with open(path.as_posix() + '/email.html', 'r') as f:
    tmpl_html = f.read()

JS = JobScraperEmailTest(config, sources)
JS.send_email(tmpl_text, tmpl_html)
