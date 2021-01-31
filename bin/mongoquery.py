import json
import os
import sys

import pymongo

splunk_home = os.environ['SPLUNK_HOME']
sys.path.append(os.path.join(splunk_home, 'etc', 'apps', 'atomic-splunk', 'lib'))

from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option


@Configuration()
class MongoQueryCommand(GeneratingCommand):
    connection_url = Option(require=True)
    db = Option(require=True)
    collection = Option(require=True)
    filter = Option(default=None)
    projection = Option(default=None)

    def generate(self):
        connection = pymongo.MongoClient(self.connection_url)
        collection = connection[self.db][self.collection]
        return collection.find(
            filter=self.filter and json.loads(self.filter),
            projection=self.projection and json.loads(self.projection),
        )


dispatch(MongoQueryCommand, sys.argv, sys.stdin, sys.stdout, __name__)
