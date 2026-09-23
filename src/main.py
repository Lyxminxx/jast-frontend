import flet as ft
from services.storage import AppStorage
from services.api import ApiClient
from themes import get_theme
from views.dashboard import DashboardView
from views.login import LoginView
from views.server_picker import ServerPickerView
from views.statistics import StatisticsView
from views.account import AccountView
from views.register import RegisterView

# 1. Change to async def
async def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    forest = get_theme()
    page.theme = forest
    page.bgcolor = forest.color_scheme.surface
    page.title = "Jast Tracker"

    app_storage = AppStorage(page)
    # 2. Await the initial cache load BEFORE running the rest of the app
    await app_storage.init()  
    
    api_client = ApiClient(app_storage)

    def navigate(route: str):
        page.route = route
        route_change()

    def route_change(e=None):
        page.views.clear()

        if page.route == "/server":
            page.views.append(ServerPickerView(page, navigate, app_storage, api_client))
        elif page.route == "/login":
            page.views.append(LoginView(page, navigate, app_storage, api_client))
        elif page.route == "/register":
            page.views.append(RegisterView(page, navigate, app_storage, api_client))
        elif page.route == "/dashboard":
            page.views.append(DashboardView(page, navigate, app_storage, api_client))
        elif page.route == "/statistics":
            page.views.append(StatisticsView(page, navigate, app_storage, api_client))
        elif page.route == "/account":
            page.views.append(AccountView(page, navigate, app_storage, api_client))

        page.update()

    page.on_route_change = route_change

    if not app_storage.get_setting("server_url"):
        navigate("/server")
    elif not app_storage.get_setting("auth_token"):
        navigate("/login")
    else:
        navigate("/dashboard")

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
