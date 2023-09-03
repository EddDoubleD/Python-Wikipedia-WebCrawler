from queue import Queue

from src.crawl.wiki_crawler import Crawler, Producer
from src.settings.settings import WikiParseConfig

chain = Queue()
out = Queue()

if __name__ == "__main__":
    wikiConfig = WikiParseConfig()
    chain.put(wikiConfig.startPage)
    Crawler(pipeline=chain, out=out).start()
    Producer(pipeline=out).start()

    # client.send_message(QueueUrl=queue_url, MessageBody=article_chain[-1])
    # link = chain.get()
    # print(link)
    # first_link = parseLink(link)
    # chain.put(first_link)
    # t.sleep(.5)
