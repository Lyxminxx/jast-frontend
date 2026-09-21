import flet as ft
from services.storage import get_setting
from themes import get_theme
from views.dashboard import DashboardView
from views.login import LoginView
from views.server_picker import ServerPickerView
from views.statistics import StatisticsView
from views.account import AccountView
from views.register import RegisterView


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    forest = get_theme()
    page.theme = forest
    page.bgcolor = forest.color_scheme.surface

    page.title = "Jast Tracker"

    def navigate(route: str):
        page.route = route
        route_change()

    def route_change(e=None):
        page.views.clear()

        if page.route == "/server":
            page.views.append(ServerPickerView(page, navigate))
        elif page.route == "/login":
            page.views.append(LoginView(page, navigate))
        elif page.route == "/register":
            page.views.append(RegisterView(page, navigate))
        elif page.route == "/dashboard":
            page.views.append(DashboardView(page, navigate))
        elif page.route == "/statistics":
            page.views.append(StatisticsView(page, navigate))
        elif page.route == "/account":
            page.views.append(AccountView(page, navigate))

        page.update()

    page.on_route_change = route_change

    # Startup route guard
    if not get_setting("server_url"):
        navigate("/server")
    elif not get_setting("auth_token"):
        navigate("/login")
    else:
        navigate("/dashboard")


if __name__ == "__main__":
    ft.run(main)
