import pytest

from oscar_sagepay.wrappers import Response
from tests import responses


@pytest.fixture
def response():
    return Response('test_1', responses.MALFORMED)


@pytest.fixture
def malformed_response():
    return Response('test_1', responses.MALFORMED)


@pytest.fixture
def registered_response():
    return Response('test_1', responses.REGISTERED)


def test_response_allows_params_to_be_extracted(response):
    assert response.param('VPSProtocol') == '3.00'
    assert response.param('Status') == 'MALFORMED'


def test_response_has_status_property(response):
    assert response.status == response.MALFORMED


def test_response_has_status_detail_property(response):
    assert response.status_detail == "3009 : The VendorTxCode is missing."


def test_malformed_response_is_not_successful(malformed_response):
    assert not malformed_response.is_successful


def test_registered_response_is_not_successful(registered_response):
    assert registered_response.is_successful
