# -*- coding: utf-8 -*-
import datetime
from unittest.mock import Mock, patch

import pytest
from federation.entities import base

from social_relay.models import Node, Post
from workers.receive import process


@pytest.mark.usefixtures('config')
@patch("workers.receive.get_pod_preferences", return_value={})
class TestReceiveWorkerCallsLogStatistics(object):
    @patch("workers.receive.log_worker_receive_statistics")
    @patch("workers.receive.handle_receive", return_value=("foo@example.com", "diaspora", ["foo", "bar"]))
    def test_log_statistics_called(self, mock_statistics, mock_handle_receive, mock_pod_preferences):
        process(Mock())
        assert mock_statistics.call_count == 1


@pytest.mark.usefixtures('config')
@patch("workers.receive.get_pod_preferences", return_value={})
class TestReceiveWorkerProcessCallsSendPayload(object):
    @patch("workers.receive.handle_receive", return_value=("foo@example.com", "diaspora", [
        base.Post(raw_content="Awesome #post")
    ]))

    @patch("workers.receive.send_payload")
    def test_send_payload_called(self, mock_handle_receive, mock_send_payload, mock_pod_preferences):
        process(Mock())
        assert mock_send_payload.call_count == 1


@pytest.mark.usefixtures('config')
@patch("workers.receive.handle_receive", return_value=("foo@example.com", "diaspora", [
    base.Post(raw_content="Awesome #post", guid="foobar")
]))
@patch("workers.receive.send_payload", return_value={"result": True, "https": True})
@patch("workers.receive.get_pod_preferences", return_value={})
class TestReceiveWorkerStoresNodeAndPostMetadata(object):
    def test_send_payload_stores_unknown_node_into_db(self, mock_handle_receive, mock_send_payload,
                                                      mock_pod_preferences):
        process(Mock())
        assert Node.select().count() == 1
        node = Node.get(Node.host=="sub.example.com")
        assert node
        assert node.https

    def test_send_payload_updates_existing_node_in_db(self, mock_handle_receive, mock_send_payload,
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

    def test_send_payload_success_clears_existing_node_failure_count(self, mock_handle_receive, mock_send_payload,
                                                                     mock_pod_preferences):
        Node.create(
            host="sub.example.com", last_success=datetime.datetime.now(), failure_count=1
        )
        process(Mock())
        node = Node.get(Node.host == "sub.example.com")
        assert node.failure_count == 0

    def test_send_payload_insert_post_into_posts_table(self, mock_handle_receive, mock_send_payload,
                                                       mock_pod_preferences):
        process(Mock())
        post = Post.get(Post.guid=="foobar")
        assert post
        assert post.nodes.count() == 1
        assert post.nodes.first().host == "sub.example.com"
