"""Shared helpers for the sftp-upload scripts: credentials, venv, connection."""
import configparser, os, stat, subprocess, sys
from pathlib import Path

VENV = Path.home() / ".local/share/ai-tools/venv"
PWFILE = Path.home() / ".password"
DEFAULT_HOST = "andrealorenzani.name"


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


def remote_dir(host, d):
    rdir = (d if d is not None else f"{host}/ai").strip("/")
    if ".." in rdir.split("/"):
        die("remote dir must not contain '..'")
    return rdir


def real_host(host, section, s):
    return s.get("host", host if section != host else section)


def connect(host, trust_new=False):
    """Return (client, real_host). Host key checked against ~/.ssh/known_hosts."""
    section, s = load_creds(host)
    ensure_paramiko()
    import paramiko
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy() if trust_new else paramiko.RejectPolicy())
    h = real_host(host, section, s)
    try:
        client.connect(h, port=s.getint("port", 22), username=s["user"], password=s["password"],
                       look_for_keys=False, allow_agent=False, timeout=20)
    except paramiko.SSHException as e:
        die(f"connection failed: {e} (unknown host key? run trust_host.py --host {host}, check the fingerprint with the user, then rerun with --yes)")
    except Exception as e:
        die(f"connection failed: {type(e).__name__}")
    return client, h
