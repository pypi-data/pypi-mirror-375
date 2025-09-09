import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

APP_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "inst"
INV_PATH = APP_DIR / "instances.json"

DEFAULTS = {
    "port": 22,
    "user": "root",
    "key": None,
    "host": None,
    "jump": None,
    "tags": [],
}


def ensure_inventory():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    if not INV_PATH.exists():
        INV_PATH.write_text(json.dumps({"instances": {}}, indent=2))


def load():
    ensure_inventory()
    try:
        return json.loads(INV_PATH.read_text())
    except Exception as e:
        sys.exit(f"Failed to read {INV_PATH}: {e}")


def save(data):
    INV_PATH.write_text(json.dumps(data, indent=2))


def norm_path(p):
    if not p:
        return None
    return os.path.expandvars(os.path.expanduser(p))


def resolve_name(data, name):
    insts = data["instances"]
    if name in insts:
        return name
    # simple fuzzy: unique substring match
    matches = [k for k in insts if name.lower() in k.lower()]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        sys.exit(f"Ambiguous name '{name}': {', '.join(matches)}")
    sys.exit(f"Unknown instance '{name}'. Use 'ls' to see names.")


def ssh_cmd(entry, extra_cmd=None):
    host = entry.get("host")
    if not host:
        sys.exit("Instance has no 'host' set.")
    user = entry.get("user") or DEFAULTS["user"]
    port = entry.get("port") or DEFAULTS["port"]
    key = norm_path(entry.get("key"))
    jump = entry.get("jump")
    cmd = ["ssh", "-p", str(port)]
    if key:
        cmd += ["-i", key]
    if jump:
        cmd += ["-J", jump]
    cmd += [f"{user}@{host}"]
    if extra_cmd:
        # allow passing a remote command after '--'
        cmd += extra_cmd
    return cmd


def do_ls(data, args):
    rows = []
    for name, e in data["instances"].items():
        host = e.get("host", "?")
        user = e.get("user") or DEFAULTS["user"]
        port = e.get("port") or DEFAULTS["port"]
        tags = ",".join(e.get("tags", []))
        rows.append((name, f"{user}@{host}:{port}", tags))
    if not rows:
        print(
            "No instances stored. Add one with: ./inst add NAME --host HOST --user USER --key PATH"
        )
        return
    width = max(len(r[0]) for r in rows)
    print("NAME".ljust(width), "ADDRESS".ljust(28), "TAGS")
    print("-" * width, "-" * 28, "-" * 20)
    for n, addr, tags in sorted(rows):
        print(n.ljust(width), addr.ljust(28), tags)


def do_add(data, args):
    name = args.name
    if name in data["instances"] and not args.force:
        sys.exit(f"Instance '{name}' already exists. Use --force to overwrite.")
    entry = {
        "host": args.host,
        "user": args.user or DEFAULTS["user"],
        "port": args.port or DEFAULTS["port"],
        "key": args.key,
        "jump": args.jump,
        "tags": args.tags or [],
    }
    data["instances"][name] = entry
    save(data)
    print(f"Saved '{name}'. Try: ./inst {name}")


def do_rm(data, args):
    name = resolve_name(data, args.name)
    del data["instances"][name]
    save(data)
    print(f"Removed '{name}'.")


def do_show(data, args):
    name = resolve_name(data, args.name)
    print(json.dumps(data["instances"][name], indent=2))


def do_edit(_data, _args):
    ensure_inventory()
    editor = (
        os.environ.get("EDITOR")
        or os.environ.get("VISUAL")
        or ("notepad" if os.name == "nt" else "vi")
    )
    subprocess.call([editor, str(INV_PATH)])


def do_ssh(data, args):
    name = resolve_name(data, args.name)
    entry = data["instances"][name]
    extra = args.remote_cmd
    cmd = ssh_cmd(entry, extra_cmd=extra)
    os.execvp(cmd[0], cmd)  # replace current process


