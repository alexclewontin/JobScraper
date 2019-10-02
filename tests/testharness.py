import time
import yaml
import requests
from selenium import webdriver

import testhooks

src = '''
-
    company: "The New York Times"
    board: "workday"
    url: "https://nytimes.wd5.myworkdayjobs.com/news"
    fmt: "rendered"
    cmd: ""

'''

s = yaml.full_load(src)
for src in s:
    if src['fmt'] == 'rendered':
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

    elif src['fmt'] == 'raw':
        data = requests.get(src['url'])
    else:
        raise ValueError('Format should either be raw or rendered!')
    result = getattr(testhooks, 'parse_' + src['board'].lower())(data, src['company'])

    print(result)
