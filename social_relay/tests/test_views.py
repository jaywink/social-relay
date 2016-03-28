# -*- coding: utf-8 -*-
from unittest.mock import patch

from flask import url_for
import pytest


@pytest.mark.usefixtures('client_class')
class TestViewsRespond(object):
    def test_index(self, client):
        assert client.get(url_for('index')).status_code == 200

    def test_host_meta(self, client):
        assert client.get(url_for('host_meta')).status_code == 200

    def test_webfinger_returns_404_with_no_or_invalid_parameters(self, client):
        assert client.get(url_for('webfinger')).status_code == 404
        assert client.get("{url}?q=foobar%40example.com".format(url=url_for('webfinger'))).status_code == 404

    def test_webfinger_returns_200_with_relay_account(self, client):
        assert client.get("{url}?q=relay%40relay.local".format(url=url_for('webfinger'))).status_code == 200

    def test_hcard_returns_404_with_invalid_parameters(self, client):
        assert client.get(url_for('webfinger', guid="1234")).status_code == 404

    def test_hcard_returns_200_with_relay_guid(self, client):
        assert client.get(url_for('webfinger', guid="jvfhieuhfuih78fhf8uibhfhuyweyfdu")).status_code == 404

    def test_receive_public_returns_404_without_xml_content(self, client):
        assert client.post(url_for("receive_public")).status_code == 404

    def test_receive_public_returns_200_with_xml_content(self, client):
        assert client.post(url_for("receive_public"), data={"xml": "foo"}).status_code == 200


@pytest.mark.usefixtures('client_class')
class TestViewsCallStatisticsLoggers(object):
    @patch("social_relay.views.log_receive_statistics")
    def test_receive_public_calls_log_receive_statistics(self, mock_statistics, client):
        client.post(url_for("receive_public"), data={"xml": "foo"})
        assert mock_statistics.call_count == 1
