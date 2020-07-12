from hmpy import (
    ApiResource,
    HiveMind,
    Task,
    extract_next_token,
)


def test_client(hm_test_client):
    assert issubclass(type(hm_test_client), ApiResource)
    assert isinstance(hm_test_client, HiveMind)
    assert hm_test_client.session.headers["Authorization"] == "ApiKey SECRET"
    assert hm_test_client.base_url == "https://studio.lambda.hvmd.io/api/"


def test_get_task(mocked_responses, hm_test_client, response_get_task):

    mocked_responses.add(response_get_task)

    task = hm_test_client.task(1470)
    assert issubclass(type(task), ApiResource)
    assert isinstance(task, Task)
    assert task.id == 1470


def test_extract_next_token():
    test_link = '</api/tasks/1470/instances?token=eyJUYXNrSWQiOnsiVmFsdWUiOjE0NzB9LCJTaG93Q2FuY2VsbGVkIjpmYWxzZSwiUGFnaW5nUGFyYW1ldGVycyI6eyJUYWtlIjo1MCwiU2tpcCI6NTAsIlNvcnQiOltdLCJGaWx0ZXIiOltdfSwiVGFncyI6W10sIkluY2x1ZGVTdW1tYXJ5IjpmYWxzZSwiVXNlcklkIjp7IlZhbHVlIjoxMjIwfX0%3D>; rel="next"'
    test_token = "eyJUYXNrSWQiOnsiVmFsdWUiOjE0NzB9LCJTaG93Q2FuY2VsbGVkIjpmYWxzZSwiUGFnaW5nUGFyYW1ldGVycyI6eyJUYWtlIjo1MCwiU2tpcCI6NTAsIlNvcnQiOltdLCJGaWx0ZXIiOltdfSwiVGFncyI6W10sIkluY2x1ZGVTdW1tYXJ5IjpmYWxzZSwiVXNlcklkIjp7IlZhbHVlIjoxMjIwfX0="
    assert test_token == extract_next_token(test_link)


def test_get_task_instances(
    mocked_responses,
    hm_test_client,
    response_get_task,
    response_get_paginated_instances,
):

    mocked_responses.add(response_get_task)
    task = hm_test_client.task(1470)

    mocked_responses.remove(response_get_task)
    mocked_responses.add(response_get_paginated_instances[0])
    mocked_responses.add(response_get_paginated_instances[1])
    instances = task.instances(per_page=50)
    assert instances == [{"pagination": "test"}, {"pagination": "test2"}]


def test_get_task_results_one_day_only_complete_with_iters(
    hm_test_client,
    mocked_responses,
    response_get_task,
    response_get_results_use_dates_inciter_onlycomplete,
):

    mocked_responses.add(response_get_task)
    mocked_responses.add(response_get_results_use_dates_inciter_onlycomplete)

    task = hm_test_client.task(1470)
    mocked_responses.remove(response_get_task)

    result = task.results(
        since_utc="2020-04-16T00:00:00.000000",
        as_of_utc="2020-04-16T23:59:59.999999",
        inc_incomplete_instances=False,
        inc_iterations=True,
    )
    assert result == [{"pagination": "test2"}]


def test_post_instances_bulk(
    mocked_responses, hm_test_client, response_get_task, response_post_instances_bulk
):

    mocked_responses.add(response_get_task)
    mocked_responses.add_callback(**response_post_instances_bulk)

    task = hm_test_client.task(1470)
    mocked_responses.remove(response_get_task)

    instances_list = [
        {"name": "instance_1"},
        {"name": "instance_2"},
        {"name": "instance_3"},
    ]
    resp = task.add_instances(instances=instances_list)

    assert resp.json() == [{"value": 0}, {"value": 1}, {"value": 2}]
    assert resp.status_code == 201
    assert (
        mocked_responses.calls[1].request.url
        == "https://studio.lambda.hvmd.io/api/tasks/1470/instances/bulk"
    )
    assert (
        mocked_responses.calls[1].response.text
        == '[{"value": 0}, {"value": 1}, {"value": 2}]'
    )

