import scrapy
from lxml import etree
from io import StringIO, BytesIO
from lxml.html.clean import clean_html

class StockScraper(scrapy.Spider):
    name = "stocks"

    def start_requests(self):
        stockname = input("What is the stock Symbol?");
        urls = [
            'http://quotes.wsj.com/' + stockname.upper()+ '/financials',
            #'http://quotes.toscrape.com/page/2/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(str(response.body)), parser)
        result = etree.tostring(tree.getroot(),pretty_print = True, method = "html")
        print("_____________________________________________________________________", result, "______________________________________________________________________")
        print clean_html(response.body)

        with open(filename, 'wb') as f:
            f.write(result)
        self.log('Saved file %s' % filename)
