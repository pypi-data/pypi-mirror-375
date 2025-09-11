from clusteroid.ceph import cluster_facts
from clusteroid.ui_tools import table_save_pos, table_load_pos
from textual.widgets import DataTable
import humanize


class PoolTable(DataTable):
    REFRESH_EVERY = 1  # seconds

    def on_mount(self) -> None:
        self.add_columns("ID", "NAME", "PGS", "S/M", "RULE", "AUTOSCALE", "EC", "APP", "OBJ", "USED", "%USED", "AVAIL")
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.refresh_table()
        self.set_interval(self.REFRESH_EVERY, self.refresh_table)

    def refresh_table(self) -> None:
        table_pos = table_save_pos(self)
        df = cluster_facts.df
        osd_pool_ls = cluster_facts.osd_pool_ls
        self.clear()
        if osd_pool_ls is None or df is None:
            return
        for pool in osd_pool_ls:
            pool_id = pool.get("pool_id", "-")
            pool_name = pool.get("pool_name", "-")
            pg_num = pool.get("pg_num", "-")
            min_size_and_size = f'{pool.get("size", "-")}/{pool.get("min_size", "-")}'
            crush_rule_id = pool.get("crush_rule", "-")
            pg_autoscale_mode = pool.get("pg_autoscale_mode", "-")
            ec_profile = pool.get("erasure_code_profile", "-")
            application = ", ".join(pool.get("application_metadata", "-"))
            pool_stats = next((p.get("stats") for p in df.get("pools", {}) if p.get("id") == pool_id), None)
            objects = "-"
            bytes_used = "-"
            percent_used = "-"
            max_available = "-"
            if pool_stats is not None:
                objects = pool_stats.get("objects", "-")
                bytes_used = pool_stats.get("bytes_used", "-")
                percent_used = pool_stats.get("percent_used", "-")
                max_available = pool_stats.get("max_avail", "-")
            self.add_row(
                pool_id,
                pool_name,
                pg_num,
                min_size_and_size,
                crush_rule_id,
                pg_autoscale_mode,
                ec_profile,
                application,
                objects,
                humanize.naturalsize(bytes_used, binary=True),
                percent_used,
                humanize.naturalsize(max_available, binary=True),
            )
        table_load_pos(self, table_pos)

