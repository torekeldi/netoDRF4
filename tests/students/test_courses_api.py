from random import randrange, choices
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from model_bakery import baker

from students.models import Course, Student


@pytest.fixture
def user():
    return User.objects.create_user('admin')


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_get_first_course(client, course_factory):
    courses = course_factory(_quantity=1)

    response = client.get('/api/v1/courses/1/')
    data = response.json()

    assert response.status_code == 200
    assert data['name'] == courses[0].name


@pytest.mark.django_db
def test_get_course_list(client, course_factory):
    courses = course_factory(_quantity=10)

    response = client.get('/api/v1/courses/')
    data = response.json()

    assert response.status_code == 200
    for i, c in enumerate(data):
        assert c['name'] == courses[i].name


@pytest.mark.django_db
def test_get_course_by_id(client, course_factory):
    courses = course_factory(_quantity=10)
    random_id = choices([course.id for course in courses], k=2)
    sorted_random_id = sorted(random_id)

    response = client.get(f'/api/v1/courses/?id={sorted_random_id[0]}&id={sorted_random_id[1]}')
    data = response.json()
    sorted_data = sorted(data, key=lambda x: x['id'])

    assert response.status_code == 200
    for i, d in enumerate(sorted_data):
        assert d['id'] == sorted_random_id[i]


@pytest.mark.django_db
def test_get_course_by_name(client, course_factory):
    courses = course_factory(_quantity=10)
    random_name = choices([course.name for course in courses])

    response = client.get(f'/api/v1/courses/?name={random_name[0]}')
    data = response.json()

    assert response.status_code == 200
    assert data[0]['name'] == random_name[0]


@pytest.mark.django_db
def test_post_course(client):
    count = Course.objects.count()

    response = client.post('/api/v1/courses/', data={'name': 'post_test'})
    data = response.json()

    assert response.status_code == 201
    assert Course.objects.count() == count + 1
    assert data['name'] == 'post_test'


@pytest.mark.django_db
def test_patch_course(client, course_factory):
    courses = course_factory(_quantity=1)
    data = {'name': 'update_test'}

    response = client.patch(f'/api/v1/courses/{courses[0].id}/', data=data)
    data = response.json()

    assert response.status_code == 200
    assert data['name'] == 'update_test'


@pytest.mark.django_db
def test_delete_course(client, course_factory):
    courses = course_factory(_quantity=1)
    name = courses[0].name

    count = Course.objects.count()

    response = client.delete(f'/api/v1/courses/{courses[0].id}/')
    delete_status = response.status_code

    response = client.get(f'/api/v1/courses/?name={name}')

    assert delete_status == 204
    assert response.json() == []
    assert Course.objects.count() == count - 1
