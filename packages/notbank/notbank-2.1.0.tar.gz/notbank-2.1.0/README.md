# Notbank Python SDK

[main page](https://notbank.exchange)

[sign up in Notbank](https://www.cryptomkt.com/account/register).

## Installation

To install Notbank use pip

```bash
pip install notbank
```

## Documentation

This sdk makes use of the [api](https://apidoc.notbank.exchange) of Notbank.

## Quick start

### Client creation

There are two communication protocols supported by the Notbank client. Communication via websocket, and via rest. Communication via websocket requires connection and permits subscriptions, other than that they are equivalent.

```python
from notbank_python_sdk.requests_models import *
from notbank_python_sdk.client_connection_factory import new_rest_client_connection
from notbank_python_sdk.error import NotbankException
from notbank_python_sdk.notbank_client import NotbankClient

try:
    # a rest client via http
    rest_connection = new_rest_client_connection()
    client = NotbankClient(rest_connection)
except NotbankException as e:
    print(e)
```

### Error handling

All internal notbank client and notbank server errors inherit from NotbankException, and all client methods may throw it (e.g. invalid request, request timeout, ...)

```python
# client : NotbankClient : ....
try:
    orderbook = client.get_order_book(OrderBookRequest("BTCUSDT", 1, 1))
except NotbankException as e:
    print(e)
```

### Put order at the top of book example

```python
import random
from decimal import Decimal

from notbank_python_sdk.notbank_client import NotbankClient
from notbank_python_sdk.client_connection_factory import new_rest_client_connection

account_id: int = 13  # must be user account id

# instantiate client
connection = new_rest_client_connection()
client = NotbankClient(connection)

# authentication (same for rest client or websocket client)
authenticate = client.authenticate(
    AuthenticateRequest(
        api_public_key="api-public-key",
        api_secret_key="api-secret-key",
        user_id="user-id",
    )
)
if not authenticate.authenticated:
    raise Exception("client not authenticated")

# get USDT user balance (also known as position)
positions = client.get_account_positions(
    GetAccountPositionsRequest(account_id))
usdt_balance = None
product = "USDT"
market_pair = "BTCUSDT"
for position in positions:
    if position.product_symbol == product:
        usdt_balance = position
if usdt_balance is None:
    raise Exception("user has no balance")

# define order_amount (between all usdt_balance and half usdt_balance)
total_balance = usdt_balance.amount
quantity_to_spend = total_balance - \
    Decimal(random.random()) * (total_balance/2)

# define order_price (around market top)
orderbook = client.get_order_book(
    OrderBookRequest(market_pair, level=2, depth=5))
top_orderbook = orderbook.bids[0]
delta = Decimal(random.randrange(10, 100))/1000
order_price = top_orderbook.price + delta
order_quantity = quantity_to_spend / order_price

# send order
instrument = client.get_instrument_by_symbol(market_pair)
request = SendOrderRequest(
    instrument=instrument,
    account_id=account_id,
    time_in_force=TimeInForce.GTC,
    side=Side.Buy,
    quantity=order_quantity,
    limit_price=order_price,
    order_type=OrderType.Limit,
)
response = client.send_order(request)

# handle order result
if response.status == SendOrderStatus.REJECTED:
    # order was rejected
    raise Exception("rejected order")
else:
    # order was accepted
    order_id = response.order_id
    print(order_id)

# close client
client.close()
```

### websocket 
There are two websocket clients, and can be instanced with the functions `new_websocket_client_connection` and `new_restarting_websocket_client_connection`. 

The restarting websocket will reconnect forever when the connection goes down unexpectedly, re-authenticating if it was authenticated, and re-subscribing to already stablished subscriptions. While reconnecting, calls to the websocket will throw. For subscriptions, reconnection will call again the snapshot hooks.
```python
from notbank_python_sdk.requests_models import *
from notbank_python_sdk.client_connection_factory import new_websocket_client_connection, new_restarting_websocket_client_connection
from notbank_python_sdk.error import NotbankException
from notbank_python_sdk.notbank_client import NotbankClient

try:
    # a websocket client
    websocket_connection = new_websocket_client_connection()
    client = NotbankClient(websocket_connection)
except NotbankException as e:
    print(e)



try:
    # a restarting websocket client
    restarting_websocket_connection = new_restarting_websocket_client_connection()
    client = NotbankClient(restarting_websocket_connection)
except NotbankException as e:
    print(e)
```

