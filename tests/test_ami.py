import unittest
from agent.ami import parse_message


class AMITests(unittest.TestCase):
    def test_parse(self):
        msg = parse_message("Event: ContactStatus\r\nEndpointName: 2001\r\nContactStatus: Reachable\r\n")
        self.assertEqual(msg["Event"], "ContactStatus")
        self.assertEqual(msg["EndpointName"], "2001")
        self.assertEqual(msg["ContactStatus"], "Reachable")


if __name__ == "__main__":
    unittest.main()
