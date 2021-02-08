import os
import sys

import requests
import pandas


splunk_home = os.environ['SPLUNK_HOME']
sys.path.append(os.path.join(splunk_home, 'etc', 'apps', 'atomic-splunk', 'lib'))

from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators


PAGE_API_URL = '{confluence_api}/content?title={page_title}&spaceKey={space_key}&expand=body.storage'


@Configuration()
class ConfluenceTableCommand(GeneratingCommand):
    space_key = Option(require=True)
    page_title = Option(require=True)
    auth_cookie = Option(require=True)
    confluence_api_url = Option(default='https://atomix.atlassian.net/wiki/rest/api')

    def generate(self):
        response = requests.get(
            url=PAGE_API_URL.format(
                confluence_api=self.confluence_api_url,
                page_title=self.page_title,
                space_key=self.space_key),
            headers=dict(cookie=self.auth_cookie),
        )
        # Raise an error in case of bad request
        response.raise_for_status()
        page_html = response.json()['results'][0]['body']['storage']['value']
        tables = pandas.read_html(page_html)
        assert len(tables) > 0, 'No tables found in the page'
        assert len(tables) <= 1, 'Found multiple tables in the page'
        table = tables[0]
        for _, row in table.iterrows():
            yield row.to_dict()


dispatch(ConfluenceTableCommand, sys.argv, sys.stdin, sys.stdout, __name__)
