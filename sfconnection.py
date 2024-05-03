import requests
from dotenv import load_dotenv
from os import getenv
import json
import urllib.parse

load_dotenv()
CLIENT_KEY = getenv('CLIENT_KEY')
CLIENT_SECRET = getenv('CLIENT_SECRET')
SF_INSTANCE = getenv('SF_INSTANCE')
SF_URL = f'https://{SF_INSTANCE}.sandbox.my.salesforce.com'
SF_OAUTH = '/services/oauth2/token'
DEBUG = getenv('DEBUG')
SYPY_INFO = 'INFO'
SYPY_WARNING = 'WARNING'
SYPY_ERROR = 'ERROR'


def log(lvl, msg):
    if DEBUG:
        print(f'{lvl}: {msg}')


class SFConnection:
    def __init__(self, version='v60.0'):
        self.version = version
        self.queryURL = f'/services/data/{self.version}/query?q='

    def extractSFCredentials(self, data):
        error = None
        try:
            self.access_token = data['access_token']
            self.signature    = data['signature']
            self.instance_url = data['instance_url']
            self.id           = data['id']
            self.token_type   = data['token_type']
            self.issued_at    = data['issued_at']
        except KeyError as e:
            error = e
        finally:
            return error

    def connect(self):
        data = {'grant_type': 'client_credentials', 'client_id': CLIENT_KEY, 'client_secret': CLIENT_SECRET}
        header = {'Conent-Type': 'application/json'}
        r = requests.post(url=f'{SF_URL}{SF_OAUTH}', data=data, headers=header)
        if r.status_code != 200:
            print("There was a problem when connecting to Salesforce")
            error = json.loads(r.text)
            if error is not None:
                return error
        jsondata = None
        try:
            jsondata = json.loads(r.text)
        except json.JSONDecodeError as e:
            print("There was an error while trying to read the response from Salesforce.")
            return e
        error = self.extractSFCredentials(jsondata)
        if error is not None:
            return error
        log(SYPY_INFO, 'Successfully got OAuth Token.')

    def query(self, query):
        query = urllib.parse.quote_plus(query)
        headers = {'Authorization': f'Bearer {self.access_token}'}
        url = f'{self.instance_url}/{self.queryURL}{query}'
        r = requests.get(url, headers=headers)
        # TODO error handling, cant be fucked right now
        data = json.loads(r.text)
        return data, None

if __name__ == '__main__':
    sf = SFConnection()
    error = sf.connect()
    if error is not None:
        print('Encountered unrecorable error.')
        print(error)
    testquery = 'Select id from Account'
    print(f'Running following query:"{testquery}"')
    data, error = sf.query(testquery)
    if error is not None:
        print(error)
    print(f'Got {data["totalSize"]} records back')
