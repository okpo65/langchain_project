import json
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_get_mrc_result_api_view_exceeds_token_limit():
    client = APIClient()

    # Define your test data with more than 512 tokens
    test_data = {
        'question': '이름이 뭐야?',
        'context': '이 프로젝트는  LLM 프로젝트야 ' * 80,
    }

    # Generate the URL for your view
    url = '/wrtn/chat/mrc'

    # Make a POST request to the API view
    response = client.post(url, data=json.dumps(test_data), content_type='application/json')

    # Validate the response should be 400 Bad Request
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'The total number of tokens in the question and context cannot exceed 512.' in str(response.data)


@pytest.mark.django_db
def test_get_mrc_result_api_view():
    client = APIClient()

    # Define your test data with more than 512 tokens
    test_data = {
        'question': '일반성면의 면적이 얼마야?',
        'context': '일반성면은 동부 5개 면의 교통, 문화, 교육, 상업의 중심지로서 일찍부터 상업이 발달한 곳으로 날로 반성 재래시장이 번성하고 있는 고장이다. 면적은 19.41 km²로 진주시 16개 읍면동 중 가장 적은 면이지만 인근에 경남 산림환경연구원이 있어 그곳을 찾는 관광객이 이곳 일반성면을 지나간다. 2012년 1월 1일 기준으로 인구 3,233명 (남 : 1,556명, 여 : 1,677명) 1,413세대로 6개 법정리 19개 자연마을 31개 반으로 구성되어 있다.',
    }

    # Generate the URL for your view
    url = '/wrtn/chat/mrc'

    # Make a POST request to the API view
    response = client.post(url, data=json.dumps(test_data), content_type='application/json')

    # Validate the response should be 400 Bad Request
    assert response.status_code == status.HTTP_200_OK