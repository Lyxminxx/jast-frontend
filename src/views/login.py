import flet as ft
from services.api import api_client
from services.storage import get_setting, remove_setting


def LoginView(page: ft.Page, navigate) -> ft.View:
    server_url = get_setting("server_url") or "Not Configured"

    # Input controls
    username_input = ft.TextField(
        label="Username or Email",
        prefix_icon=ft.Icons.PERSON,
        autofocus=True,
        width=360,
    )

    password_input = ft.TextField(
        label="Password",
        prefix_icon=ft.Icons.LOCK,
        password=True,
        can_reveal_password=True,
        width=360,
    )

    status_text = ft.Text("", color=ft.Colors.RED, size=14)
    loading_ring = ft.ProgressRing(width=20, height=20, visible=False, stroke_width=2)

    def handle_login(e):
        username = username_input.value.strip()
        password = password_input.value

        if not username or not password:
            status_text.value = "Please enter both username and password."
            status_text.color = ft.Colors.RED
            page.update()
            return

        # UI feedback for in-flight request
        login_btn.disabled = True
        loading_ring.visible = True
        status_text.value = ""
        page.update()

        # Call Django authentication endpoint
        success, message = api_client.login(username, password)

        loading_ring.visible = False
        login_btn.disabled = False

        if success:
            navigate("/dashboard")
        else:
            status_text.value = message
            status_text.color = ft.Colors.RED
            page.update()

    login_btn = ft.FilledButton(
        "Sign In",
        icon=ft.Icons.LOGIN,
        on_click=handle_login,
        width=360,
    )

    def change_server(e):
        remove_setting("server_url")
        navigate("/server")

    return ft.View(
        route="/login",
        controls=[
            ft.SafeArea(
                content=ft.Container(
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.LOCK_PERSON, size=64, color="#a3b18a"),
                            ft.Text("Sign In", size=28, weight=ft.FontWeight.BOLD),
                            # Connected server badge with reset action
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.STORAGE, size=16, color="#a3b18a"),
                                    ft.Text(
                                        server_url,
                                        size=12,
                                        color="#a3b18a",
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.TextButton(
                                        "Change",
                                        on_click=change_server,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=4,
                            ),
                            ft.Container(height=10),
                            username_input,
                            password_input,
                            ft.Row(
                                controls=[loading_ring, status_text],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=10,
                            ),
                            login_btn,
                            ft.Container(height=10),
                            # Link to register view
                            ft.Row(
                                controls=[
                                    ft.Text("Don't have an account?", color="#a3b18a"),
                                    ft.TextButton(
                                        "Register",
                                        on_click=lambda _: navigate("/register"),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=2,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=12,
                    ),
                ),
                expand=True,
            )
        ],
    )
