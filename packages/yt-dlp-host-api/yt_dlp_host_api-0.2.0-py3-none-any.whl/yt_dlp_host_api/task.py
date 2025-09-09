import requests
import json
import time
from .exceptions import APIError

class Task:
    def __init__(self, client, task_id, task_type):
        self.client = client
        self.task_id = task_id
        self.task_type = task_type

    def get_status(self):
        response = requests.get(f"{self.client.host_url}/status/{self.task_id}", headers=self.client.headers)
        if response.status_code != 200:
            raise APIError(response.json().get('error', 'Unknown error'))
        return response.json()

    def get_result(self, max_retries=360, delay=1):
        for _ in range(max_retries):
            status = self.get_status()
            if status['status'] == 'completed':
                return TaskResult(self.client, status)
            elif status['status'] == 'error':
                raise APIError(f"Task failed: {status.get('error', 'Unknown error')}")
            elif status['status'] in ['waiting', 'processing']:
                time.sleep(delay)
            else:
                raise APIError(f"Unknown task status: {status['status']}")
        
        raise APIError(f"Task did not complete within the expected time (waited {max_retries * delay} seconds)")

class TaskResult:
    def __init__(self, client, status):
        self.client = client
        self.status = status

    def get_file(self, raw_response=False):
        url = self.get_file_url()
        response = requests.get(url, headers=self.client.headers)
        if response.status_code != 200:
            raise APIError(response.json().get('error', 'Unknown error'))
        if raw_response: return response
        return response.content

    def get_file_url(self):
        return f"{self.client.host_url}{self.status['file']}"

    def save_file(self, path):
        url = self.get_file_url()
        response = requests.get(url, headers=self.client.headers)
        if response.status_code != 200:
            raise APIError(response.json().get('error', 'Unknown error'))
        with open(path, 'wb') as f:
            f.write(response.content)

    def get_json(self, fields=None):
        if self.status['task_type'] != 'get_info':
            raise APIError("This method is only available for get_info tasks")
        url = self.get_file_url()
        if fields:
            url += "?"
            for field in fields:
                url += f'{field}&'
        response = requests.get(url, headers=self.client.headers)
        if response.status_code != 200:
            raise APIError(response.json().get('error', 'Unknown error'))
        data = json.loads(response.text)
        return data
