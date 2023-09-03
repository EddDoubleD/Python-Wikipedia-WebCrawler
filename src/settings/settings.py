import json
import typing
from abc import ABC

import boto3
from betterconf import Config, field
from betterconf.config import AbstractProvider


class JSONProvider(AbstractProvider, ABC):
    def __init__(self, path):
        self.path = path
        with open(path, "r") as f:
            self.settings = json.load(f)

    def get(self, name: str) -> typing.Any:
        return self.settings.get(name)


class WIKICrawlerConfig(Config):
    # init custom provider
    provider = JSONProvider("ymq_settings.json")
    # parse field
    accessKeyId = field("YMQ_ID", provider=provider, default=lambda: Exception("access key id not set"))
    secretAccessKey = field("YMQ_KEY", provider=provider, default=lambda: Exception("secret access key not set"))
    serviceName = field("YMQ_SERVICE", provider=provider, default="sqs")
    endpointUrl = field("YMQ_ENDPOINT", provider=provider, default="https://message-queue.api.cloud.yandex.net")
    regionName = field("YMQ_REGION", provider=provider, default="ru-central1")
    queueUrl = field("YMQ_QUEUE", provider=provider, default=lambda: Exception("yandex message queue not set"))

    def sqsConnection(self) -> boto3.client:
        return boto3.client(
            aws_access_key_id=self.accessKeyId,
            aws_secret_access_key=self.secretAccessKey,
            service_name=self.serviceName,
            endpoint_url=self.endpointUrl,
            region_name=self.regionName
        )


class WikiParseConfig(Config):
    # init custom provider
    provider = JSONProvider("wiki_settings.json")

    startPage = field("WIKI_START", default="https://en.wikipedia.org/wiki/Special:Random")
