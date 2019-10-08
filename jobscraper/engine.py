"""TODO: add a docstring"""

import pathlib
import smtplib
import ssl
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import mysql.connector as mdb
import pystache as ps
import requests
import yaml
from selenium import common, webdriver

import hooks


class JobScraper:
    """Encapsulates all the methods and data needed by JobScraper"""
    def __init__(self, cfg, src):
        print('Initializing...')
        self.opps = []
        self.cfg = cfg
        self.src = src
        self.cnx = mdb.connect(user=self.cfg['db']['user'], password=self.cfg['db']['passwd'], database=self.cfg['db']['db'])
        self.cur = self.cnx.cursor(dictionary=True)
        self.cur.execute('SHOW TABLES')
        tables = [i for l in self.cur.fetchall() for i in l.values()]
        spec = '''(odate DATE,
                        seen BIT,
                        corp VARCHAR(255),
                        title VARCHAR(255),
                        loc VARCHAR(255),
                        id VARCHAR(255),
                        url VARCHAR(255),
                        status VARCHAR(255))'''
        if 'jobs' not in tables:
            self.cur.execute('CREATE TABLE jobs' + spec)
            self.cur.execute('INSERT INTO jobs VALUES (NULL, 0, NULL, NULL, NULL, \'TRACKER\', NULL, NULL)')
            self.cnx.commit()

        self.cur.execute('SELECT seen FROM jobs WHERE id = \'TRACKER\'')
        seen = self.cur.fetchone()
        if seen['seen'] == 1:
            self.next_seen = 0
        else:
            self.next_seen = 1

        options = webdriver.ChromeOptions()
            #options.binary_location = 'chromedriver'
        options.add_argument('--window-size=1200x800')
        options.add_argument('--headless')

        self.browser = webdriver.Chrome(options=options)
        print("Initialized")

    def __del__(self):
        try:
            self.browser.quit()
        except Exception:
            pass
        self.cnx.close()

    def __touch_opp(self, data):
        stmnt = 'SELECT id FROM jobs WHERE id = %s AND corp = %s'
        args = (data['id'], data['corp'])
        self.cur.execute(stmnt, args)
        result = self.cur.fetchall()
        #self.cur.execute('SELECT id FROM new WHERE id = %s AND corp = %s', (id, corp))
        #result.append(self.cur.fetchall())
        if not result:
            stmnt = 'INSERT INTO jobs VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
            args = (data['date'].strftime('%Y-%m-%d'), self.next_seen, data['corp'], data['title'], data['loc'], data['id'], data['url'], 'new')
            self.cur.execute(stmnt, args)
        else:
            stmnt = 'UPDATE jobs SET seen = %s WHERE corp = %s AND id = %s'
            args = (self.next_seen, data['corp'], data['id'])
            self.cur.execute(stmnt, args)
        self.cnx.commit()

    def send_email(self, text, html):
        """TODO: add docstring"""
        self.cur.execute('SELECT * FROM jobs WHERE status = \'new\' AND corp IN (SELECT * FROM outlets)')
        new_opps = self.cur.fetchall()

        self.cur.execute('SELECT * FROM jobs WHERE status = \'current\' AND seen != %s AND id != \'TRACKER\'', (self.next_seen,))
        old_opps = self.cur.fetchall()

        if not new_opps and not old_opps:
            self.cur.execute('UPDATE jobs SET seen = %s WHERE id = \'TRACKER\' and status = \'current\'', (self.next_seen,))
            self.cur.execute('INSERT INTO outlets(name) SELECT DISTINCT corp FROM jobs WHERE corp NOT IN (SELECT name FROM outlets)')
            self.cur.execute('UPDATE jobs SET status = \'current\' WHERE status = \'new\'')
            self.cnx.commit()
            print('Nothing new, no email sent.')
            return

        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Job updates!'

        html = ps.render(html, {'new': new_opps, 'old': old_opps})
        text = ps.render(text, {'new': new_opps, 'old': old_opps})

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

        self.cur.execute('UPDATE jobs SET status = \'old\' WHERE seen != %s AND id != \'TRACKER\'', (self.next_seen,))
        self.cur.execute('UPDATE jobs SET status = \'current\' WHERE status = \'new\'')
        self.cur.execute('UPDATE jobs SET seen = %s WHERE id = \'TRACKER\'', (self.next_seen,))
        self.cur.execute('INSERT INTO outlets(name) SELECT DISTINCT j.corp FROM jobs j WHERE j.corp NOT IN (SELECT name FROM outlets)')
        self.cnx.commit()

        print('Database updated, email sent')

    def crawl(self):
        """TODO: add docstring"""
        for c in self.src:
            print('Crawling %s...' % c['company'])
            if 'cmd' in c:
                cmd = c['cmd']
            else:
                cmd = ''
            self.__scrape(c['fmt'], c['board'], c['company'], c['url'], cmd=cmd)
        for o in self.opps:
            self.__touch_opp(o)

    def __scrape(self, fmt, board, company, url, cmd=''):
        try:
            if fmt == 'rendered':
                self.browser.implicitly_wait(30)
                self.browser.get(url)
                time.sleep(5)
                self.browser.execute_script(cmd)
                time.sleep(5)
                data = self.browser.execute_script("return document.body.innerHTML")

            elif fmt == 'raw':
                data = requests.get(url)
            else:
                raise ValueError('Format should either be raw or rendered!')

            result = getattr(hooks, 'parse_' + board.lower())(data, company)

            self.opps.extend(result)
        except common.exceptions.TimeoutException:
            self.cur.execute('UPDATE jobs SET seen = %s WHERE corp = %s AND status = \'current\'', (self.next_seen, company))
            print("Request timed out.")

path = pathlib.Path(__file__).absolute().parent.parent / 'config'

with open(path.as_posix() + '/sources.yaml', 'r') as f:
    sources = yaml.full_load(f)
with open(path.as_posix() + '/config.yaml', 'r') as f:
    config = yaml.full_load(f)
with open(path.as_posix() + '/email.txt', 'r') as f:
    tmpl_text = f.read()
with open(path.as_posix() + '/email.html', 'r') as f:
    tmpl_html = f.read()

JS = JobScraper(config, sources)
JS.crawl()
JS.send_email(tmpl_text, tmpl_html)

