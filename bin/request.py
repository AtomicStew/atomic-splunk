import os
import sys
import typing
from json import JSONDecodeError

import requests

splunk_home = os.environ['SPLUNK_HOME']
sys.path.append(os.path.join(splunk_home, 'etc', 'apps', 'atomic-splunk', 'lib'))

from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators


@Configuration()
class RequestCommand(GeneratingCommand):
    url = Option(require=True)
    method = Option(default='GET', validate=validators.Set('GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH'))

    def generate(self):
        response = requests.request(method=self.method, url=self.url)
        try:
            data = response.json()
        except JSONDecodeError:
            yield self.to_event(response.content)
            return

        if isinstance(data, typing.Sequence):
            for item in data:
                yield self.to_event(item)
        else:
            yield self.to_event(data)

    @staticmethod
    def to_event(item):
        """
        Transform non-dicts into dicts (which represents splunk events)

        :return: An event which represents `item`
        :rtype: dict
        """
        return item if isinstance(item, typing.Mapping) else dict(value=item)


dispatch(RequestCommand, sys.argv, sys.stdin, sys.stdout, __name__)
