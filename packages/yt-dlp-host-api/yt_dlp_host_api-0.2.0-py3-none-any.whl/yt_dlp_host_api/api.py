from .client import Client

class api:
    def __init__(self, host_url):
        self.host_url = host_url

    def get_client(self, api_key):
        return Client(self.host_url, api_key)
