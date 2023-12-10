import getopt
import requests
from bs4 import BeautifulSoup
import sys
import time

def argparse(argv) -> tuple[bool, bool, str, int]:
    """
    Accepting parameters:
        - h / help
        - u / 100 = download the URLs of (by default) 100 items from specified website
        - v / verbose = verbose output to stderr
        - f / fetch <file> = download and print a TSV to stdout containg products from file specified
        - l / limit <int> = number of urls to download and process to TSV
        - c / consecutive <int> = maxmum number of consecutive requests
        - p / pause <int> = pause time (in seconds) to wait after maximum consecutive requests
        - e / errcnt <int> = number of acceptable invalid responces before termination
        - o / offset <int> = scraped webpage page offset
    """
    urlFile = ""
    hundredURLs = False
    fetchProducts = False
    limit = 100
    global maxConsecutiveReqs
    global sleepPeriodAfterReqs
    global errorReqs
    global pageRef
    global verbose

    try:
        opts, _ = getopt.getopt(argv, "huvf:l:c:p:e:o:", ["help", "100", "verbose", "fetch=", "limit=", "consecutive=", "pause=", "errcnt=", "offset="])
    except getopt.GetoptError:
        print("upa3.py -u | -f <urlfile> [-v] [-l limit] [-c maxConsecutiveRequests] [-p pausePeriod] [-e retryTimes] [-o paginationOffset]")
        sys.exit(1)

    for opt, arg in opts:
        if opt in ("-u", "--100"):
            hundredURLs = True
        elif opt in ("-f", "--fetch"):
            if not arg:
                print("Missing url file for fetch", file=sys.stderr)
                sys.exit(1)
            fetchProducts = True
            urlFile = arg
        elif opt in ("-l", "-c", "-p", "-e", "-o", "--limit", "--consecutive", "--pause", "--errcnt", "--offset"):
            num = 0
            try:
                num = int(arg)

                if opt in ("-l", "--limit"):
                    limit = num
                elif opt in ("-c", "--consecutive"):
                    maxConsecutiveReqs = num
                elif opt in ("-p", "--pause"):
                    sleepPeriodAfterReqs = num
                elif opt in ("-e", "--errcnt"):
                    errorReqs = num
                elif opt in ("-o", "--offset"):
                    pageRef = num
            except Exception:
                print(f"Can't convert parameter {opt} value to integer. Using default value instead.")
        
        elif opt in ("v", "verbose"):
            verbose = True

        else:
            print("upa3.py -u | -f <urlfile> [-v] [-l limit] [-c maxConsecutiveRequests] [-p pausePeriod] [-e retryTimes] [-o paginationOffset]")
            sys.exit(0)

    if fetchProducts and hundredURLs:
        print("Only one parameter can be present at the same time\n", file=sys.stderr)

    return (hundredURLs, fetchProducts, urlFile, limit)

# v Global Variables
pageRef = 1
baseURL = "https://wordery.com"
url = baseURL + f"/science-fiction-books-FL?resultsPerPage=20&page={pageRef}&leadTime[]=any"
maxConsecutiveReqs = 10
sleepPeriodAfterReqs = 3 # in seconds
reqCounter = 0
errorReqs = 0
verbose = False
# ^ Global Variables

