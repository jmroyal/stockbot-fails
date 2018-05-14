from scrapy.selector import Selector
from scrapy.http import HtmlResponse

def remove_non_ascii(text):
    return ''.join(i for i in text if ord(i)<128)

scrapy shell "quotes.wsj.com/GOOGL/financials"
meme1 = ""
meme = Selector(text = response.body).xpath('//span/text()').extract()
meme = response.xpath("//span/text()").extract()
with open ("memes1.txt", 'w') as f:
    for i in range(len(meme)-1):
        meme2 = remove_non_ascii(meme[i])
        meme1 = meme1 + meme2 + "\n"
    f.write(meme1)
