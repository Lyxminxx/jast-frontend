import flet as ft

def forest_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#a3b18a",           # Soft Sage Green
            on_primary="#111d13",        # Dark text on primary
            primary_container="#344e41", # Dark Fern Container
            on_primary_container="#dad7cd",
            secondary="#dda15e",         # Warm Earth/Amber accent
            on_secondary="#111d13",
            surface="#111d13",           # Deep Pine / Charcoal-Green Base
            on_surface="#dad7cd",        # Soft Cream Text
            on_surface_variant="#a3b18a",# Muted Subtext
            outline="#588157",           # Fern Green Borders
            error="#e76f51",             # Terracotta Red
            on_error="#111d13",
        ),
        visual_density=ft.VisualDensity.COMFORTABLE,
    )
