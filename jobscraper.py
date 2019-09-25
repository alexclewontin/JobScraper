import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime as dt
import yaml
import mysql.connector as mdb
import pystache as ps
import scraper

class JobScraper:
    def __init__(self):
        self.opps = []
        with open('sources.yaml', 'r') as f:
            self.src = yaml.full_load(f)
        with open('config.yaml', 'r') as f:
            self.config = yaml.full_load(f)

        self.cnx = mdb.connect(user=self.config['db']['user'], password=self.config['db']['passwd'], database=self.config['db']['db'])
        self.cur = self.cnx.cursor(dictionary=True)
        self.cur.execute('SHOW TABLES')
        tables_raw = self.cur.fetchall()
        tables = []
        for s in tables_raw:
            for i in s.values():
                tables.append(i)
        spec = '(odate DATE, sdate DATE, corp VARCHAR(255), title VARCHAR(255), loc VARCHAR(255), id VARCHAR(255))'
        if 'new' not in tables:
            self.cur.execute('CREATE TABLE new' + spec)
        if 'current' not in tables:
            self.cur.execute('CREATE TABLE current' + spec)
        if 'old' not in tables:
            self.cur.execute('CREATE TABLE old' + spec)

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
            self.cur.execute('UPDATE current SET sdate = %s WHERE corp = %s AND id = %s ', (dt.today().strftime('%Y-%m-%d'), corp, ident))
        self.cnx.commit()

    def send_email(self):
        self.cur.execute('SELECT * FROM new')
        new_opps = self.cur.fetchall()

        self.cur.execute('SELECT * FROM current WHERE sdate != %s', (dt.today().strftime('%Y-%m-%d'),))
        old_opps = self.cur.fetchall()

        if not new_opps and not old_opps:
            print('nothing new')
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

        msg['From'] = self.config['smtp']['user']
        msg['To'] = self.config['recipient']['email']

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(self.config['smtp']['url'], self.config['smtp']['port'], context=context) as server:
            server.login(self.config['smtp']['user'], self.config['smtp']['passwd'])
            server.sendmail(self.config['smtp']['user'], self.config['recipient']['email'], msg.as_string())

        self.cur.execute('INSERT INTO old SELECT * FROM current WHERE sdate != %s', (dt.today().strftime('%Y-%m-%d'),))
        self.cur.execute('DELETE FROM current WHERE sdate != %s', (dt.today().strftime('%Y-%m-%d'),))
        self.cnx.commit()

        self.cur.execute('INSERT INTO current SELECT * FROM new')
        self.cur.execute('DELETE FROM new')
        self.cnx.commit()

    def crawl(self):

        for s in self.src:
            for c in self.src[s]:
                if 'cmd' in c:
                    cmd = c['cmd']
                else:
                    cmd = ''
                if 'fmt' in c:
                    fmt = c['fmt']
                else:
                    fmt = ''
                raw = scraper.scrape(s, c['company'], c['url'], fmt=fmt, cmd=cmd)
                for r in raw:
                    self.opps.append(r)
                for o in self.opps:
                    self.__touch_opp(o['date'], o['company'], o['title'], o['loc'], o['id'])

        print('crawled')

js = JobScraper()
js.crawl()
js.send_email()
