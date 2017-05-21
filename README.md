# May 2017, Sale of Balance flats from HDB
This Python application is for scraping information off HDB's website.

Comprises of 3 components:
* Scraper
* Data
* Visualiser

## Installation
You'll need Python 3 (64 bit) to run. Install *pip* into python, then `pip install -r requirements.txt` to get the required packages. You may wish to use *virtualenv* to manage your Python environment.

# Scraper
Location: `\src\scraper`

Because the HDB SBF site goes down when the application period is over, we scrape the data and perform offline data analysis instead of fetching it on-the-fly.

Content is retrieved using GET (*i.e. URL*) requests. Pleasantly, HDB uses minimal JavaScript and has a well-defined, though *unofficial* API. If not for the former, we'd have to use a heavyweight scraper to parse the JavaScript instead.

Data is extracted into the `\data` folder. There is the JSON version in `\data\json`, and the Python pickled/serialised version in `\data\pickle`.

## Technology
* Python 3 (64 bit)
* Requests
* BeautifulSoup4 w/ html5lib parser

> Requests and BS4 is much faster than using Selenium. Scrapy configuration is a little unwieldy.

> html5lib parser is lenient; it handles invalid HTML better.

# Data
As mentioned, we have the JSON versions in `\data\json`, and the pickled version in `\data\pickle`. In addition, we also imported the data into a SQLite database in `\data\sqlite`.

We recommend using *SQLite* if you are doing data analysis. But if you wish to deploy the data on a different storage engine (e.g. traditional RDBMS, Lucene, or Document NoSQL), import the raw data using *pickle* (Python) or *JSON*.

## Data Scraped
* Estate
* Street Address
* Lat-long<sup>#</sup>
* Block No.
* Flat Category
* Lease left<sup>#</sup>
* Probable Completion Date<sup>^</sup>
* Delivery Possession Date<sup>^</sup>
* Lease Commencement Date<sup>^</sup>
* Ethnic Quota (Malay, Chinese, Indian/Others)
* Apartment No.
* Is Repurchased
* Gross Area
* Est. Price wrt Lease Term

<sup><sup>#</sup>SQLite only</sup>

<sup><sup>^</sup>PCD is HDB's estimated date of completion. DPD is HDB's delivery deadline. LCD is mostly for repurchased flats. PCD < DPD < LCD.</sup>

# Visualiser
Location: `\src\visualiser`

## Technology
* Python 3 (64 bit)
* SQLite
