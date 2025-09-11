from clusteroid.ceph import cluster_facts
from clusteroid.ui_tools import table_save_pos, table_load_pos
from textual.widgets import DataTable
import humanize

class ServiceTable(DataTable):
    REFRESH_EVERY = 1  # seconds

    def on_mount(self) -> None:
        self.add_columns("Name", "Host", "Ports", "Status", "%CPU", "Ram", "Ram limit", "Version")
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.refresh_table()
        self.set_interval(self.REFRESH_EVERY, self.refresh_table)

    def refresh_table(self) -> None:
        table_pos = table_save_pos(self)
        ps = cluster_facts.orch_ps
        self.clear()
        if ps is None:
            return
        for s in ps:
            
            self.add_row(
                s.get("daemon_name", "-"),
                s.get("hostname", "-"),
                ",".join(map(str,s.get("ports", []))),
                s.get("status_desc", "-"),
                s.get("cpu_percentage", "-"),
                humanize.naturalsize(s.get("memory_usage", "0"), binary=True),
                humanize.naturalsize(s.get("memory_request", "0"), binary=True),
                s.get("version", "-"),

            )
        table_load_pos(self, table_pos)

