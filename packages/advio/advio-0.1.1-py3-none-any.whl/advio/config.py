

from loguru import logger
import sys,json
from pathlib import Path
from typing import Optional


logger.remove()
logger.add(sink = sys.stdout, format = '<c><b>{time:YYYY-MM-DD HH:mm:ss}</b></c> | <level>{level: <8}</level> | <white><b>{message}</b></white>')
logger = logger.opt(colors = True)







class Settings:
    def __init__(
        self,
        sessions_path: Optional[str] = None,
        join_list: Optional[str] = None,
        sleep_time: Optional[int] = None,
        telegram: Optional[str] = None,
        last_index: Optional[int] = None
    ):
        """
        Initialize the Settings object

        Parameters
        ----------
        sessions_path : str, optional
            Path to the sessions file. Default is 'sessions.ses'.
        join_list : str, optional
            Path to the join list file. Default is 'join_list.txt'.
        sleep_time : int, optional
            Time in seconds to sleep between joins. Default is 1.
        telegram : str, optional
            Telegram client type. Default is 'A'.
            - 'A' => Android
            - 'X' => AndroidX
            - 'W' => Windows
            - 'I' => iOS
            - 'L' => Linux
            - 'M' => macOS
            - 'MD'=> macOS Desktop
        last_index : int, optional
            Last index of the join list. Default is 0.
        """
        self.SETTINGS_JSON = self._resolve_path('settings.json')
        data = self._load()

        self.sessions_path = sessions_path or data.get('sessions_path', 'sessions.ses')
        self.join_list     = join_list or data.get('join_list', 'join_list.txt')
        self.sleep_time    = sleep_time if sleep_time is not None else data.get('sleep_time', 1)
        self.telegram      = self._telegram(telegram, data)
        self.last_index    = last_index if last_index is not None else data.get('last_index', 0)

        self._save()

    def _resolve_path(self, filename: str) -> str:
        path = Path(filename)
        if not path.is_absolute():
            path = Path.cwd() / path
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)

    @staticmethod
    def _telegram(current_value: Optional[str], data: dict[str, str]) -> str:
        allowed_values = ['A', 'X', 'W', 'I', 'L', 'M', 'MD']
        value = current_value or data.get('telegram', 'A')
        value = value.upper()
        return value if value in allowed_values else 'A'

    def _load(self) -> dict:
        try:
            with open(self.SETTINGS_JSON, encoding='utf8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save(self) -> None:
        data = {
            "sessions_path": self.sessions_path,
            "join_list": self.join_list,
            "sleep_time": self.sleep_time,
            "telegram": self.telegram,
            "last_index": self.last_index
        }
        with open(self.SETTINGS_JSON, 'w', encoding='utf8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _update(self, key: str, value) -> None:
        setattr(self, key, value)
        data = self._load()
        data[key] = value
        self._save()

    def next_index(self) -> int:
        self.last_index += 1
        self._update('last_index', self.last_index)
        return self.last_index