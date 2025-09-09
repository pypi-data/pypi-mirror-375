from dataclasses import dataclass
import json
import shlex
import subprocess
from typing import Optional

from qau.logging_utils import log


@dataclass
class Capabilities:
    port: Optional[int]
    user: Optional[str]
    ssh_password: Optional[str]
    host: Optional[str]

def run_termux_sms_list(capabilities:Capabilities, limit: int = 1, unread_only: bool = False):
    command = ["termux-sms-list","-l",str(limit)]
    if unread_only:
        command += ['-t',"unread"]

    remote_cmd = " ".join(shlex.quote(x) for x in command)

    ssh_cmd = [
        "sshpass","-p",capabilities.ssh_password,
        "ssh","-o", "StrictHostKeyChecking=no",
        "-p", capabilities.port,
        f"{capabilities.user}@{capabilities.host}",
        remote_cmd,
    ]
    proc = subprocess.run(ssh_cmd,capture_output=True,text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"SSH_ERR: {proc.stderr.strip()}")
    output = proc.stdout.strip()

    try:
        msgs = json.loads(output)
        for m in msgs:
            return m.get('body').split("인증번호")[1].split('를')[0].strip()
    except Exception:
        log.exception("JSON parse error",)
