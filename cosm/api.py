# -*- coding: utf-8 -*-

import json
import re
import xml.etree.cElementTree as ET

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

import cosm


DEFAULT_FORMAT = 'json'


class Client(object):

    api_version = 'v2'
    client_class = cosm.Client

    def __init__(self, key):
        self.client = self.client_class(key)
        self.client.base_url += '/{}/'.format(self.api_version)
        self.feeds = FeedsManager(self.client)


class ManagerBase(object):

    def _url(self, url_or_id):
        url = self.base_url
        if url_or_id:
            url += '/'
            url = urljoin(url, str(url_or_id))
        return url


class FeedsManager(ManagerBase):

    def __init__(self, client):
        self.client = client
        self.base_url = urljoin(client.base_url, 'feeds')

    def create(self, title, **kwargs):
        data = dict(title=title, **kwargs)
        response = self.client.post(self.base_url, data=data)
        response.raise_for_status()
        feed = cosm.Feed(**data)
        feed._manager = self
        feed._data['feed'] = response.headers['location']
        return feed

    def update(self, id_or_url, **kwargs):
        url = self._url(id_or_url)
        payload = json.dumps(kwargs)
        response = self.client.put(url, data=payload)
        response.raise_for_status()

    def list(self, **params):
        url = self._url(None)
        response = self.client.get(url, params=params)
        response.raise_for_status()
        json = response.json()
        for feed_data in json['results']:
            feed = cosm.Feed(**feed_data)
            feed._manager = self
            yield feed

    def get(self, url_or_id, **params):
        url = self._url(url_or_id)
        response = self.client.get(url, **params)
        response.raise_for_status()
        data = response.json()
        feed = cosm.Feed(**data)
        self._manager = self
        return feed

    def delete(self, url_or_id):
        url = self._url(url_or_id)
        response = self.client.delete(url)
        response.raise_for_status()


class DatastreamsManager(ManagerBase):

    def __init__(self, client, base_url=None):
        self.client = client
        self.base_url = base_url + '/datastreams'

    def create(self, id, **kwargs):
        data = dict(id=id, **kwargs)
        response = self.client.post(self.base_url, data=data)
        response.raise_for_status()
        datastream = cosm.Datastream(**data)
        datastream._manager = self
        return datastream

    def update(self, datastream_id, **kwargs):
        url = self._url(datastream_id)
        payload = json.dumps(kwargs)
        response = self.client.put(url, data=payload)
        response.raise_for_status()

    def list(self, **params):
        url = self._url('..')
        response = self.client.get(url, params=params)
        response.raise_for_status()
        json = response.json()
        for datastream_data in json['datastreams']:
            datastream = cosm.Datastream(**datastream_data)
            datastream._manager = self
            yield datastream

    def get(self, url_or_id, format=DEFAULT_FORMAT, **params):
        url = self._url(url_or_id, format)
        response = self.client.get(url, **params)
        response.raise_for_status()
        return response.json()

    def delete(self, url_or_id):
        url = self._url(url_or_id)
        response = self.client.delete(url)
        response.raise_for_status()


class DatapointsManager(ManagerBase):

    def __init__(self, client, base_url=None):
        self.client = client
        self.base_url = base_url + '/datapoints'

    def create(self, datapoints):
        payload = json.dumps(datapoints)
        response = self.client.post(self.base_url, data=payload)
        response.raise_for_status()

    def update(self, at, value):
        url = self._url(at)
        payload = json.dumps({'value': value})
        response = self.client.put(url, data=payload)
        response.raise_for_status()

    def get(self, at, format=DEFAULT_FORMAT):
        url = self._url(at, format)
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()

    def delete(self, at):
        url = self._url(at)
        response = self.client.delete(url)
        response.raise_for_status()
