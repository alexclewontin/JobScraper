"""TODO: add a docstring"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime as dt
import yaml
import mysql.connector as mdb
import pystache as ps

import hooks

class JobScraper:
    """Encapsulates all the methods and data needed by JobScraper"""
    def __init__(self):
        self.opps = []
        with open('sources.yaml', 'r') as f:
            self.src = yaml.full_load(f)
        with open('config.yaml', 'r') as f:
            self.cfg = yaml.full_load(f)

        self.cnx = mdb.connect(user=self.cfg['db']['user'], password=self.cfg['db']['passwd'], database=self.cfg['db']['db'])
        self.cur = self.cnx.cursor(dictionary=True)
        self.cur.execute('SHOW TABLES')
        tables_raw = self.cur.fetchall()
        tables = []
        for s in tables_raw:
            for i in s.values():
                tables.append(i)
        self.spec = '''(odate DATE,
                        sdate DATE,
                        corp VARCHAR(255),
                        title VARCHAR(255),
                        loc VARCHAR(255),
                        id VARCHAR(255))'''
        if 'new' not in tables:
            self.cur.execute('CREATE TABLE new' + self.spec)
        if 'current' not in tables:
            self.cur.execute('CREATE TABLE current' + self.spec)
        if 'old' not in tables:
            self.cur.execute('CREATE TABLE old' + self.spec)

        self.cnx.commit()

    def __touch_opp(self, date, corp, title, loc, ident):
        self.cur.execute('SELECT id FROM current WHERE id = %s AND corp = %s', (ident, corp))
        result = self.cur.fetchall()
        #self.cur.execute('SELECT id FROM new WHERE id = %s AND corp = %s', (ident, corp))
        #result.append(self.cur.fetchall())
        if not result:
            stmnt = 'INSERT INTO new VALUES (%s, %s, %s, %s, %s, %s);'
            data = (date.strftime('%Y-%m-%d'), dt.today().strftime('%Y-%m-%d'), corp, title, loc, ident)
            self.cur.execute(stmnt, data)
        else:
            stmnt = 'UPDATE current SET sdate = %s WHERE corp = %s AND id = %s; '
            data = (dt.today().strftime('%Y-%m-%d'), corp, ident)
            self.cur.execute(stmnt, data)
        self.cnx.commit()

    def send_email(self):
        self.cur.execute('SELECT * FROM new')
        new_opps = self.cur.fetchall()

        self.cur.execute('SELECT * FROM current WHERE sdate != %s', (dt.today().strftime('%Y-%m-%d'),))
        old_opps = self.cur.fetchall()

        if not new_opps and not old_opps:
            return

        msg = MIMEMultipart('alternative')
        msg['Subject'] = ''

        with open('email.txt', 'r') as f:
            text = f.read()

        with open('email.html', 'r') as f:
            html = f.read()

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

        self.cur.execute('INSERT INTO old SELECT * FROM current WHERE sdate != %s', (dt.today().strftime('%Y-%m-%d'),))
        self.cur.execute('DELETE FROM current WHERE sdate != %s', (dt.today().strftime('%Y-%m-%d'),))
        self.cnx.commit()

        self.cur.execute('INSERT INTO current SELECT * FROM new')
        self.cur.execute('DELETE FROM new')
        self.cnx.commit()

    def crawl(self):

        for b in self.src:
            for c in self.src[b]:
                if 'cmd' in c:
                    cmd = c['cmd']
                else:
                    cmd = ''
                if 'fmt' in c:
                    fmt = c['fmt']
                else:
                    fmt = ''
                self.__scrape(fmt, b, c['company'], c['url'], cmd=cmd)
        for o in self.opps:
            self.__touch_opp(o['date'], o['company'], o['title'], o['loc'], o['id'])

    def __scrape(self, fmt, board, company, url, cmd=''):
        data = getattr(hooks, 'get_' + fmt.lower())(url, cmd)
        result = getattr(hooks, 'parse_' + board.lower())(data, company)
        self.opps.append(result)




JS = JobScraper()
JS.crawl()
JS.send_email()
