import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ira_ev_api_wrapper.iraApi import IraAPI


class TestAuth(unittest.TestCase):

    def setUp(self):
        self.auth = IraAPI()

    def test_login(self):
        print()
        print("Test login")

        countryCode = "91"
        phone = "1234567890"

        refId = self.auth.login(countryCode, phone)
        print(f"refId: {refId}")

        self.assertIsNotNone(refId)
        self.assertTrue(len(refId) > 0)

    def test_verifyOtp(self):
        print()
        print("Test verifyOtp")

        otp: str = "123456"
        countryCode = "91"
        phone = "1234567890"
        refId: str = "dbc9a19d-9794-4980-9e29-6a238d6aa26e"

        tokenData = self.auth.verifyOtp(refId, otp, countryCode, phone)
        print(f"accessToken: {tokenData.accessToken}")
        print(f"refreshToken: {tokenData.refreshToken}")

        self.assertIsNotNone(tokenData)
        self.assertIsNotNone(tokenData.accessToken)
        self.assertIsNotNone(tokenData.refreshToken)

    def test_refreshAccessToken(self):
        print()
        print("Test refreshAccessToken")

        refreshToken = "0787fafa-9227-4125-aae4-e24609d57525"

        tokenData = self.auth.refreshAccessToken(refreshToken)
        print(f"accessToken: {tokenData.accessToken}")
        print(f"refreshToken: {tokenData.refreshToken}")

        self.assertIsNotNone(tokenData)
        self.assertIsNotNone(tokenData.accessToken)
        self.assertIsNotNone(tokenData.refreshToken)

    def test_getVehicles(self):
        print()
        print("Test getVehicles")

        accessToken = "cb3e5d8a-0c9c-478a-acf0-85e73930f6e9"

        vehicles = self.auth.getVehicles(accessToken)
        print(f"Vehicle Count: {len(vehicles)}")

        for vehicle in vehicles:
            print(f"chassisNumber: {vehicle.chassisNumber}")
            print(f"registrationNumber: {vehicle.registrationNumber}")
            print(f"parentProductLine: {vehicle.parentProductLine}")
            print()

        self.assertIsNotNone(vehicles)
        self.assertGreater(len(vehicles), 0)


if __name__ == "__main__":
    unittest.main(exit=False)
