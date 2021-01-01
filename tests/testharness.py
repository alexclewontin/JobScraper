import time
import yaml
import requests
from selenium import webdriver

import testhooks

src = '''
-
    company: "Boston Dynamics"
    board: "workday"
    url: "https://bostondynamics.wd1.myworkdayjobs.com/Boston_Dynamics/"
    fmt: "rendered"
    cmd: ""

'''
print('Loading sources...')
s = yaml.full_load(src)
for src in s:
    print('Getting %s...' % src['company'])
    if src['fmt'] == 'rendered':
        print('Rendering %s...' % src['company'])
        options = webdriver.ChromeOptions()
        #options.binary_location = 'chromedriver'
        options.add_argument('--window-size=1200x800')
        options.add_argument('--headless')

        browser = webdriver.Chrome(options=options)

        browser.implicitly_wait(30)
        browser.get(src['url'])
        time.sleep(5)
        browser.execute_script(src['cmd'])
        time.sleep(5)
        data = browser.execute_script("return document.body.innerHTML")

        browser.quit()

        print('Rendered %s.' % src['company'])

    elif src['fmt'] == 'raw':
        data = requests.get(src['url'])
    else:
        raise ValueError('Format should either be raw or rendered!')
    print('Parsing %s...' % src['company'])
    result = getattr(testhooks, 'parse_' + src['board'].lower())(data, src['company'], src['url'])

    print(result)
