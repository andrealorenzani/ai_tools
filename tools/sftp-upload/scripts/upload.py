#!/usr/bin/env python3
"""Upload a file to a host over SFTP. Credentials from ~/.password (INI, chmod 600).

Usage: upload.py FILE [--host andrealorenzani.name] [--dir ai] [--force] [--trust-new-host]
"""
import argparse, configparser, os, posixpath, stat, subprocess, sys
from pathlib import Path

VENV = Path.home() / ".local/share/ai-tools/venv"
PWFILE = Path.home() / ".password"


def die(msg):
    sys.exit(f"error: {msg}")


def ensure_paramiko():
    try:
        import paramiko  # noqa: F401
        return
    except ImportError:
        pass
    py = VENV / "bin/python"
    if os.environ.get("_SFTP_UPLOAD_REEXEC"):
        die("paramiko unavailable even in venv")
    if not py.exists():
        print(f"creating venv {VENV} and installing paramiko...", file=sys.stderr)
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV)])
        subprocess.check_call([str(py), "-m", "pip", "install", "-q", "paramiko"])
    os.environ["_SFTP_UPLOAD_REEXEC"] = "1"
    os.execv(str(py), [str(py), *sys.argv])


def load_creds(host):
    if not PWFILE.exists():
        die(f"{PWFILE} missing. Create it with a [{host}] section (host/user/password), chmod 600")
    if PWFILE.stat().st_mode & (stat.S_IRWXG | stat.S_IRWXO):
        die(f"{PWFILE} must be chmod 600")
    cp = configparser.ConfigParser(interpolation=None)
    cp.read(PWFILE)
    labels = host.split(".")
    for i in range(len(labels) - 1):  # exact host first, then parent domains
        name = ".".join(labels[i:])
        if cp.has_section(name):
            s = cp[name]
            if not s.get("user") or not s.get("password"):
                die(f"[{name}] in {PWFILE} needs user and password")
            return name, s
    die(f"no section for {host} (or parent domain) in {PWFILE}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--host", default="andrealorenzani.name")
    ap.add_argument("--dir", default="ai", help="remote dir, relative to login dir")
    ap.add_argument("--force", action="store_true", help="overwrite existing remote file")
    ap.add_argument("--trust-new-host", action="store_true", help="accept unknown host key (first connect only)")
    a = ap.parse_args()

    src = Path(a.file).expanduser()
    if not src.is_file():
        die(f"{src} is not a file")
    rdir = a.dir.strip("/")
    if ".." in rdir.split("/"):
        die("remote dir must not contain '..'")

    section, s = load_creds(a.host)
    ensure_paramiko()
    import paramiko

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy() if a.trust_new_host else paramiko.RejectPolicy())
    host = s.get("host", a.host if section != a.host else section)
    try:
        client.connect(host, port=s.getint("port", 22), username=s["user"], password=s["password"],
                       look_for_keys=False, allow_agent=False, timeout=20)
    except paramiko.SSHException as e:
        die(f"connection failed: {e} (unknown host key? retry once with --trust-new-host if you trust {host})")
    except Exception as e:
        die(f"connection failed: {type(e).__name__}")

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
