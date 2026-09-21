import flet as ft
from services.storage import save_setting


def ServerPickerView(page: ft.Page, navigate) -> ft.View:
    # 1. Set width to 140px so "https://" fits comfortably alongside the dropdown arrow
    protocol_dropdown = ft.Dropdown(
        value="https://",
        width=140,
        options=[
            ft.dropdown.Option("https://"),
            ft.dropdown.Option("http://"),
        ],
    )

    # 2. Host input field takes remaining horizontal space
    host_input = ft.TextField(
        label="Server Host / IP",
        hint_text="jast.example.com",
        autofocus=True,
        expand=True,
    )

    status_text = ft.Text("", color=ft.Colors.RED)

    def save_server(e):
        raw_host = host_input.value.strip()

        # Clean off any protocol typed by accident
        if raw_host.startswith("http://"):
            raw_host = raw_host[7:]
        elif raw_host.startswith("https://"):
            raw_host = raw_host[8:]

        # Strip trailing slashes or pre-existing /api
        raw_host = raw_host.rstrip("/")
        if raw_host.endswith("/api"):
            raw_host = raw_host[:-4].rstrip("/")

        if not raw_host:
            status_text.value = "Please enter a valid host address"
            page.update()
            return

        protocol = protocol_dropdown.value
        final_url = f"{protocol}{raw_host}/api"

        save_setting("server_url", final_url)
        navigate("/login")

    return ft.View(
        route="/server",
        controls=[
            ft.SafeArea(
                content=ft.Container(
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.PARK, size=64, color="#a3b18a"),
                            ft.Text(
                                "Welcome to Jast",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Select protocol and enter server host",
                                color="#a3b18a",
                            ),
                            ft.Container(height=10),
                            # Container set to 360px total width
                            ft.Container(
                                width=360,
                                content=ft.Row(
                                    controls=[protocol_dropdown, host_input],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=10,
                                ),
                            ),
                            # Subtext helper note
                            ft.Text(
                                "e.g. jast.domain.com or 192.168.1.50:8000",
                                size=12,
                                color="#a3b18a",
                            ),
                            status_text,
                            ft.FilledButton(
                                "Connect to Server",
                                icon=ft.Icons.ARROW_FORWARD,
                                on_click=save_server,
                                width=360,
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