def do_test(data, args):
    name = resolve_name(data, args.name)
    entry = data["instances"][name]
    cmd = ssh_cmd(entry, extra_cmd=["echo", "ok"])
    cmd = cmd[:1] + ["-o", "BatchMode=yes", "-o", "ConnectTimeout=5"] + cmd[1:]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        print(out.strip())
    except subprocess.CalledProcessError as e:
        print(e.output.strip())
        sys.exit(e.returncode or 1)


def do_scp(data, args):
    """
    scp helper:
      ./inst scp NAME LOCAL REMOTE
    If REMOTE starts with ':', it's remote path on the instance.
    If LOCAL starts with ':', it pulls from remote to local.
    """
    name = resolve_name(data, args.name)
    e = data["instances"][name]
    host = e.get("host")
    user = e.get("user") or DEFAULTS["user"]
    port = e.get("port") or DEFAULTS["port"]
    key = norm_path(e.get("key"))
    jump = e.get("jump")
    base = ["scp", "-P", str(port)]
    if key:
        base += ["-i", key]
    if jump:
        base += ["-o", f"ProxyJump={jump}"]

    def mk_remote(path):
        return f"{user}@{host}:{path}"

    src, dst = args.src, args.dst
    if src.startswith(":"):
        src = mk_remote(src[1:])
    if dst.startswith(":"):
        dst = mk_remote(dst[1:])
    cmd = base + [src, dst]
    # print(" ".join(shlex.quote(c) for c in cmd))
    os.execvp(cmd[0], cmd)


def main():
    ensure_inventory()
    data = load()
    p = argparse.ArgumentParser(prog="inst", description="Tiny SSH instance manager")
    sub = p.add_subparsers(dest="cmd")

    p_ls = sub.add_parser("ls", help="List instances")
    p_ls.set_defaults(func=do_ls)

    p_add = sub.add_parser("add", help="Add/update an instance")
    p_add.add_argument("name")
    p_add.add_argument("--host", required=True)
    p_add.add_argument("--user")
    p_add.add_argument("--port", type=int)
    p_add.add_argument("--key", help="Path to private key (e.g. ~/.ssh/proj1-prod.pem)")
    p_add.add_argument("--jump", help="SSH jump host (user@bastion)")
    p_add.add_argument("--tags", nargs="*", help="Tags to help organize")
    p_add.add_argument("--force", action="store_true")
    p_add.set_defaults(func=do_add)

    p_rm = sub.add_parser("rm", help="Remove an instance")
    p_rm.add_argument("name")
    p_rm.set_defaults(func=do_rm)

    p_show = sub.add_parser("show", help="Show one instance JSON")
    p_show.add_argument("name")
    p_show.set_defaults(func=do_show)

    p_edit = sub.add_parser("edit", help=f"Open inventory in $EDITOR ({INV_PATH})")
    p_edit.set_defaults(func=do_edit)

    p_test = sub.add_parser("test", help="Quick connectivity check")
    p_test.add_argument("name")
    p_test.set_defaults(func=do_test)

    p_scp = sub.add_parser("scp", help="scp via a stored instance")
    p_scp.add_argument("name")
    p_scp.add_argument("src")
    p_scp.add_argument("dst")
    p_scp.set_defaults(func=do_scp)

    # default action: first arg is NAME (plus optional remote command after --)
    p_ssh = sub.add_parser("ssh", help="SSH into instance (usually you can omit 'ssh')")
    p_ssh.add_argument("name")
    p_ssh.add_argument(
        "remote_cmd",
        nargs=argparse.REMAINDER,
        help="Command to run remotely (prefix with --)",
    )
    p_ssh.set_defaults(func=do_ssh)

    # Allow ./inst NAME [-- remote cmd]
    if len(sys.argv) >= 2 and sys.argv[1] not in {
        None,
        "ls",
        "add",
        "rm",
        "edit",
        "show",
        "scp",
        "test",
        "ssh",
        "-h",
        "--help",
    }:
        # Rewrite argv to call 'ssh'
        sys.argv = [sys.argv[0], "ssh"] + sys.argv[1:]

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        sys.exit(0)
    args.func(data, args)


if __name__ == "__main__":
    main()
