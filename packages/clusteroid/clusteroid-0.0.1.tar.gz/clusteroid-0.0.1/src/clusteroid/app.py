from clusteroid.config import ConfigTable
from clusteroid.crushmap import OsdTree, CrushRuleTree
from clusteroid.disks import DiskTable
from clusteroid.hosts import Hosts
from clusteroid.metrics import CephStatus
from clusteroid.pools import PoolTable
from clusteroid.services import ServiceTable
from clusteroid.terminal import Terminal
from textual.app import App, ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Footer, Header, Static, TabbedContent, TabPane


class ClusteroidTUI(App):
    TITLE = "Clusteroid"
    CSS = """
    Screen {
        layout: vertical;
    }
    TabbedContent {
        height: 1fr;
    }
    TabPane {
        padding: 1;
    }
    """
    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+f", "run_terminal", "📟 Terminal"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(id="tabs"):
            with TabPane("🗠  Metrics", id="tab-metrics"):
                with VerticalScroll():
                    yield CephStatus()
            with TabPane("🖵  Hosts", id="tab-hosts"):
                yield Hosts()
            with TabPane("🖴  Disks", id="tab-disks"):
                yield DiskTable()
            with TabPane("🧩 Services", id="tab-services"):
                yield ServiceTable()
            with TabPane("🏊 Pools", id="tab-pools"):
                yield PoolTable()
            with TabPane("🧭 Crushmap", id="tab-crushmap"):
                with VerticalScroll():
                    yield OsdTree("")
                    yield CrushRuleTree("Crush Rules")
            with TabPane("🔧 Config", id="tab-config"):
                yield ConfigTable()
        yield Footer()

    async def action_run_terminal(self, cmd=None, title="Terminal") -> None:
        tabs = self.query_one("#tabs", TabbedContent)
        num = 0
        while bool(self.query(f"#tab-terminal-{num}")):
            num += 1
        pane = TabPane(f"📟{num} {title}", Terminal(command=cmd, id=f"terminal-{num}"), id=f"tab-terminal-{num}")
        await tabs.add_pane(pane)

