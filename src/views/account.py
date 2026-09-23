import flet as ft

def AccountView(page: ft.Page, navigate, app_storage, api_client) -> ft.View:
    user_info = {}

    # Form Fields: Dark containers with crisp white text
    input_style = {
        "color": "#FFFFFF",
        "bgcolor": "#2a3d32",
        "border_color": "#588157",
        "focused_border_color": "#a3b18a",
        "label_style": ft.TextStyle(color="#dad7cd", weight=ft.FontWeight.BOLD),
        "width": float("inf"),
    }

    username_in = ft.TextField(label="Username", **input_style)
    first_name_in = ft.TextField(label="First Name", **input_style)
    last_name_in = ft.TextField(label="Last Name", **input_style)
    email_in = ft.TextField(label="Email", **input_style)
    
    currency_in = ft.TextField(
        label="Currency Symbol (e.g. kr, $, €)",
        value=app_storage.get_currency_symbol(),
        **input_style,
    )

    password_in = ft.TextField(
        label="New Password (leave blank to keep current)",
        password=True,
        can_reveal_password=True,
        **input_style,
    )

    status_msg = ft.Text("", size=13)
    loading_spinner = ft.ProgressRing(width=20, height=20, visible=False)

    # --- DELETE ACCOUNT MODAL ---
    def close_delete_modal(e=None):
        delete_modal.open = False
        page.update()

    def confirm_delete_account(e):
        ok, msg = api_client.delete_me()
        delete_modal.open = False
        page.update()
        if ok:
            navigate("/login")
        else:
            status_msg.value = f"Delete failed: {msg}"
            status_msg.color = ft.Colors.RED_300
            page.update()

    delete_modal = ft.AlertDialog(
        title=ft.Text("Delete Account", color="#FFFFFF"),
        content=ft.Text(
            "Are you sure you want to permanently delete your account and all associated transactions? This action cannot be undone.",
            color="#dad7cd",
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_delete_modal),
            ft.FilledButton(
                "Delete Permanently",
                bgcolor=ft.Colors.RED_400,
                color=ft.Colors.WHITE,
                on_click=confirm_delete_account,
            ),
        ],
    )

    def prompt_delete_account(e):
        if delete_modal not in page.overlay:
            page.overlay.append(delete_modal)
        delete_modal.open = True
        page.update()

    def handle_logout(e):
        api_client.logout()
        navigate("/login")

    def handle_save_profile(e):
        status_msg.value = ""
        loading_spinner.visible = True
        page.update()

        u_val = username_in.value.strip()
        e_val = email_in.value.strip()
        fn_val = first_name_in.value.strip()
        ln_val = last_name_in.value.strip()
        p_val = password_in.value.strip()
        c_val = currency_in.value.strip() or "kr"

        # Save currency locally
        app_storage.set_currency_symbol(c_val)

        ok, res = api_client.update_me(
            username=u_val or None,
            email=e_val,
            first_name=fn_val,
            last_name=ln_val,
            password=p_val or None,
        )

        loading_spinner.visible = False

        if ok:
            status_msg.value = "Profile and settings updated successfully!"
            status_msg.color = "#a3b18a"
            password_in.value = ""
        else:
            status_msg.value = f"Error: {res}"
            status_msg.color = ft.Colors.RED_300

        page.update()

    def load_user_profile():
        ok, res = api_client.get_me()
        if ok and isinstance(res, dict):
            nonlocal user_info
            user_info = res
            username_in.value = user_info.get("username", "")
            email_in.value = user_info.get("email", "")
            first_name_in.value = user_info.get("first_name", "")
            last_name_in.value = user_info.get("last_name", "")
            page.update()
        elif not ok and "401" in str(res):
            api_client.logout()
            navigate("/login")

    load_user_profile()

    content_column = ft.Column(
        controls=[
            ft.Container(height=32),
            # Header Row
            ft.Row(
                controls=[
                    ft.Text("Jast", size=24, weight=ft.FontWeight.BOLD, color="#a3b18a"),
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color="#a3b18a",
                        icon_size=20,
                        tooltip="Back to Dashboard",
                        on_click=lambda _: navigate("/dashboard"),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Text("Account Settings", size=20, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
            ft.Container(height=6),
            
            # --- PROFILE DETAILS CARD ---
            ft.Card(
                bgcolor="#344e41",
                margin=0,
                content=ft.Container(
                    padding=20,
                    content=ft.Column(
                        controls=[
                            ft.Text("PROFILE DETAILS", size=12, color="#a3b18a", weight=ft.FontWeight.BOLD),
                            username_in,
                            first_name_in,
                            last_name_in,
                            email_in,
                            currency_in,
                            password_in,
                            status_msg,
                            ft.Column(
                                controls=[
                                    loading_spinner,
                                    ft.FilledButton(
                                        "Save Changes",
                                        bgcolor="#a3b18a",
                                        color="#111d13",
                                        width=float("inf"),
                                        on_click=handle_save_profile,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=8,
                            ),
                        ],
                        spacing=14,
                    ),
                ),
            ),
            ft.Container(height=10),

            # --- SESSION & DANGER ZONE CARD ---
            ft.Card(
                bgcolor="#344e41",
                margin=0,
                content=ft.Container(
                    padding=20,
                    content=ft.Column(
                        controls=[
                            ft.Text("SESSION & ACCOUNT", size=12, color="#a3b18a", weight=ft.FontWeight.BOLD),
                            ft.OutlinedButton(
                                "Log Out",
                                icon=ft.Icons.LOGOUT,
                                icon_color="#FFFFFF",
                                style=ft.ButtonStyle(color="#FFFFFF"),
                                width=float("inf"),
                                on_click=handle_logout,
                            ),
                            ft.FilledButton(
                                "Delete Account",
                                icon=ft.Icons.DELETE_FOREVER,
                                bgcolor=ft.Colors.RED_400,
                                color=ft.Colors.WHITE,
                                width=float("inf"),
                                on_click=prompt_delete_account,
                            ),
                        ],
                        spacing=12,
                    ),
                ),
            ),
            ft.Container(height=20),
        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    return ft.View(
        route="/account",
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                width=600,
                content=content_column,
                padding=ft.padding.Padding(16, 0, 16, 0),
                expand=True,
            ),
        ],
    )
