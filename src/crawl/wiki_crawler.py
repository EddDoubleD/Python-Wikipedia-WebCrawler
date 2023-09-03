import json
import queue
import string
import threading
import urllib
import uuid

import requests
from bloomfilter import BloomFilter
from bs4 import BeautifulSoup as BeautifulSoup

from src.settings.settings import WIKICrawlerConfig

FINISH = object();


def joinUrl(url, add) -> string:
    return urllib.parse.urljoin('https://en.wikipedia.org/' + add, url)


def stripeTag(html):
    soup = BeautifulSoup(html, features="html.parser")
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out
    # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    return '\n'.join(chunk for chunk in chunks if chunk)


class Crawler(threading.Thread):

    def __init__(self, pipeline: queue.Queue, out: queue.Queue):
        super().__init__()
        self.uuid = str(uuid.uuid4())
        self.pipeline = pipeline
        self.out = out
        self.filter = BloomFilter(size=100, fp_prob=1e-6)

    def bypass(self, url):
        if self.filter.__len__() >= 100:
            return

        response = requests.get(url)

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        content_div = soup.find(id="mw-content-text").find(class_="mw-parser-output")

        for element in content_div.find_all("p", recursive=False):
            # recursive = False means that we parse only towars the direct child of the DIV:

            if element.find('a', recursive=False):
                href = element.find('a', recursive=False).get('href')
                if href.__contains__("#"):
                    print(f"skip anchor link {href}")
                    continue

                if href not in self.filter:
                    self.filter.add(href)
                    self.pipeline.put(joinUrl(href, ''))
                    self.out.put(href)
                else:
                    print(f"skip double link {href}")

    def run(self) -> None:
        print(f"crawler-{self.uuid} running")
        while not self.pipeline.empty():
            value = self.pipeline.get()
            print(f"handle url: {value}")
            self.bypass(value)

        self.out.put(FINISH)
        print(f"crawler-{self.uuid} finish")


class Producer(threading.Thread):
    def __init__(self, pipeline: queue.Queue):
        super().__init__()
        self.uuid = str(uuid.uuid4())
        self.pipeline = pipeline

        config = WIKICrawlerConfig()

        self.targetUrl = config.queueUrl
        self.client = config.sqsConnection()

    @staticmethod
    def parse(topic):
        topic = f"https://en.wikipedia.org/w/api.php?action=parse&page={topic}&format=json&prop=text&section=0"
        json_response = requests.get(topic).json()
        if len(json_response) > 1 and json_response[1][0] == u'error':
            print(json_response)
            return None
        return stripeTag(json_response['parse']['text']['*'])

    def run(self):
        print(f"producer-{self.uuid} running")
        value = None
        while value != FINISH:
            while not self.pipeline.empty():
                value = self.pipeline.get()
                if value != FINISH:
                    value = value.replace("/wiki/", "")
                    message = "Error:"
                    try:
                        text = self.parse(value)
                        self.client.send_message(QueueUrl=self.targetUrl, MessageBody=json.dumps(
                            dict({"url": joinUrl(value, "wiki/"), "content": text})))
                    except Exception as e:
                        print(e)
                        self.client.send_message(QueueUrl=self.targetUrl, MessageBody=f"{message} + {e}")

        print(f"producer-{self.uuid} finish")
