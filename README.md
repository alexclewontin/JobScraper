# JobScraper: an extensible webscraping engine for jobseeking

JobScraper is a webscraping engine that crawls across jobboards and keeps a record of their contents,
sending email notifications when it finds new listings, or notices listings have gone away.

## Dependencies

JobScraper uses an assortment of packages available through pip (noted in the `Pipfile`). It also requires
a chromedriver executable, and an installation of MySQL, or MariaDB.

## Installation and Setup

Coming soon.

Most elements should be system-independent. I use a cron job to regularly run it. Because of variations across systems, and users desires for how frequently it runs, this has been left as an exercise for the reader.

## Configuration

An empty `config.yaml` file is included in the repository. The fields should be fairly self-explanatory. The email templates are included as `email.html` and `email.txt`. They should be trivial to customize.

A list of journalism-related sources is included as `sources.yaml` as well. Adding additional sources that utilize an already implemented format should be trivial.

Part of the power of JobScraper is that adding new formats to parse should also be trivial. Simply define a new function in `hooks.py` of the format `parse_{FORMAT}(data, company)` where `company` is a string containing the name of the company, and `data` is the raw text of the html response (set the key `fmt` to `rendered` in `sources.yaml` if the javascript should be rendered.) The function should return a list of dict objects, each containing the following kvps:

```
            'corp' : 'the company', as a string
            'title' : 'the title of the position', as a string
            'loc' : 'the location of the position', as a string
            'id' : 'the position id', as a string (if this does not exist, use an md5 hash of the name and the company)
            'date' : the date of the posting, as a datetime object 
            'url' : 'the url of the posting', as a string
```
