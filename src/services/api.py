import httpx

class ApiClient:
    def __init__(self, storage, timeout: float = 10.0):
        self.storage = storage
        self.timeout = timeout

    @property
    def base_url(self) -> str | None:
        return self.storage.get_setting("server_url")

    def _headers(self, auth: bool = True) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if auth:
            token = self.storage.get_setting("auth_token")
            if token:
                headers["Authorization"] = f"Bearer {token}"
        return headers

    def get_headers(self) -> dict[str, str]:
        return self._headers(auth=True)

    def _refresh_access_token(self) -> bool:
        """Swap the stored refresh token for a fresh access token.

        Returns True only if a new access token was stored. Never raises: if it
        did, the exception would surface from a caller's `except Exception` as a
        message with no status code in it, which would break the views that
        detect an expired session by looking for "401" in the error text.
        """
        token = self.storage.get_setting("refresh_token")
        if not token:
            return False
        try:
            res = self._request(
                "POST", "/auth/refresh", auth=False, json={"refresh_token": token}
            )
            if res.status_code != 200:
                return False
            new_token = res.json().get("access_token")
        except Exception:
            return False
        if not new_token:
            return False
        self.storage.save_setting("auth_token", new_token)
        return True

    def _request(
        self, method: str, path: str, *, auth: bool = True, json=None
    ) -> httpx.Response:
        """Issue a request, transparently refreshing and retrying once on 401.

        `auth=False` both omits the bearer and opts out of the retry, which is
        what keeps /auth/refresh, /auth/login and /auth/register from recursing.

        Transport errors propagate: each caller already turns them into
        (False, str(err)), and that wording must not change.
        """
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=self.timeout) as client:
            res = client.request(method, url, json=json, headers=self._headers(auth))
            if auth and res.status_code == 401:
                if self._refresh_access_token():
                    # Re-reads auth_token, which save_setting updated synchronously.
                    res = client.request(
                        method, url, json=json, headers=self._headers(auth)
                    )
                else:
                    # Give back the original 401 so callers' messages are unchanged.
                    self.logout()
        return res

    def get_me(self) -> tuple[bool, dict | str]:
        if not self.base_url: return False, "Server URL is not configured."
        try:
            res = self._request("GET", "/auth/me")
            if res.status_code == 200:
                return True, res.json()
            return False, f"Failed to fetch profile ({res.status_code})"
        except Exception as err:
            return False, str(err)

    def get_categories(self) -> tuple[bool, list]:
        if not self.base_url: return False, []
        try:
            res = self._request("GET", "/categories")
            if res.status_code == 200:
                return True, res.json()
            return False, []
        except Exception:
            return False, []

    def get_transactions(self) -> tuple[bool, list | str]:
        if not self.base_url: return False, "Server URL is not configured."
        try:
            res = self._request("GET", "/transactions")
            if res.status_code == 200:
                return True, res.json()
            return False, f"Failed to fetch transactions ({res.status_code})"
        except Exception as err:
            return False, str(err)

    def create_transaction(self, title: str, amount: str | float, date_str: str, category_id: int | None = None) -> tuple[bool, str]:
        if not self.base_url: return False, "Server URL is not configured."
        payload = {"title": title, "amount": str(amount), "date": date_str, "category_id": category_id}
        try:
            res = self._request("POST", "/transactions", json=payload)
            if res.status_code == 200: return True, "Transaction created"
            return False, f"Error creating transaction ({res.status_code})"
        except Exception as err:
            return False, str(err)

    def update_transaction(self, transaction_id: int, title: str, amount: str | float, date_str: str, category_id: int | None = None) -> tuple[bool, str]:
        if not self.base_url: return False, "Server URL is not configured."
        payload = {"title": title, "amount": str(amount), "date": date_str, "category_id": category_id}
        try:
            res = self._request("PUT", f"/transactions/{transaction_id}", json=payload)
            if res.status_code == 200: return True, "Transaction updated"
            return False, f"Error updating transaction ({res.status_code})"
        except Exception as err:
            return False, str(err)

    def delete_transaction(self, transaction_id: int) -> tuple[bool, str]:
        if not self.base_url: return False, "Server URL is not configured."
        try:
            res = self._request("DELETE", f"/transactions/{transaction_id}")
            if res.status_code == 200: return True, "Transaction deleted"
            return False, f"Error deleting transaction ({res.status_code})"
        except Exception as err:
            return False, str(err)

    def login(self, username: str, password: str) -> tuple[bool, str]:
        if not self.base_url: return False, "Server URL is not configured."
        try:
            response = self._request(
                "POST", "/auth/login", auth=False,
                json={"username": username, "password": password},
            )
            if response.status_code == 200:
                data = response.json()
                self.storage.save_setting("auth_token", data.get("access_token"))
                if data.get("refresh_token"):
                    self.storage.save_setting("refresh_token", data.get("refresh_token"))
                return True, "Login successful"
            return False, "Invalid username or password"
        except Exception as err:
            return False, str(err)

    def logout(self) -> None:
        self.storage.remove_setting("auth_token")
        self.storage.remove_setting("refresh_token")

    def update_me(self, username: str | None = None, email: str | None = None, first_name: str | None = None, last_name: str | None = None, password: str | None = None) -> tuple[bool, dict | str]:
        if not self.base_url: return False, "Server URL is not configured."
        payload = {}
        if username: payload["username"] = username
        if email is not None: payload["email"] = email
        if first_name is not None: payload["first_name"] = first_name
        if last_name is not None: payload["last_name"] = last_name
        if password: payload["password"] = password

        try:
            res = self._request("PUT", "/auth/me", json=payload)
            if res.status_code == 200:
                try: return True, res.json()
                except Exception: return True, {}
            try:
                return False, res.json().get("detail", f"Update failed ({res.status_code})")
            except Exception:
                return False, f"Update failed ({res.status_code}): {res.text}"
        except Exception as err:
            return False, str(err)

    def delete_me(self) -> tuple[bool, str]:
        if not self.base_url: return False, "Server URL is not configured."
        try:
            res = self._request("DELETE", "/auth/me")
            if res.status_code == 200:
                self.logout()
                return True, "Account deleted."
            return False, "Failed to delete account."
        except Exception as err:
            return False, str(err)

    def register(self, username: str, password: str, email: str | None = None, first_name: str | None = None, last_name: str | None = None) -> tuple[bool, str]:
        if not self.base_url: return False, "Server URL is not configured."
        payload = {"username": username, "password": password, "email": email or "", "first_name": first_name or "", "last_name": last_name or ""}
        try:
            res = self._request("POST", "/auth/register", auth=False, json=payload)
            if res.status_code == 200:
                data = res.json()
                self.storage.save_setting("auth_token", data.get("access_token"))
                if data.get("refresh_token"):
                    self.storage.save_setting("refresh_token", data.get("refresh_token"))
                return True, "Registration successful"

            try: err_detail = res.json().get("detail", "Registration failed")
            except: err_detail = f"Registration failed ({res.status_code})"
            return False, err_detail
        except Exception as err:
            return False, str(err)
