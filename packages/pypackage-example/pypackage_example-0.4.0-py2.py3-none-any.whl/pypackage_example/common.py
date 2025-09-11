"""The common module contains common functions and classes used by the other modules."""


def hello_world():
    """Prints "Hello World!" to the console."""
    print("Hello World!")


def create_basemap_widget(map_instance, basemap_options=None):
    """
    Creates a dropdown widget for selecting and switching basemaps on an ipyleaflet map.

    The widget includes a toggle button to show/hide the dropdown, a dropdown menu to select basemaps,
    and a close button to hide the menu. When a new basemap is selected, it calls `map_instance.add_basemap2`
    with the selected basemap name.

    Args:
        map_instance (ipyleaflet.Map): The map instance to update when the basemap is changed.

    Returns:
        ipywidgets.HBox: A widget containing the toggle button, dropdown, and close button for basemap selection.
    """
    import ipywidgets as widgets

    if basemap_options is None:
        basemap_options = [
            "OpenStreetMap.Mapnik",
            "CartoDB.Positron",
            "CartoDB.DarkMatter",
            "OpenTopoMap",
            "Esri.WorldImagery",
        ]

    toggle = widgets.ToggleButton(
        value=False,
        button_style="",  # 'success', 'info', 'warning', 'danger' or ''
        tooltip="Click to toggle",
        icon="map",  # (FontAwesome names without the `fa-` prefix)
        layout=widgets.Layout(width="40px", height="40px"),
    )

    close_button = widgets.Button(
        icon="times",
        layout=widgets.Layout(width="40px", height="40px"),
    )

    dropdown = widgets.Dropdown(
        options=basemap_options,
        value=basemap_options[0],
        description="Basemap:",
    )

    basemap_gui = widgets.HBox([toggle, dropdown, close_button])

    def on_toggle_change(change):
        if change["new"]:
            basemap_gui.children = [toggle, dropdown, close_button]
        else:
            basemap_gui.children = [toggle]

    def on_close_click(b):
        # basemap_gui.children = [toggle]
        # toggle.value = False
        basemap_gui.close()
        toggle.close()
        dropdown.close()
        close_button.close()

    def on_dropdown_change(change):
        if change["new"]:
            map_instance.layers = map_instance.layers[:-2]
            map_instance.add_basemap2(change["new"])

    toggle.observe(on_toggle_change, names="value")
    close_button.on_click(on_close_click)
    dropdown.observe(on_dropdown_change, names="value")

    return basemap_gui
