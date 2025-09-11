import time
import threading

class TTLDict:
    def __init__(self, default_ttl: int = 60, cleanup_interval: int = 300):
        """
        :param default_ttl: TTL по умолчанию (сек), если при записи не указан
        :param cleanup_interval: периодическая очистка от просроченных ключей (сек), по умолчанию 5 мин
        """
        self._store = {}
        self._lock = threading.Lock()
        self._default_ttl = default_ttl
        self._cleanup_interval = cleanup_interval
        self._stop_event = threading.Event()

        self._timer = threading.Thread(target=self._cleanup_worker, daemon=True)
        self._timer.start()

    def set(self, key, value, ttl: int = None):
        """Установить значение с временем жизни (в секундах)."""
        if ttl is None:
            ttl = self._default_ttl
        expire_at = time.monotonic() + ttl
        with self._lock:
            self._store[key] = (value, expire_at)

    def get(self, key):
        """Получить значение или None, если ключ отсутствует/просрочен."""
        now = time.monotonic()
        with self._lock:
            item = self._store.get(key)
            if not item:
                return None

            value, expire_at = item
            if expire_at < now:
                del self._store[key]
                return None

            return value

    def __setitem__(self, key, value):
        """
        cache[key] = val         → TTL по умолчанию
        """
        self.set(key, value, self._default_ttl)

    def __getitem__(self, key):
        """cache[key] -> value | None"""
        return self.get(key)

    def __contains__(self, key):
        return self.get(key) is not None

    def __len__(self):
        return len(self._store)

    def __repr__(self):
        return f"<TTLDict size={len(self._store)}>"

    def _cleanup_worker(self):
        """Фоновый поток для периодической очистки."""
        while not self._stop_event.wait(self._cleanup_interval):
            self.cleanup()

    def cleanup(self):
        """Удалить все просроченные ключи."""
        now = time.monotonic()
        with self._lock:
            expired = [k for k, (_, exp) in self._store.items() if exp < now]
            for k in expired:
                self._store.pop(k, None)

    def stop(self):
        """Остановить фон очистки"""
        self._stop_event.set()
        self._timer.join(timeout=1)
