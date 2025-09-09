from time import sleep
import unittest

from notbank_python_sdk.requests_models.subscribe_trades_request import SubscribeTradesRequest
from notbank_python_sdk.requests_models.unsubscribe_trades_request import UnsubscribeTradesRequest
from notbank_python_sdk.notbank_client import NotbankClient
from tests.test_helper import CallMarker, new_websocket_client_connection


class TestSubscribeTrades(unittest.TestCase):
    def setUp(self):
        self._websocket_connection = new_websocket_client_connection()
        self._websocket_connection.connect()
        self.client = NotbankClient(self._websocket_connection)

    def test_subscribe_with_instrument_id(self):
        snapshot_marker = CallMarker.create()
        update_marker = CallMarker.create()

        self.client.subscribe_trades(
            SubscribeTradesRequest(154, 3),
            lambda trades: snapshot_marker.mark_called(),
            lambda trades: update_marker.mark_called())
        sleep(60)
        self.client.unsubscribe_trades(
            UnsubscribeTradesRequest(154))
        self._websocket_connection.close()
        self.assertTrue(snapshot_marker.was_callled(),
                        'snapshot callback was not called')
        self.assertTrue(update_marker.was_callled(),
                        'update callback was not called')


if __name__ == "__main__":
    unittest.main()
