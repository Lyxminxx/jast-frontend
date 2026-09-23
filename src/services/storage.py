import flet as ft

class AppStorage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.prefs = ft.SharedPreferences()
        self._cache = {}

    async def init(self):
        # Only look for our exact keys, ignoring hidden browser data
        app_keys = ["server_url", "auth_token", "refresh_token", "currency_symbol"]
        
        for k in app_keys:
            if await self.prefs.contains_key(k):
                self._cache[k] = str(await self.prefs.get(k))

    def save_setting(self, key: str, value: str) -> None:
        self._cache[key] = value
        self.page.run_task(self._async_save, key, value)

    async def _async_save(self, key, value):
        await self.prefs.set(key, str(value))

    def get_setting(self, key: str, default: str | None = None) -> str | None:
        return self._cache.get(key, default)

    def remove_setting(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]
        self.page.run_task(self._async_remove, key)

    async def _async_remove(self, key):
        await self.prefs.remove(key)

    def get_currency_symbol(self) -> str:
        return self.get_setting("currency_symbol") or "kr"

    def set_currency_symbol(self, symbol: str) -> None:
        self.save_setting("currency_symbol", symbol)
