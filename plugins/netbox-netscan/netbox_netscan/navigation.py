from netbox.plugins import PluginMenu, PluginMenuItem


menu = PluginMenu(
    label="Network Scanner",
    groups=(("Discovery", (
        PluginMenuItem(link="plugins:netbox_netscan:dashboard", link_text="Discovered devices"),
        PluginMenuItem(link="plugins:netbox_netscan:map", link_text="Network map"),
    )),),
    icon_class="mdi mdi-radar",
)
