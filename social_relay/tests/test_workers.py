# -*- coding: utf-8 -*-
from unittest.mock import Mock, patch

import pytest
from federation.entities.base import Post

from social_relay import config
from workers.receive import process


@pytest.mark.usefixtures('config')
class TestReceiveWorkerCallsLogStatistics(object):
    @patch("workers.receive.log_worker_receive_statistics")
    @patch("workers.receive.handle_receive", return_value=("foo@example.com", "diaspora", ["foo", "bar"]))
    def test_log_statistics_called(self, mock_statistics, mock_handle_receive):
        process(Mock())
        assert mock_statistics.call_count == 1


@pytest.mark.usefixtures('config')
class TestReceiveWorkerProcessCallsSendPayload(object):
    @patch("workers.receive.handle_receive", return_value=("foo@example.com", "diaspora", [
        Post(raw_content="Awesome #post")
    ]))
    @patch("workers.receive.send_payload")
    def test_send_payload_called(self, mock_handle_receive, mock_send_payload):
        config.ALWAYS_FORWARD_TO_HOSTS = ["foo@sub.example.com"]
        process(Mock())
        assert mock_send_payload.call_count == 1
