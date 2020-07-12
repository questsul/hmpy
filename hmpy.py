# Module that contains wrapper around Hive Mind REST API.

import requests
from urllib.parse import unquote


def extract_next_token(link):
    """Use with paginated endpoints for extracting
    token which points to next page of data."""

    clean_link = link.split(";")[0].strip("<>")
    token = clean_link.split("?token=")[1]
    # token is already quoted we have to unqoute so it can be passed to params
    return unquote(token)


class ApiResource:
    """Base class for HM API wrapper.
    Contains basic functionality  like GET and POST methods.
    Initiates requests.Session object.
    """

    session = requests.Session()

    def __init__(self):
        self.base_url = "https://studio.lambda.hvmd.io/api/"

    def from_dict(self, dictionary):
        """Method used when creating objects from
        API responses."""

        for key, value in dictionary.items():
            setattr(self, key, value)
        return self

    def get_request(self, url, **kwargs):
        with self.session as s:
            response = s.get(url, **kwargs)
            response.raise_for_status()
        return response

    def get_request_paginated(self, url, params):
        """Use with endpoints for which response is paginated"""

        result = []
        while True:
            response = self.get_request(url, params=params)
            result.extend(response.json())
            try:
                next_page = response.headers["link"]
                token = extract_next_token(next_page)
                params = {"token": token}
            except KeyError:
                break
        return result

    def post_request(self, url, **kwargs):
        with self.session as s:
            response = s.post(url, **kwargs)
            response.raise_for_status()
        return response


class HiveMind(ApiResource):
    """Client class. Entry point when connecting with HM API
    To create an object valid API key is needed.
    """

    def __init__(self, api_key):
        super().__init__()
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"ApiKey {api_key}",
        }
        self.session.headers.update(self.headers)

    def task(self, task_id):
        url = f"{self.base_url}tasks/{task_id}"
        return Task(self.get_request(url).json())

    def tasks(self, status=None):
        url = f"{self.base_url}tasks"
        if status:
            payload = {"status": status}
            return self.get_request(url, params=payload).json()
        return self.get_request(url).json()


class Task(ApiResource):
    """Class that represents HiveMind task.
    Contains methods to interact with HM tasks like:
    downloading and adding new instances..."""

    def __init__(self, task_dict):
        super().__init__()
        self.base_url = f"{self.base_url}tasks/"
        self.from_dict(task_dict)

    def instance(self, instance_id):
        url = f"{self.base_url}{self.id}/instances/{instance_id}"
        return self.get_request(url).json()

    def instances(self, per_page=None):
        url = f"{self.base_url}{self.id}/instances"
        params = {"perPage": per_page}
        return self.get_request_paginated(url, params)

    def results(
        self,
        per_page=None,
        since_utc=None,
        as_of_utc=None,
        tag=None,
        inc_incomplete_instances=False,
        inc_iterations=True,
    ):

        url = f"{self.base_url}{self.id}/results"
        params = {
            "perPage": per_page,
            "asOfUtc": as_of_utc,
            "sinceUtc": since_utc,
            "tag": tag,
            "incIncompleteInstances": inc_incomplete_instances,
            "incIterations": inc_iterations,
        }
        return self.get_request_paginated(url, params)

    def add_instances(self, instances):
        url = f"{self.base_url}{self.id}/instances/bulk"
        json_data = instances
        return self.post_request(url, json=json_data)
