import pytest
import responses
import json
from hmpy import HiveMind


@pytest.fixture
def hm_test_client():
    return HiveMind("SECRET")


# API responses mocking
def load_json(path):
    with open(path, "r") as jsonfile:
        return json.load(jsonfile)


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def response_get_task():

    return responses.Response(
        method=responses.GET,
        url="https://studio.lambda.hvmd.io/api/tasks/1470",
        json=load_json("tests/resources/task_1470.json"),
        status=200,
        content_type="application/json",
    )


@pytest.fixture
def response_get_paginated_instances():

    mocks = [
        responses.Response(
            method=responses.GET,
            url="https://studio.lambda.hvmd.io/api/tasks/1470/instances?perPage=50",
            json=[{"pagination": "test"}],
            status=200,
            match_querystring=True,
            headers={
                "link": '</api/tasks/1470/instances?token=eyJUYXNrSWQiOnsiVmFsdWUiOjE0NzB9LCJTaG93Q2FuY2VsbGVkIjpmYWxzZSwiUGFnaW5nUGFyYW1ldGVycyI6eyJUYWtlIjo1MCwiU2tpcCI6NTAsIlNvcnQiOltdLCJGaWx0ZXIiOltdfSwiVGFncyI6W10sIkluY2x1ZGVTdW1tYXJ5IjpmYWxzZSwiVXNlcklkIjp7IlZhbHVlIjoxMjIwfX0%3D>; rel="next"'
            },
            content_type="application/json",
        ),
        responses.Response(
            method=responses.GET,
            url="https://studio.lambda.hvmd.io/api/tasks/1470/instances?token=eyJUYXNrSWQiOnsiVmFsdWUiOjE0NzB9LCJTaG93Q2FuY2VsbGVkIjpmYWxzZSwiUGFnaW5nUGFyYW1ldGVycyI6eyJUYWtlIjo1MCwiU2tpcCI6NTAsIlNvcnQiOltdLCJGaWx0ZXIiOltdfSwiVGFncyI6W10sIkluY2x1ZGVTdW1tYXJ5IjpmYWxzZSwiVXNlcklkIjp7IlZhbHVlIjoxMjIwfX0%3D",
            json=[{"pagination": "test2"}],
            match_querystring=True,
            status=200,
            content_type="application/json",
        ),
    ]
    return mocks


@pytest.fixture
def response_get_results_use_dates_inciter_onlycomplete():

    return responses.Response(
        method=responses.GET,
        url="https://studio.lambda.hvmd.io/api/tasks/1470/results?asOfUtc=2020-04-16T23%3A59%3A59.999999&sinceUtc=2020-04-16T00%3A00%3A00.000000&incIncompleteInstances=False&incIterations=True",
        match_querystring=True,
        json=[{"pagination": "test2"}],
        status=201,
        content_type="application/json",
    )


@pytest.fixture
def response_post_instances_bulk():
    def instances_bulk_callback(request):
        payload = json.loads(request.body)
        resp_body = [{"value": num} for num, value in enumerate(payload)]
        headers = {"date": "2020-04-15"}
        return 201, headers, json.dumps(resp_body)

    return {
        "url": "https://studio.lambda.hvmd.io/api/tasks/1470/instances/bulk",
        "callback": instances_bulk_callback,
        "method": responses.POST,
        "content_type": "application/json",
    }
