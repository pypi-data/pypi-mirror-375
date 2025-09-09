import json
from dataclasses import dataclass
import logging
from typing import Any, Callable, Optional
from notbank_python_sdk.client_connection import ClientConnection
from notbank_python_sdk.client_connection_factory import (
    new_websocket_client_connection as create_new_websocket_client_connection, new_rest_client_connection as create_new_rest_client_connection)
from notbank_python_sdk.requests_models.authenticate_request import AuthenticateRequest


TEST_URL = "stgapi.notbank.exchange"


@dataclass
class Credentials:
    public_key: str
    secret_key: str
    user_id: int
    account_id: int


def load_credentials(file_path: Optional[str] = None) -> Credentials:
    if file_path is None:
        file_path = 'keys.json'
    with open(file_path) as f:
        data = json.load(f)
        return Credentials(
            public_key=data['ApiPublicKey'],
            secret_key=data['ApiSecretKey'],
            user_id=data['UserId'],
            account_id=data['AccountId'],
        )


def authenticate_connection(connection: ClientConnection, credentials: Optional[Credentials] = None) -> bool:
    if credentials is None:
        credentials = load_credentials('keys.json')
    response = connection.authenticate(AuthenticateRequest(
        api_public_key=credentials.public_key,
        api_secret_key=credentials.secret_key,
        user_id=credentials.user_id,
    ))
    return response.authenticated


def new_websocket_client_connection():
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    return create_new_websocket_client_connection(
        TEST_URL,
        lambda: logger.debug("on open"),
        lambda o1, o2: logger.debug("on close"),
        lambda err: logger.debug("error: " + str(err)),
        lambda msg: logger.debug("message in: " + msg),
        lambda msg: logger.debug("message out: "+msg),
        5)


def print_message_out(httpMethod: str, headers: Any, extra_headers: Any, url: str, body: dict) -> None:
    print("\n", "** message out+*")
    print("httpMethod:", httpMethod)
    # print("headers:", headers)
    # print("extra headers:", extra_headers)
    print("url:", url)
    print("body:", body)


def print_message_in(body: str) -> None:
    print("\n", "** message in**")
    print("body:", body)


def new_rest_client_connection(
    peek_message_in: Callable[[str], None] = lambda a: None,
    peek_message_out: Callable[[str, Any, Any, str,
                                dict], None] = lambda a, b, c, d, e: None
):
    return create_new_rest_client_connection(TEST_URL, peek_message_in, peek_message_out)


class CallMarker:
    _call_count: int

    def __init__(self, call_count: int) -> None:
        self._call_count = call_count

    @staticmethod
    def create() -> 'CallMarker':
        return CallMarker(0)

    def mark_called(self) -> None:
        self._call_count += 1

    def was_callled(self) -> bool:
        return self._call_count > 0

    def get_call_count(self) -> int:
        return self._call_count