def downloadData(downloadURL: str) -> BeautifulSoup:
    global reqCounter
    global errorReqs
    try:
        if verbose:
            print("URL: " + downloadURL, file=sys.stderr)
            print("Began downloading...", file=sys.stderr)

        if reqCounter >= maxConsecutiveReqs:
            # In order not to overload the server, after maxConsecutiveReqs requests
            # the script is instructed to wait for a breaf amount of time
            # (determined by sleepPeriodAfterReqs).
            # The counter is than reset
            time.sleep(sleepPeriodAfterReqs)
            reqCounter = 0

        resp = requests.get(downloadURL)
        resp.raise_for_status()
        reqCounter += 1
        if verbose:
            print(f"Download finished with code {resp.status_code}", file=sys.stderr)

        return BeautifulSoup(resp.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error while downloading data:\n{e}", file=sys.stderr)
        errorReqs += 1
        return None


def getURLs(limit: int = 100) -> list[str]:
    # Using global variables
    global pageRef
    global url
    urlList = []

    while len(urlList) < limit:
        url = baseURL + f"/science-fiction-books-FL?resultsPerPage=20&page={pageRef}&leadTime[]=any"
        soup = downloadData(url)

        if not soup:
            if errorReqs > 10:
                return urlList
            continue

        # Adjust the url
        pageRef += 1

        # Extracting list items with class="o-book-list__book"
        bookDivs = soup.find_all('li', class_="o-book-list__book")
        for book in bookDivs:
            # For each list item locate an anchor with class "c-book__title"
            anchorElement = book.find('a', class_="c-book__title")
            urlList.append(baseURL + anchorElement['href'])

    return urlList

def getURLsFromFile(file: str, limit: int) -> list[str]:
    urlList = []
    try:
        with open(file, 'r') as f:
            for line in f:
                urlList.append(line.rstrip())
                if len(urlList) >= limit:
                    break

    except Exception as e:
        print(f"Error when accessing given file.\nError msg.: {e}")
    
    return urlList

def fetchTSV(urls: list[str] = []) -> str:
    global reqCounter
    tsv = ""

    for bookURL in urls: 
        soup = downloadData(bookURL)

        if not soup:
            if errorReqs > 10:
                return tsv
            continue

        tsv += bookURL + "\t"

        # Extraction of valuable data
        # 1. Extract name of the product
        titleWhole = soup.find('main').find('h1')
        if not titleWhole:
            tsv += "\t"
        else:
            title = titleWhole.find('strong')
            tsv += title.text + "\t"

        # 2. Extract price of the product
        price = soup.find('strong', class_="u-fs--ex u-t--lh1")
        if not price:
            tsv += "\t"
        else:
            tsv += price.text + "\t"

        # Extracting additional detailes
        productDetes = soup.find('dl', class_='o-dl-inline o-dl-inline--colon')
        productSpecs = productDetes.find_all('dt')
        found = False

        # 3.a Parameter 1/3 - Author
        authors = []
        for spec in productSpecs:  
            if spec.text.lower() == "author":
                found = True
                specDef = spec.find_next_sibling('dd')
                authors.append(specDef.text.strip())
        
        if not found:
            tsv += "\t"
        else:
            for i in range(len(authors)):
                if i == len(authors) - 1:
                    tsv += authors[i] + "\t"
                else:
                    tsv += authors[i] + ","
            found = False

        # 3.b Parameter 2/3 - ISBN-13
        for spec in productSpecs:
            if spec.text.lower() == "isbn-13":
                found = True
                specDef = spec.find_next_sibling('dd')
                tsv += specDef.text.strip() + "\t"
        
        if not found:
            tsv += "\t"
        else:
            found = False
        
        
        # 3.c Parameter 3/3 - Publisher
        for spec in productSpecs:
            if spec.text.lower() == "publisher":
                found = True
                specDef = spec.find_next_sibling('dd')
                tsv += specDef.text.strip() + "\t"
        
        if not found:
            tsv += "\t"
        else:
            found = False

        # 3.d Parameter 4/3 - Format
        for spec in productSpecs:
            if spec.text.lower() == "format":
                found = True
                specDef = spec.find_next_sibling('dd')
                if specDef.text.strip()[-1] == ',':
                    tsv += specDef.text.strip()[:-1] + "\t"
                else:
                    tsv += specDef.text.strip() + "\t"


        if not found:
            tsv += "\t"
        else:
            found = False
            
        # 3.e Parameter 5/3 - Language
        for spec in productSpecs:
            if spec.text.lower() == "language":
                found = True
                specDef = spec.find_next_sibling('dd')
                tsv += specDef.text.strip()

        tsv += "\n"

    return tsv

if __name__ == '__main__':
    tup = argparse(sys.argv[1:])
    if True not in tup:
        print("No option selected\nUsage:\n\tupa3.py -u | -f <urlfile> [-v] [-l limit] [-c maxConsecutiveRequests] [-p pausePeriod] [-e retryTimes] [-o paginationOffset]")
        sys.exit(0)

    if tup[0]:
        urlList = getURLs(tup[-1])
        for url in urlList:
            print(url)

    else:
        if tup[1] and tup[2]:
            urlList = getURLsFromFile(tup[2], tup[-1])
            tsv = fetchTSV(urlList)
            print(tsv)


