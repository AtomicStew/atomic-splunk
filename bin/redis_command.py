import json
import os
import sys
import typing
from redis import Redis

splunk_home = os.environ['SPLUNK_HOME']
sys.path.append(os.path.join(splunk_home, 'etc', 'apps', 'atomic-splunk', 'lib'))

from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators


@Configuration()
class RedisCommand(GeneratingCommand):
    host = Option(require=True)
    port = Option(default=6379, validate=validators.Integer(minimum=0, maximum=2 ** 16 - 1))
    db = Option(default=0, validate=validators.Integer())
    username = Option()
    password = Option()
    command = Option(default='GET')
    args = Option(require=True)

    def generate(self):
        r = Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            username=self.username,
            password=self.password,
        )
        try:
            args = json.loads(self.args)
        except json.JSONDecodeError:
            args = [self.args]
        if isinstance(args, typing.Mapping):
            args = sum(list(args.items()), [])
        response = r.execute_command(self.command, *args)
        return self.to_events(response)

    @staticmethod
    def to_event(item):
        """
        Transform non-dicts into dicts (which represents splunk events)

        :return: An event which represents `item`
        :rtype: dict
        """
        if isinstance(item, typing.Mapping):
            return item
        if isinstance(item, bytes):
            item = item.decode('UTF-8')
        return dict(value=item)

    @classmethod
    def to_events(cls, data):
        """
        Extracts events from most data objects (which represents splunk events)

        :return: An generator of events which represents `data`
        :rtype: dict
        """
        if isinstance(data, (list, set, tuple)):
            for item in data:
                yield cls.to_event(item)
        else:
            yield cls.to_event(data)


dispatch(RedisCommand, sys.argv, sys.stdin, sys.stdout, __name__)
