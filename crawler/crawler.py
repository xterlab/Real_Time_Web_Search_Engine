import json
import requests
from bs4 import BeautifulSoup
import pymongo

class Crawler():
    # connect to cloud mongo
    uri = "mongodb+srv://deepak:deepakpanwa<write MongoDB passwword>@cluster0.pwcyhe9.mongodb.net/search_engine?retryWrites=true&w=majority"
    
    client = pymongo.MongoClient(uri)
    
    # create db client
    db = client.search

    # search results storage
    search_results = []

    # crawl domain
    def crawl(self, url, depth):
        # try to perform HTTP GET request
        try:
            print('Crawling url: "%s" at depth: %d' % (url, depth))
            response = requests.get(url, headers={'user-agent': 'code-monkey-search'})
        
        # return otherwise
        except:
            print('Failed to perform HTTP GET request on "%s"\n' % url)
            return
        
        # parse page content
        content = BeautifulSoup(response.text, 'lxml')

        # try to extract page title and description
        try:
            title = content.find('title').text
            description = ''
            
            for tag in content.findAll():
                if tag.name == 'p':
                    description += tag.text.strip().replace('\n', '')
        # return otherwise
        except:
            return
        
        # store the result structure
        result = {
            'url': url,
            'title': title,
            'description': description
        }
        
        search_results = self.db.search_results
        search_results.insert_one(result)
        search_results.create_index([
            ('url', pymongo.TEXT),
            ('title', pymongo.TEXT),
            ('description', pymongo.TEXT)
        ], name='search_results', default_language='english')
        
        # return when depth is exhausted
        if depth == 0:
            return

        # extract all the available links on the page
        links = content.findAll('a')

        # loop over links
        for link in links:
            # try to crawl links recursively
            try:
                # use only links starting with 'http'
                if 'http' in link['href']:
                    self.crawl(link['href'], depth - 1)
            
            # ignore internal links
            except KeyError:
                pass
        
        # close connection (should be outside the crawl method)
        self.client.close()

crawler = Crawler()
crawler.crawl('https://www.zomato.com/', 5)
