import threading
import time
from copy import deepcopy
from clusteroid.tools import run_cmd


class Facts:
    _instance = None
    _lock = threading.Lock()  # guards _instance creation

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_once(*args, **kwargs)
        return cls._instance

    def _init_once(self, update_interval=10):
        self.update_interval = update_interval

        # shared state
        self.orch_device_ls = None
        self.orch_host_ls = None
        self.df = None
        self.osd_pool_ls = None
        self.config_dump = None
        self.status = None
        self.orch_ps = None
        self.osd_crush_dump = None
        self.osd_tree = None

        # sync + lifecycle
        self._last_update = None
        self._state_lock = threading.Lock()
        self._stop = threading.Event()
        self._threads = []

        # one thread per command
        self._commands = {
            "orch_device_ls":   "ceph orch device ls --format=json",
            "orch_host_ls":     "ceph orch host ls --detail --format=json",
            "df":               "ceph df detail --format=json",
            "osd_pool_ls":      "ceph osd pool ls detail --format=json",
            "config_dump":      "ceph config dump --format=json",
            "status":           "ceph status",
            "orch_ps":          "ceph orch ps --format=json",
            "osd_crush_dump":   "ceph osd crush dump --format=json",
            "osd_tree":         "ceph osd tree",
        }

        for attr, cmd in self._commands.items():
            t = threading.Thread(
                target=self._cmd_worker, args=(attr, cmd), daemon=True
            )
            t.start()
            self._threads.append(t)

    def _cmd_worker(self, attr, cmd):
        while not self._stop.is_set():
            try:
                result = run_cmd(cmd, expect_json=("--format=json" in cmd))
            except Exception:
                result = None  # swallow and retry next interval

            if result is not None:
                with self._state_lock:
                    setattr(self, attr, result)
                    self._last_update = time.time()
            # sleep, but wake fast if stopping
            self._stop.wait(self.update_interval)


    def stop(self):
        self._stop.set()
        for t in self._threads:
            t.join()


cluster_facts = Facts()

