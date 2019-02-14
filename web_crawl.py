import time
import urllib
import requests
from bs4 import BeautifulSoup as bs
import time as t
from continue_crawl import continue_crawl


start_url = "https://en.wikipedia.org/wiki/Special:Random" #opens a random wikipedia page.
target_url = "https://en.wikipedia.org/wiki/Philosophy"
article_chain=[start_url]

    
def find_first_link(url):
    
    
    response=requests.get(url)
    
    html=response.text
    soup=bs(html,'html.parser')
     
    content_div = soup.find(id="mw-content-text").find(class_="mw-parser-output")
    
    article_link=None
    
    for element in content_div.find_all("p",recursive=False):
    #recursive = False means that we parse only towars the direct child of the DIV:
    
      if element.find('a', recursive=False):
       
        article_link = element.find('a',recursive=False).get('href')
        break
    
    if article_link:
      first_link = urllib.parse.urljoin('https://en.wikipedia.org/', article_link)
      return first_link
      #return("https://en.wikipedia.org/{}".format(article_link))
    
    else:
      return
        

while continue_crawl(article_chain, target_url): 
	print(article_chain[-1])
	first_link=find_first_link(article_chain[-1])
	article_chain.append(first_link)
	t.sleep(2)
    


       	