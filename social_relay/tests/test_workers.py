import datetime
from unittest.mock import Mock, patch

import pytest
from federation.entities.diaspora.entities import DiasporaPost

from social_relay.models import Node
from workers.receive import process, get_send_to_nodes, HEADERS


@pytest.mark.usefixtures('config')
@patch("social_relay.utils.data.get_pod_preferences", return_value={})
class TestReceiveWorkerCallsLogStatistics:
    @patch("workers.receive.log_worker_receive_statistics")
    @patch("workers.receive.handle_receive", return_value=("foo@example.com", "diaspora", ["foo", "bar"]))
    def test_log_statistics_called(self, mock_statistics, mock_handle_receive, mock_pod_preferences):
        process(Mock())
        assert mock_statistics.call_count == 1


@pytest.mark.usefixtures('config')
class TestReceiveWorkerProcessCallsSendPayload:
    @patch("social_relay.utils.data.get_pod_preferences", return_value={})
    @patch("workers.receive.handle_receive", return_value=("foo@example.com", "diaspora", [
        DiasporaPost(raw_content="Awesome #post")
    ]))
    @patch("workers.receive.send_document", return_value=(200, None))
    def test_send_payload_called(self, mock_send_document, mock_handle_receive, mock_pod_preferences):
        process("payload")
        assert mock_send_document.call_count == 1
        mock_send_document.assert_called_once_with(
            url="https://sub.example.com/receive/public", data="payload", headers=HEADERS,
        )


@pytest.mark.usefixtures('config')
@patch("workers.receive.handle_receive", return_value=("foo@example.com", "diaspora", [
    DiasporaPost(raw_content="Awesome #post", guid="foobar")
]))
@patch("workers.receive.send_document", return_value=(200, None))
@patch("social_relay.utils.data.get_pod_preferences", return_value={})
class TestReceiveWorkerStoresNodeAndPostMetadata:
    def test_send_payload_stores_unknown_node_into_db(self, mock_handle_receive, mock_send_document,
                                                      mock_pod_preferences):
        process(Mock())
        assert Node.select().count() == 1
        node = Node.get(Node.host=="sub.example.com")
        assert node
        assert node.https

    def test_send_payload_updates_existing_node_in_db(self, mock_handle_receive, mock_send_document,
                                                      mock_pod_preferences):
        Node.create(
            host="sub.example.com", last_success=datetime.datetime.now()
        )
        process(Mock())
        node = Node.get(Node.host=="sub.example.com")
        assert node.total_delivered == 1
        assert node.https


    def test_send_payload_failure_updates_existing_node_failure_count(self, mock_handle_receive, mock_send_payload,
                                                                      mock_pod_preferences):
        Node.create(
            host="sub.example.com", last_success=datetime.datetime.now()
        )
        mock_send_payload.return_value = {"result": False, "https": False}
        process(Mock())
        node = Node.get(Node.host=="sub.example.com")
        assert node.failure_count == 1

    def test_send_payload_success_clears_existing_node_failure_count(self, mock_handle_receive, mock_send_document,
                                                                     mock_pod_preferences):
        Node.create(
            host="sub.example.com", last_success=datetime.datetime.now(), failure_count=1
        )
        process(Mock())
        node = Node.get(Node.host == "sub.example.com")
        assert node.failure_count == 0


@pytest.mark.usefixtures('config')
class TestReceiveWorkerGetSendToNodes:
    @patch("workers.receive.nodes_who_want_all", return_value=set())
    def test_get_send_to_nodes_with_post_returns_nodes(self, mock_nodes_who_want_all):
        nodes = get_send_to_nodes("foo@example.com", DiasporaPost())
        assert nodes == {"sub.example.com"}

    @patch("workers.receive.nodes_who_want_tags", return_value={"tags.example.com"})
    @patch("workers.receive.nodes_who_want_all", return_value=set())
    def test_get_send_to_nodes_with_post_returns_nodes_with_tags(self, mock_nodes_who_want_tags,
                                                                 mock_nodes_who_want_all):
        nodes = get_send_to_nodes("foo@example.com", DiasporaPost())
        assert nodes == {"sub.example.com", "tags.example.com"}
