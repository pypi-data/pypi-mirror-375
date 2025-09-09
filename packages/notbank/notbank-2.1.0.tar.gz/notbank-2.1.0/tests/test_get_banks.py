import unittest
from notbank_python_sdk.requests_models.get_account_info_request import GetAccountInfoRequest

from tests import test_helper

from notbank_python_sdk.notbank_client import NotbankClient
from notbank_python_sdk.requests_models.get_banks_request import GetBanksRequest


class TestGetBanks(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        connection = test_helper.new_rest_client_connection()
        cls.credentials = test_helper.load_credentials()        
        test_helper.authenticate_connection(connection, cls.credentials)
        cls.client = NotbankClient(connection)

    def test_get_banks(self):
        response = self.client.get_banks(GetBanksRequest("CL"))
        self.assertIsNotNone(response)


if __name__ == "__main__":
    unittest.main()
