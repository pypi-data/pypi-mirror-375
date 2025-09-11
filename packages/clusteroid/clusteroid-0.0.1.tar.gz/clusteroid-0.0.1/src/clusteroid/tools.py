import json
import logging
import shlex
import subprocess

log = logging.getLogger("clusteroid")

def run_cmd(cmd, app=None, expect_json=False):
    parts = shlex.split(cmd)
    log.debug("exec %s", " ".join(parts))
    try:
        p = subprocess.run(
            parts,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True)
    except Exception as e:
        log.error(e)
        if app is not None:
            app.notify(str(e), severity="error", title=cmd)
        return
    if expect_json:
        try:
            loaded = json.loads(p.stdout)
        except Exception as e:
            log.error(e)
            if app is not None:
                app.notify(str(e), severity="warning", title=cmd)
            return
        return loaded
    return p.stdout

