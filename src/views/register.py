import flet as ft
from services.api import api_client
from services.storage import get_setting, remove_setting


def RegisterView(page: ft.Page, navigate) -> ft.View:
    server_url = get_setting("server_url") or "Not Configured"

    # Input controls
    username_input = ft.TextField(
        label="Username",
        prefix_icon=ft.Icons.PERSON,
        autofocus=True,
        width=360,
    )

    email_input = ft.TextField(
        label="Email (Optional)",
        prefix_icon=ft.Icons.EMAIL,
        width=360,
    )

    first_name_input = ft.TextField(
        label="First Name (Optional)",
        prefix_icon=ft.Icons.BADGE,
        width=360,
    )

    last_name_input = ft.TextField(
        label="Last Name (Optional)",
        prefix_icon=ft.Icons.BADGE_OUTLINED,
        width=360,
    )

    password_input = ft.TextField(
        label="Password",
        prefix_icon=ft.Icons.LOCK,
        password=True,
        can_reveal_password=True,
        width=360,
    )

    confirm_password_input = ft.TextField(
        label="Confirm Password",
        prefix_icon=ft.Icons.LOCK_OUTLINED,
        password=True,
        can_reveal_password=True,
        width=360,
    )

    status_text = ft.Text("", color=ft.Colors.RED, size=14)
    loading_ring = ft.ProgressRing(width=20, height=20, visible=False, stroke_width=2)

    def handle_register(e):
        username = username_input.value.strip()
        email = email_input.value.strip()
        first_name = first_name_input.value.strip()
        last_name = last_name_input.value.strip()
        password = password_input.value
        confirm_password = confirm_password_input.value

        if not username or not password:
            status_text.value = "Username and password are required."
            status_text.color = ft.Colors.RED
            page.update()
            return

        if password != confirm_password:
            status_text.value = "Passwords do not match."
            status_text.color = ft.Colors.RED
            page.update()
            return

        # UI feedback for in-flight request
        register_btn.disabled = True
        loading_ring.visible = True
        status_text.value = ""
        page.update()

        # Call Django registration endpoint
        success, message = api_client.register(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        loading_ring.visible = False
        register_btn.disabled = False

        if success:
            navigate("/dashboard")
        else:
            status_text.value = message
            status_text.color = ft.Colors.RED
            page.update()

    register_btn = ft.FilledButton(
        "Create Account",
        icon=ft.Icons.PERSON_ADD,
        on_click=handle_register,
        width=360,
    )

    def change_server(e):
        remove_setting("server_url")
        navigate("/server")

    return ft.View(
        route="/register",
        controls=[
            ft.SafeArea(
                content=ft.Container(
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.APP_REGISTRATION, size=56, color="#a3b18a"),
                            ft.Text("Register", size=28, weight=ft.FontWeight.BOLD),
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
                            ft.Container(height=6),
                            username_input,
                            email_input,
                            first_name_input,
                            last_name_input,
                            password_input,
                            confirm_password_input,
                            ft.Row(
                                controls=[loading_ring, status_text],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=10,
                            ),
                            register_btn,
                            ft.Container(height=6),
                            # Link to login view
                            ft.Row(
                                controls=[
                                    ft.Text("Already have an account?", color="#a3b18a"),
                                    ft.TextButton(
                                        "Sign In",
                                        on_click=lambda _: navigate("/login"),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=2,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ),
                expand=True,
            )
        ],
    )
