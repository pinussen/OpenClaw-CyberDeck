import unittest

import web_server


class _DummyServer:
    def get_status(self):
        return {"connected": True, "demo_mode": True}

    def get_display_state(self):
        return {"ok": True}


class WebServerSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        web_server.server = _DummyServer()
        cls.client = web_server.app.test_client()

    def test_api_status_smoke(self):
        resp = self.client.get("/api/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("connected", data)

    def test_api_display_state_smoke(self):
        resp = self.client.get("/api/display-state")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data.get("ok"))

    def test_api_agents_smoke(self):
        resp = self.client.get("/api/agents")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("agents", data)
        self.assertIn("count", data)

    def test_api_command_status_smoke(self):
        resp = self.client.post("/api/command", json={"command": "status"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data.get("success"))
        self.assertIn("status", data)


if __name__ == "__main__":
    unittest.main()
