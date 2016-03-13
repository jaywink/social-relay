import pytest
from flask import url_for


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
