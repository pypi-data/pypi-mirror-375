from clusteroid.ceph import cluster_facts
from clusteroid.ui_tools import table_save_pos, table_load_pos
from textual.widgets import DataTable, Button
from textual.containers import Horizontal, Vertical, HorizontalScroll

class HostTable(DataTable):
    REFRESH_EVERY = 1  # seconds

    def on_mount(self) -> None:
        self.add_columns("Hostname", "IP address", "CPU", "RAM", "HDD", "SSD")
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.refresh_table()
        self.set_interval(self.REFRESH_EVERY, self.refresh_table)

    def refresh_table(self) -> None:
        table_pos = table_save_pos(self)
        hosts = cluster_facts.orch_host_ls
        self.clear()
        if hosts is None:
            return
        for host in hosts:
            self.add_row(
                host.get("hostname", "-"),
                host.get("addr", "-"),
                host.get("cpu_summary", "-"),
                host.get("ram", "-"),
                host.get("hdd_summary", "-"),
                host.get("ssd_summary", "-"),
            )
        table_load_pos(self, table_pos)

class Toolbar(Horizontal):
    DEFAULT_CSS="""
    Toolbar {
        height: 4;
    }
    Toolbar Button {
        margin: 0 1 0 0;
    }
    """
    def compose(self):
        yield Button("➕ Add", id="btn-host-add", tooltip="Add new host.")
        yield Button("➖ Remove", id="btn-host-remove", tooltip="Remove selected host.")
        yield Button("📟 SSH", id="btn-host-ssh", tooltip="SSH to selected host.")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-host-ssh":
            table = self.app.query_one("#host-table", DataTable)
            row_id = table.cursor_row
            ip = table.get_row_at(row_id)[1]
            hostname = table.get_row_at(row_id)[0]
            await self.app.action_run_terminal(cmd=f"ssh {ip}", title=hostname)

class Hosts(Vertical):
    def compose(self):
        yield Toolbar()
        yield HostTable(id="host-table")

