from clusteroid.ceph import cluster_facts
from clusteroid.ui_tools import table_save_pos, table_load_pos
from textual.widgets import DataTable


class ConfigTable(DataTable):
    REFRESH_EVERY = 1  # seconds

    def on_mount(self) -> None:
        self.add_columns("SECTION", "NAME", "VALUE", "UPDATES AT RUNTIME")
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.refresh_table()
        self.set_interval(self.REFRESH_EVERY, self.refresh_table)

    def refresh_table(self) -> None:
        table_pos = table_save_pos(self)
        config_dump = cluster_facts.config_dump
        self.clear()
        if config_dump is None:
            return
        for c in config_dump:
            self.add_row(
                c.get("section", "-"),
                c.get("name", "-"),
                c.get("value", "-"),
                c.get("can_update_at_runtime", "-"),
                )
        table_load_pos(self, table_pos)

