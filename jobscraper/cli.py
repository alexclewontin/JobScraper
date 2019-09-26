import pathlib
import yaml
import engine as js


path = pathlib.Path(__file__).parent.parent / 'config'
path = path.absolute()

with open(path.as_posix() + '/sources.yaml', 'r') as f:
    src = yaml.full_load(f)
with open(path.as_posix() + '/config.yaml', 'r') as f:
    cfg = yaml.full_load(f)

JS = js.JobScraper(cfg, src)
JS.crawl()
JS.send_email()