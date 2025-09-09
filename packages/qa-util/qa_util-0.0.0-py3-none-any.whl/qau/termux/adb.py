import subprocess

from qau.logging_utils import log


def _adb_forward(serial: str = None):
    cmd = ["adb"]
    if serial:
        cmd += ["-s", serial]
    cmd += ["forward", "tcp:8022", "tcp:8022"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        msg = f"adb forward Fail: {result.stderr.strip()}"
        log.error(msg)
        raise RuntimeError(f"adb forward Fail: {result.stderr.strip()}")
    log.info("adb forward Success")