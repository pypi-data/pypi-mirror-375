from clusteroid.ceph import cluster_facts
from textual.widgets import Static

class CephStatus(Static):
    REFRESH_EVERY = 1  # seconds

    def on_mount(self) -> None:
        self.refresh_text()
        self.set_interval(self.REFRESH_EVERY, self.refresh_text)

    def refresh_text(self) -> None:
        status = cluster_facts.status
        self.update(str(status))

