from datetime import datetime
import flet as ft
from services.api import api_client
from services.storage import get_currency_symbol

def DashboardView(page: ft.Page, navigate) -> ft.View:
    transactions = []
    categories = []
    user_info = {}
    is_loading = True
    editing_tx_id = None

    user_greeting = ft.Text("Loading...", size=20, weight=ft.FontWeight.BOLD)
    current_balance_text = ft.Text("0.00", size=32, weight=ft.FontWeight.BOLD, color="#dad7cd")
    
    transaction_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    loading_spinner = ft.ProgressRing(width=22, height=22, visible=True)

    category_dropdown = ft.Dropdown(
        label="Category (Optional)",
        options=[], 
    )
    title_in = ft.TextField(label="Title", autofocus=True)
    
    def toggle_sign(e=None):
        sign_btn.data = not sign_btn.data
        sign_btn.icon = ft.Icons.ADD if sign_btn.data else ft.Icons.REMOVE
        sign_btn.bgcolor = "#a3b18a" if sign_btn.data else "#e76f51"
        sign_btn.update()

    sign_btn = ft.FilledButton(
        "", 
        icon=ft.Icons.REMOVE,
        data=False,
        bgcolor="#e76f51",
        icon_color="#111d13",
        on_click=toggle_sign,
        width=55,
        height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=4),
        )
    )
    
    amount_in = ft.TextField(
        label=f"Amount ({get_currency_symbol()})", 
        keyboard_type=ft.KeyboardType.NUMBER, 
        expand=True
    )
    
    amount_row = ft.Row(
        [sign_btn, amount_in], 
        spacing=10, 
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

    date_in = ft.TextField(
        label="Date (YYYY-MM-DD)",
        value=datetime.now().strftime("%Y-%m-%d"),
    )
    dialog_status = ft.Text("", color=ft.Colors.RED, size=12)
    modal_title = ft.Text("Add Transaction")

    def close_dialog(e=None):
        add_modal.open = False
        page.update()

    def save_transaction(e):
        t_val = title_in.value.strip()
        a_val = amount_in.value.strip().replace(',', '.')
        d_val = date_in.value.strip()
        
        cat_val = None
        if category_dropdown.value:
            cat_val = int(category_dropdown.value)

        if not t_val or not a_val or not d_val:
            dialog_status.value = "Title, Amount, and Date are required."
            page.update()
            return

        try:
            amt_float = float(a_val)
            if not sign_btn.data and amt_float > 0:
                amt_float = -amt_float
            elif sign_btn.data and amt_float < 0:
                amt_float = abs(amt_float)
        except ValueError:
            dialog_status.value = "Enter a valid numeric amount."
            page.update()
            return

        if editing_tx_id is None:
            ok, msg = api_client.create_transaction(t_val, amt_float, d_val, cat_val)
        else:
            ok, msg = api_client.update_transaction(editing_tx_id, t_val, amt_float, d_val, cat_val)

        if ok:
            add_modal.open = False
            page.update()
            load_data()
        else:
            dialog_status.value = f"Failed: {msg}"
            page.update()

    add_modal = ft.AlertDialog(
        title=modal_title,
        content=ft.Column(
            controls=[
                category_dropdown,
                title_in,
                amount_row,
                date_in,
                dialog_status,
            ],
            tight=True,
            spacing=15,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_dialog),
            ft.FilledButton("Save", on_click=save_transaction),
        ],
    )

    def open_add_dialog(e=None):
        nonlocal editing_tx_id
        editing_tx_id = None
        modal_title.value = "Add Transaction"
        amount_in.label = f"Amount ({get_currency_symbol()})"
        
        title_in.value = ""
        amount_in.value = ""
        date_in.value = datetime.now().strftime("%Y-%m-%d")
        dialog_status.value = ""
        category_dropdown.value = None
        
        sign_btn.data = False
        sign_btn.icon = ft.Icons.REMOVE
        sign_btn.bgcolor = "#e76f51"
        
        if add_modal not in page.overlay:
            page.overlay.append(add_modal)
            
        add_modal.open = True
        page.update()

    def edit_item(tx: dict):
        nonlocal editing_tx_id
        editing_tx_id = tx["id"]
        modal_title.value = "Edit Transaction"
        amount_in.label = f"Amount ({get_currency_symbol()})"
        
        title_in.value = tx.get("title", "")
        amt_val = float(tx.get("amount", 0))
        amount_in.value = f"{abs(amt_val):.2f}"
        date_in.value = tx.get("date", datetime.now().strftime("%Y-%m-%d"))
        dialog_status.value = ""
        
        cat_obj = tx.get("category")
        if cat_obj and isinstance(cat_obj, dict):
            category_dropdown.value = str(cat_obj.get("id"))
        else:
            category_dropdown.value = None

        is_income = amt_val >= 0
        sign_btn.data = is_income
        sign_btn.icon = ft.Icons.ADD if is_income else ft.Icons.REMOVE
        sign_btn.bgcolor = "#a3b18a" if is_income else "#e76f51"

        if add_modal not in page.overlay:
            page.overlay.append(add_modal)

        add_modal.open = True
        page.update()

    deleting_tx_id = None
    delete_confirm_text = ft.Text("")

    def close_delete_dialog(e=None):
        delete_modal.open = False
        page.update()

    def confirm_delete(e):
        nonlocal deleting_tx_id
        if deleting_tx_id is not None:
            ok, msg = api_client.delete_transaction(deleting_tx_id)
            delete_modal.open = False
            page.update()
            if ok:
                load_data()
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Failed to delete: {msg}"),
                    bg_color=ft.Colors.RED,
                )
                page.snack_bar.open = True
                page.update()

    delete_modal = ft.AlertDialog(
        title=ft.Text("Confirm Delete"),
        content=delete_confirm_text,
        actions=[
            ft.TextButton("Cancel", on_click=close_delete_dialog),
            ft.FilledButton("Delete", bgcolor=ft.Colors.RED_400, color=ft.Colors.WHITE, on_click=confirm_delete),
        ],
    )

    def prompt_delete(tx: dict):
        nonlocal deleting_tx_id
        deleting_tx_id = tx["id"]
        tx_title = tx.get("title", "this transaction")
        delete_confirm_text.value = f"Are you sure you want to delete '{tx_title}'?"
        
        if delete_modal not in page.overlay:
            page.overlay.append(delete_modal)
            
        delete_modal.open = True
        page.update()

    def load_data(e=None):
        nonlocal transactions, user_info, categories, is_loading
        is_loading = True
        loading_spinner.visible = True
        page.update()

        ok_user, user_res = api_client.get_me()
        if ok_user and isinstance(user_res, dict):
            user_info = user_res
            first_name = user_info.get("first_name")
            username = user_info.get("username", "User")
            user_greeting.value = f"Welcome, {first_name or username}!"
        elif not ok_user and "401" in str(user_res):
            api_client.logout()
            navigate("/login")
            return

        ok_cat, cat_res = api_client.get_categories()
        if ok_cat and isinstance(cat_res, list):
            categories = cat_res
            category_dropdown.options = [
                ft.dropdown.Option(key=str(c["id"]), text=c["name"]) for c in categories
            ]

        ok_tx, tx_res = api_client.get_transactions()
        if ok_tx and isinstance(tx_res, list):
            transactions = tx_res
        else:
            transactions = []

        is_loading = False
        loading_spinner.visible = False
        render_dashboard()

    def render_dashboard():
        curr_symbol = get_currency_symbol()
        total_spent = sum(float(t.get("amount", 0)) for t in transactions)
        current_balance_text.value = f"{total_spent:,.2f} {curr_symbol}"

        transaction_list.controls.clear()

        if not transactions:
            transaction_list.controls.append(
                ft.Container(
                    padding=30,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.RECEIPT_LONG, size=48, color="#a3b18a"),
                            ft.Text("No transactions yet.", color="#a3b18a", size=16),
                            ft.Text("Tap '+' below to add one.", color="#a3b18a", size=12),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                )
            )
        else:
            for tx in transactions:
                cat_name = tx.get("category", {}).get("name") if tx.get("category") else "General"
                amount_val = float(tx.get("amount", 0))

                icon_type = ft.Icons.ADD if amount_val >= 0 else ft.Icons.REMOVE

                transaction_list.controls.append(
                    ft.Card(
                        bgcolor="#344e41",
                        content=ft.Container(
                            padding=14,
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Text(
                                                tx.get("title", "Untitled"),
                                                weight=ft.FontWeight.BOLD,
                                                size=16,
                                                expand=True,
                                            ),
                                            ft.Text(
                                                f"{cat_name} • {tx.get('date', '')}",
                                                size=12,
                                                color="#a3b18a",
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Container(
                                                        padding=6,
                                                        border_radius=8,
                                                        bgcolor="#2a3d32",
                                                        content=ft.Icon(
                                                            icon_type,
                                                            color="#a3b18a",
                                                            size=18,
                                                        ),
                                                    ),
                                                    ft.Text(
                                                        f"{abs(amount_val):,.2f} {curr_symbol}",
                                                        weight=ft.FontWeight.BOLD,
                                                        size=16,
                                                    ),
                                                ],
                                                spacing=10,
                                            ),
                                            ft.Row(
                                                controls=[
                                                    ft.IconButton(
                                                        icon=ft.Icons.EDIT_OUTLINED,
                                                        icon_color="#a3b18a",
                                                        icon_size=20,
                                                        tooltip="Edit",
                                                        on_click=lambda e, item=tx: edit_item(item),
                                                    ),
                                                    ft.IconButton(
                                                        icon=ft.Icons.DELETE_OUTLINED,
                                                        icon_color=ft.Colors.RED_300,
                                                        icon_size=20,
                                                        tooltip="Delete",
                                                        on_click=lambda e, item=tx: prompt_delete(item),
                                                    ),
                                                ],
                                                spacing=0,
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                ],
                                spacing=8,
                            ),
                        ),
                    )
                )

        page.update()

    load_data()

    content_column = ft.Column(
        controls=[
            ft.Container(height=32), 
            ft.Row(
                controls=[
                    ft.Text("Jast", size=24, weight=ft.FontWeight.BOLD, color="#a3b18a"),
                    ft.Row(
                        controls=[
                            loading_spinner,
                            ft.IconButton(
                                icon=ft.Icons.REFRESH,
                                icon_color="#a3b18a",
                                icon_size=20,
                                tooltip="Refresh Data",
                                on_click=load_data,
                            )
                        ],
                        spacing=0,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            user_greeting,
            ft.Container(height=6),
            ft.Card(
                bgcolor="#344e41",
                margin=0, 
                content=ft.Container(
                    padding=20,
                    width=float("inf"), 
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "CURRENT BALANCE",
                                size=12,
                                color="#a3b18a",
                                weight=ft.FontWeight.BOLD,
                            ),
                            current_balance_text,
                        ],
                        spacing=4,
                    ),
                ),
            ),
            ft.Container(height=4),
            ft.Row(
                controls=[
                    ft.FilledButton(
                        "Statistics",
                        icon=ft.Icons.BAR_CHART,
                        color="#dad7cd",
                        bgcolor="#344e41",
                        expand=True,
                        on_click=lambda _: navigate("/statistics"),
                    ),
                    ft.FilledButton(
                        "Account",
                        icon=ft.Icons.ACCOUNT_CIRCLE,
                        color="#dad7cd",
                        bgcolor="#344e41",
                        expand=True,
                        on_click=lambda _: navigate("/account"),
                    ),
                ],
                spacing=10,
            ),
            ft.Container(height=6),
            ft.Text("Recent Transactions", size=18, weight=ft.FontWeight.BOLD),
            transaction_list,
        ],
        spacing=10,
        expand=True,
    )

    return ft.View(
        route="/dashboard",
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        floating_action_button=ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor="#a3b18a",
            foreground_color="#344e41",
            tooltip="Add Transaction",
            on_click=open_add_dialog,
        ),
        controls=[
            ft.Container(
                width=600,
                content=content_column,
                padding=ft.padding.Padding(16, 0, 16, 0),
                expand=True,
            ),
        ],
    )
