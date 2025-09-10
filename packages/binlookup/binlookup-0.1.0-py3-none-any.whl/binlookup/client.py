import requests

class BinlistClient:
    BASE_URL = "https://lookup.binlist.net/"
    HEADERS = {"Accept-Version": "3"}

    def __init__(self, timeout=5):
        self.timeout = timeout

    def lookup(self, bin_number: str) -> dict:
        if not bin_number.isdigit() or len(bin_number) < 6:
            raise ValueError("BIN must be at least 6 digits")
        url = f"{self.BASE_URL}{bin_number}"
        response = requests.get(url, headers=self.HEADERS, timeout=self.timeout)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"error": "BIN not found"}
        else:
            response.raise_for_status()

