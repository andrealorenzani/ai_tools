#!/usr/bin/env python3
"""Upload a file to a host over SFTP. Credentials from ~/.password (INI, chmod 600).

Usage: upload.py FILE [--host andrealorenzani.name] [--dir <host>/ai] [--force] [--trust-new-host]
"""
import argparse, posixpath, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEFAULT_HOST, connect, die, remote_dir  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--dir", default=None, help="remote dir, relative to login dir (default: <host>/ai)")
    ap.add_argument("--force", action="store_true", help="overwrite existing remote file")
    ap.add_argument("--trust-new-host", action="store_true", help="accept unknown host key (first connect only; prefer trust_host.py)")
    a = ap.parse_args()

    src = Path(a.file).expanduser()
    if not src.is_file():
        die(f"{src} is not a file")
    rdir = remote_dir(a.host, a.dir)
    client, host = connect(a.host, a.trust_new_host)

    with client.open_sftp() as sftp:
        path = ""
        for part in rdir.split("/") if rdir else []:
            path = posixpath.join(path, part) if path else part
            try:
                sftp.stat(path)
            except FileNotFoundError:
                sftp.mkdir(path)
                print(f"created {path}/")
        remote = posixpath.join(rdir, src.name) if rdir else src.name
        if not a.force:
            try:
                sftp.stat(remote)
                die(f"{remote} exists on {host}; use --force to overwrite")
            except FileNotFoundError:
                pass
        sftp.put(str(src), remote)
    client.close()
    print(f"uploaded {src.name} -> {host}:{remote}")


if __name__ == "__main__":
    main()
