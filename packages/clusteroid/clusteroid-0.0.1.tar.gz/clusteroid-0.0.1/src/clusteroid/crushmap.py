from clusteroid.ceph import cluster_facts
from clusteroid.ui_tools import table_save_pos, table_load_pos
from textual.widgets import DataTable, Tree, Static
import json

class CrushRuleTree(Tree):
    REFRESH_EVERY = 1  # seconds

    def on_mount(self) -> None:
        self.refresh_tree()
        self.set_interval(self.REFRESH_EVERY, self.refresh_tree)

    def refresh_tree(self) -> None:
        crush = cluster_facts.osd_crush_dump
        self.clear()
        if crush is None:
            return
        rules = crush.get("rules", [])
        self.add_json(rules)
        self.root.expand_all()


class OsdTree(Static):
    REFRESH_EVERY = 1  # seconds

    def on_mount(self) -> None:
        self.refresh_text()
        self.set_interval(self.REFRESH_EVERY, self.refresh_text)

    def refresh_text(self) -> None:
        osd_tree = cluster_facts.osd_tree
        self.update(str(osd_tree))

