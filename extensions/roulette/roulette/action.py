import requests

from config import settings


class Timeout:
    def __init__(self, res):
        self._duration: int = res["duration_mins"]
        self._duration_label: str = res["duration_display_str"]

    @property
    def duration(self):
        return self._duration

    @property
    def duration_label(self):
        return self._duration_label


def fetch() -> Timeout | None:
    """
    Fetches an action (i.e. timeout) to apply to the user.
    :return:
    """
    try:
        res = requests.get(settings.get("remote_roulette_url"))
        action = res.json()["action"]
        if "timeout" in action:
            return Timeout(action["timeout"])
    # TODO: Tighten exception catching
    except Exception:
        return
