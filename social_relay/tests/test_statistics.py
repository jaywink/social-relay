# -*- coding: utf-8 -*-
import pytest

from social_relay.models import ReceiveStatistic, WorkerReceiveStatistic
from social_relay.utils.statistics import log_receive_statistics, log_worker_receive_statistics


@pytest.mark.usefixtures('config')
class TestLogReceiveStatistics(object):
    def test_receive_statistics_logged(self):
        log_receive_statistics("example.com")
        assert ReceiveStatistic.select().count() == 1
        statistic = ReceiveStatistic.select().first()
        assert statistic.sender_host == "example.com"


@pytest.mark.usefixtures('config')
class TestLogWorkerReceiveStatistics(object):
    def test_worker_receive_statistics_logged(self):
        log_worker_receive_statistics("diaspora", 3, 2, 1)
        assert WorkerReceiveStatistic.select().count() == 1
        statistic = WorkerReceiveStatistic.select().first()
        assert statistic.protocol == "diaspora"
        assert statistic.entities == 3
        assert statistic.sent_amount == 2
        assert statistic.sent_success == 1
