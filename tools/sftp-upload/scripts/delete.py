#!/usr/bin/env python3
"""Delete files from a host over SFTP. Dry run unless --yes.

Usage: delete.py NAME... [--host andrealorenzani.name] [--dir <host>/ai] [--rmdir] [--yes]
NAME is a file name inside --dir (no slashes). --rmdir also removes --dir itself if empty.
"""
import argparse, posixpath, stat, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEFAULT_HOST, connect, die, remote_dir  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", help="file names inside --dir")
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--dir", default=None, help="remote dir, relative to login dir (default: <host>/ai)")
    ap.add_argument("--rmdir", action="store_true", help="also remove --dir if it ends up empty")
    ap.add_argument("--yes", action="store_true", help="really delete (user must have confirmed); default is dry run")
    ap.add_argument("--list", action="store_true", help="list --dir and exit")
    a = ap.parse_args()

    rdir = remote_dir(a.host, a.dir)
    if not rdir:
        die("refusing to operate on the login dir; give --dir")
    if not a.names and not a.list and not a.rmdir:
        die("give file names, --list or --rmdir")
    for n in a.names:
        if "/" in n or n in (".", "..") or any(c in n for c in "*?[]"):
            die(f"bad name '{n}': plain file names only, no slashes or wildcards")

    client, host = connect(a.host)
    with client.open_sftp() as sftp:
        try:
            entries = {e.filename: e for e in sftp.listdir_attr(rdir)}
        except FileNotFoundError:
            die(f"{rdir} not found on {host}")
        if a.list:
            for n, e in sorted(entries.items()):
                print(("d " if stat.S_ISDIR(e.st_mode) else "- ") + n)
            return
        for n in a.names:
            if n not in entries:
                die(f"{rdir}/{n} not found on {host}")
            if stat.S_ISDIR(entries[n].st_mode):
                die(f"{rdir}/{n} is a directory; only files are deleted")
        remaining = set(entries) - set(a.names)
        if a.rmdir and remaining:
            die(f"--rmdir: {rdir} would still hold {len(remaining)} item(s); not removing it")
        verb = "deleted" if a.yes else "would delete"
        for n in a.names:
            p = posixpath.join(rdir, n)
            if a.yes:
                sftp.remove(p)
            print(f"{verb} {host}:{p}")
        if a.rmdir:
            if a.yes:
                sftp.rmdir(rdir)
            print(f"{verb} {host}:{rdir}/")
    client.close()
    if not a.yes:
        print("dry run: rerun with --yes after the user confirms")


if __name__ == "__main__":
    main()
