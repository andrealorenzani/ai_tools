#!/usr/bin/env python3
"""Add a host's SSH key to ~/.ssh/known_hosts. Shows the fingerprint; adds only with --yes.

Usage: trust_host.py [--host andrealorenzani.name] [--yes]
Refuses if known_hosts already holds a DIFFERENT key for the host (possible MITM).
"""
import argparse, os, socket, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEFAULT_HOST, die, ensure_paramiko, load_creds, real_host  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--yes", action="store_true", help="write to known_hosts (user must have confirmed the fingerprint)")
    a = ap.parse_args()

    section, s = load_creds(a.host)  # only for host/port; password not used
    ensure_paramiko()
    import paramiko, base64, hashlib

    host, port = real_host(a.host, section, s), s.getint("port", 22)
    try:
        t = paramiko.Transport(socket.create_connection((host, port), timeout=20))
        t.start_client(timeout=20)
        key = t.get_remote_server_key()
        t.close()
    except Exception as e:
        die(f"cannot fetch host key: {type(e).__name__}")

    fp = "SHA256:" + base64.b64encode(hashlib.sha256(key.asbytes()).digest()).decode().rstrip("=")
    print(f"{host}:{port} {key.get_name()} {fp}")

    kh = Path.home() / ".ssh/known_hosts"
    name = host if port == 22 else f"[{host}]:{port}"
    hk = paramiko.HostKeys()
    if kh.exists():
        hk.load(str(kh))
    old = hk.lookup(name)
    if old is not None:
        if old.get(key.get_name()) == key:
            print("already trusted; nothing to do")
            return
        if key.get_name() in old.keys():
            die("known_hosts has a DIFFERENT key for this host: possible MITM or server change. Not touching it; tell the user")
    if not a.yes:
        print("dry run: verify the fingerprint with the user, then rerun with --yes")
        return
    kh.parent.mkdir(mode=0o700, exist_ok=True)
    with open(kh, "a") as f:  # append only: never rewrite the user's file
        f.write(f"{name} {key.get_name()} {key.get_base64()}\n")
    os.chmod(kh, 0o600)
    print(f"added {name} to {kh}")


if __name__ == "__main__":
    main()
