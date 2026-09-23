import flet as ft
import flet_charts as fch

def StatisticsView(page: ft.Page, navigate, app_storage, api_client) -> ft.View:
    transactions = []
    is_loading = True

    PIE_COLORS = [
        "#56B4E9",
        "#E69F00",
        "#009E73",
        "#CC79A7",
        "#F0E442",
        "#D55E00",
        "#0072B2",
    ]

    loading_spinner = ft.ProgressRing(width=22, height=22, visible=True)
    chart_container = ft.Container(alignment=ft.Alignment.CENTER, height=300)
    legend_column = ft.Column(spacing=10)

    callout_text = ft.Text(
        "Tap or hover over a section to view details",
        size=13,
        color="#a3b18a",
        weight=ft.FontWeight.W_500,
        text_align=ft.TextAlign.CENTER,
    )
    
    speech_bubble = ft.Container(
        content=callout_text,
        bgcolor="#344e41",
        padding=ft.padding.Padding(16, 10, 16, 10),
        border_radius=12,
        alignment=ft.Alignment.CENTER,
        border=ft.Border.all(1, "#588157"),
    )

    def load_data():
        nonlocal transactions, is_loading
        is_loading = True
        loading_spinner.visible = True
        page.update()

        ok_tx, tx_res = api_client.get_transactions()
        if ok_tx and isinstance(tx_res, list):
            transactions = tx_res
        else:
            transactions = []

        is_loading = False
        loading_spinner.visible = False
        render_statistics()

    def render_statistics():
        curr_symbol = app_storage.get_currency_symbol()
        category_totals = {}
        total_expenses = 0.0

        for tx in transactions:
            amt = float(tx.get("amount", 0))
            if amt < 0:
                cat_name = tx.get("category", {}).get("name") if tx.get("category") else "General"
                abs_amt = abs(amt)
                category_totals[cat_name] = category_totals.get(cat_name, 0) + abs_amt
                total_expenses += abs_amt

        chart_container.content = None
        legend_column.controls.clear()

        if total_expenses == 0:
            chart_container.content = ft.Column(
                controls=[
                    ft.Icon(ft.Icons.PIE_CHART_OUTLINE, size=48, color="#a3b18a"),
                    ft.Text("No expense data to display.", color="#a3b18a"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            )
            page.update()
            return

        sorted_categories = sorted(category_totals.items(), key=lambda item: item[1], reverse=True)

        display_categories = []
        if len(sorted_categories) > 6:
            display_categories = sorted_categories[:6]
            other_total = sum(amount for _, amount in sorted_categories[6:])
            if other_total > 0:
                display_categories.append(("Other", other_total))
        else:
            display_categories = sorted_categories

        sections = []
        chart_data = []

        for index, (cat_name, amount) in enumerate(display_categories):
            color = PIE_COLORS[index]
            percentage = (amount / total_expenses) * 100
            
            chart_data.append({
                "cat_name": cat_name, 
                "amount": amount, 
                "percentage": percentage,
                "color": color
            })

            sections.append(
                fch.PieChartSection(
                    value=amount,
                    title=f"{percentage:.0f}%",
                    title_style=ft.TextStyle(size=13, color="#111d13", weight=ft.FontWeight.BOLD),
                    color=color,
                    radius=80,
                )
            )

            legend_column.controls.append(
                ft.Card(
                    bgcolor="#344e41",
                    margin=0,
                    content=ft.Container(
                        padding=12,
                        content=ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Container(width=12, height=12, border_radius=6, bgcolor=color),
                                        ft.Text(cat_name, weight=ft.FontWeight.BOLD, size=14),
                                    ],
                                    spacing=10,
                                ),
                                ft.Text(f"{amount:,.2f} {curr_symbol}", weight=ft.FontWeight.BOLD, size=14),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        )
                    )
                )
            )

        def on_chart_event(e):
            hovered_index = getattr(e, "section_index", -1)
            if hovered_index is None:
                hovered_index = -1
            
            if 0 <= hovered_index < len(chart_data):
                selected = chart_data[hovered_index]
                callout_text.value = f"{selected['cat_name']}: {selected['amount']:,.2f} {curr_symbol} ({selected['percentage']:.1f}%)"
                callout_text.color = "#dad7cd"
                speech_bubble.border = ft.Border.all(1.5, selected["color"])
            else:
                callout_text.value = "Tap or hover over a section to view details"
                callout_text.color = "#a3b18a"
                speech_bubble.border = ft.Border.all(1, "#588157")

            for idx, section in enumerate(pie_chart.sections):
                if idx == hovered_index:
                    section.radius = 98
                else:
                    section.radius = 80

            speech_bubble.update()
            pie_chart.update()

        pie_chart = fch.PieChart(
            sections=sections,
            sections_space=3,
            center_space_radius=45,
            expand=True,
            on_event=on_chart_event,
        )
        chart_container.content = pie_chart

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
                                icon=ft.Icons.ARROW_BACK,
                                icon_color="#a3b18a",
                                icon_size=20,
                                tooltip="Back to Dashboard",
                                on_click=lambda _: navigate("/dashboard"),
                            ),
                        ],
                        spacing=0,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Text("Statistics", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            speech_bubble,
            ft.Container(height=10),
            chart_container,
            ft.Container(height=10),
            ft.Text("Spending by Category", size=18, weight=ft.FontWeight.BOLD),
            legend_column,
        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    return ft.View(
        route="/statistics",
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
