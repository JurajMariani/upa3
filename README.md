# UPA Project No. 3

This is a web scraping demonstration projcet for UPA - Data Storage and Preparation, BUT - Brno University of Technology, Faculty of Infromation Technology.

## Table of Contents

- [Overview](#overview)
- [Team](#team)
- [Domain selection](#domain-selection)
- [Scraping](#scraping)
  - [TSV](#tsv)
  - [Prerequisites](#prerequisites)
  - [Usage](#usage)
- [Acknowledgements](#acknowledgements)

## Overview

Provide a brief overview of your project. Mention its purpose, key features, and any other relevant information.

## Team

Our team - *tUPAc* consists of three members:

- **Bc. Filip Bučko**, *xbucko05*, [xbucko05@stud.fit.vutbr.cz](mailto:xbucko05@stud.fit.vutbr.cz)
- **Bc. Juraj Mariani**, *xmaria03*, [xmaria03@stud.fit.vutbr.cz](mailto:xmaria03@stud.fit.vutbr.cz)
- **Bc. Šimon Šmída**, *xsmida03*, [xsmida03@stud.fit.vutbr.cz](mailto:xsmida03@stud.fit.vutbr.cz)

## Domain selection

We picked a book selling website [Wordery](https://wordery.com) available through this URL link <https://wordery.com>. This website was selected due to several key reasons.

Firstly, it does not explicitly prohibit web scraping activities in its terms of service, providing a legaly available environment for data extraction. This characteristic allowd our team to gather information from the website without concerns about violating usage policies.

Secondly, Wordery lacks specific protective measures against automated spiders, crawlers, or bots. The absence of such anti-scraping mechanisms simplifies the extraction process, enabling a smoother and more straightforward web scraping experience. This makes Wordery an ideal candidate for collecting data efficiently and without encountering unnecessary obstacles.

## Scraping

To implement the scraper, we utilized Python 3 along with modules that streamline the work with HTTP requests and HTML parsing and traversal.

### TSV

The TSV contains 8 values denoted from left to right:

- **Book URL**
- **Book Title**
- **Price**
- Author/s (comma separated)
- ISBN-13
- Publisher
- Print format (comma separated)
- Language (comma separated)

### Prerequisites

- **Python3.10**
  - requests
  - beautifulsoup4
  - getopt

- Bash (for demo scripts)

### Usage

The script can be executed in this manner:

```bash
python3.10 upa3.py *CLI arguments*
```

List of arguments:

- `-h | -help`
- `-u | --100`
  - download the URLs of (by default) 100 items from specified website
- `-f | --fetch <file>`
  - download and print a TSV to stdout containg products from file specified
- `-v | --verbose`*
  - verbose output to stderr
- `-l | --limit <int>`*
  - number of urls to download and process to TSV
- `-c | --consecutive <int>`*
  - maxmum number of consecutive requests
- `-p | --pause <int>`*
  - pause time (in seconds) to wait after maximum consecutive requests
- `-e | --errcnt <int>`*
  - number of acceptable invalid responces before termination
- `-o | --offset <int>`*
  - scraped webpage page offset

\* = Argument is optional

A demonstraction can be executed as per assignment instructions `run.sh`. The shell script (executing the python script with `-u` argument) downloads at least 100 book URLs starting from page in range 1 to 10 randomized. Those URLs are stored in file `test_urls.txt`. The python script is then executed again to scrape the first 10 URLs for data. Those data are displayed in a TSV format to the STDOUT.

## Acknowledgements

bbb