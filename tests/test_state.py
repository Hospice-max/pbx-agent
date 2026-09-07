import tempfile
import unittest
from agent.state import StateStore


class StateTests(unittest.TestCase):
    def test_extension_update(self):
        with tempfile.TemporaryDirectory() as directory:
            store = StateStore(directory + "/state.json")
            store.update_extension("2001", "ext-local", "8")
            data = store.snapshot()
            self.assertEqual(data["extensions"]["2001"]["state"], "ringing")
            self.assertEqual(data["extensions"]["2001"]["class"], "status-orange")

    def test_channel_lifecycle(self):
        store = StateStore("/tmp/pbx-agent-test-state.json")
        store.add_channel("PJSIP/2001-1", "abc", "Up")
        self.assertEqual(store.snapshot()["summary"]["active_channels"], 1)
        store.remove_channel("abc")
        self.assertEqual(store.snapshot()["summary"]["active_channels"], 0)


if __name__ == "__main__":
    unittest.main()
