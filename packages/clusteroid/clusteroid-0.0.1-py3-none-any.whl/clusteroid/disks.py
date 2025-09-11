from clusteroid.ceph import cluster_facts
from clusteroid.ui_tools import table_save_pos, table_load_pos
from rich.text import Text
from textual.widgets import DataTable


class DiskTable(DataTable):
    REFRESH_EVERY = 1  # seconds

    def on_mount(self) -> None:
        self.add_columns("HOST", "PATH", "TYPE", "SIZE", "AVAILABLE", "DEVICE ID")
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.refresh_table()
        self.set_interval(self.REFRESH_EVERY, self.refresh_table)

    def refresh_table(self) -> None:
        table_pos = table_save_pos(self)
        dev_tree = cluster_facts.orch_device_ls
        self.clear()
        if dev_tree is None:
            return
        for host in dev_tree:
            for device in host.get("devices", []):
                self.add_row(
                    host.get("name", host.get("addr", "-")),
                    device.get("path", "-"),
                    Text(device.get("human_readable_type", "-"), justify="right"),
                    Text(device.get("sys_api", {}).get("human_readable_size", "-"), justify="right"),
                    Text("✅" if device.get("available", False) else "🚫", justify="center"),
                    device.get("device_id", "-"),
                )
        table_load_pos(self, table_pos)

