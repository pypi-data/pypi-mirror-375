import requests
from urllib.parse import urljoin
import uuid

class ConsentiumThings:
    BASE_URL = "https://api.consentiumiot.com/"

    def __init__(self, board_key):
        self.board_key = board_key
        self.send_url = urljoin(self.BASE_URL, "v2/updateData")
        self.receive_url = urljoin(self.BASE_URL, "getData")
        self.session = requests.Session()
        self.send_key = None
        self.receive_key = None

    def begin_send(self, send_key):
        self.send_key = send_key

    def begin_receive(self, receive_key, recents=True):
        self.receive_key = receive_key
        self.receive_recent = recents

    def send_data(self, data_buff, info_buff, firmware="0.0", arch="GenericPython",
                  status_ota=False, signal_strength=-100):
        """
        Send sensor data to Consentium IoT Cloud.
        """
        if not self.send_key:
            raise ValueError("Send key not initialized. Call begin_send first.")

        sensor_data = [{"info": info, "data": str(data)}
                       for data, info in zip(data_buff, info_buff)]

        mac = ":".join(f"{b:02x}" for b in uuid.getnode().to_bytes(6, "big"))

        payload = {
            "sensors": {"sensorData": sensor_data},
            "boardInfo": {
                "firmwareVersion": firmware,
                "architecture": arch,
                "statusOTA": status_ota,
                "deviceMAC": mac,
                "signalStrength": signal_strength
            }
        }

        params = {"sendKey": self.send_key, "boardKey": self.board_key}

        try:
            response = self.session.post(self.send_url, params=params, json=payload)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as http_err:
            # If the server sent a JSON error message, capture it
            try:
                error_payload = response.json()
            except ValueError:
                error_payload = {"message": response.text}

            print(f"HTTP error {response.status_code}: {error_payload.get('message')}")
            return error_payload  # Return JSON error payload for caller to handle

        except requests.exceptions.RequestException as e:
            # Covers network errors, timeouts, etc.
            print(f"An error occurred during sending data: {e}")
            return {"message": str(e)}

    def receive_data(self):
        """
        Fetch sensor data from Consentium IoT Cloud.
        Returns a dictionary mapping sensor labels (info1, info2...) to values.
        """
        if not self.receive_key:
            raise ValueError("Receive key not initialized. Call begin_receive first.")

        params = {
            "receiveKey": self.receive_key,
            "boardKey": self.board_key
        }
        if self.receive_recent:
            params["recents"] = "true"

        try:
            response = self.session.get(self.receive_url, params=params)
            response.raise_for_status()
            payload = response.json()
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"An error occurred during receiving data: {e}")
            return {}

        board = payload.get("board", {})
        feeds = payload.get("feeds", [])

        sensor_map = {f"info{i}": f"value{i}" for i in range(1, len(board) + 1) if f"info{i}" in board}

        parsed_data = []
        for feed in feeds:
            entry = {"updated_at": feed.get("updated_at")}
            for info_key, value_key in sensor_map.items():
                label = board.get(info_key)
                if label and value_key in feed:
                    entry[label] = feed[value_key]
            parsed_data.append(entry)

        return parsed_data
