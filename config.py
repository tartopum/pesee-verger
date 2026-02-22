import json


class Config:
    def __init__(self):
        self.ap = {
            "ssid": "Newton",
            "password": "",
        }
        self.networks = []
        self.pressure_sensor = {
            "addr": 0x48,
            "channel": 1,
            "pin_sda": 0,
            "pin_scl": 1,
        }
        self.error = None

    def load(self):
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
                self.ap = data.get("ap", self.ap)
                self.networks = data.get("networks", self.networks)
                self.pressure_sensor = data.get("pressure_sensor", self.pressure_sensor)
        except Exception as e:
            self.error = e

    def save(self):
        with open("config.json", "w") as f:
            json.dump(self, f)


config = Config()