import pathlib
import yaml
import engine as js

path = pathlib.Path(__file__).absolute().parent.parent / 'config'

with open(path.as_posix() + '/sources.yaml', 'r') as f:
    src = yaml.full_load(f)
with open(path.as_posix() + '/config.yaml', 'r') as f:
    cfg = yaml.full_load(f)
with open(path.as_posix() + '/email.txt', 'r') as f:
    tmpl_text = f.read()
with open(path.as_posix() + '/email.html', 'r') as f:
    tmpl_html = f.read()

JS = js.JobScraper(cfg, src)
JS.crawl()
JS.send_email(tmpl_text, tmpl_html)
