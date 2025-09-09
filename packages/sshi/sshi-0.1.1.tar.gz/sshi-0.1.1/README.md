# sshi

`sshi` is a tiny SSH instance manager that lets you store your cloud/server SSH details in a simple JSON inventory and connect to them quickly.

## Features

- Store SSH instances with `name`, `host`, `user`, `port`, `key`, and optional `jump` host.
- SSH into servers with `sshi <name>`.
- Run remote commands with `sshi <name> -- <command>`.
- List all instances with `sshi ls`.
- Add or remove instances: `sshi add`, `sshi rm`.
- Show or edit stored entries: `sshi show`, `sshi edit`.
- Quick connectivity check: `sshi test <name>`.
- Copy files with `sshi scp <name> SRC DST` (use `:` prefix for remote paths).

## Installation

### From Source

```bash
git clone https://github.com/jacobsun000/sshi.git
cd sshi
uv build
uv pip install dist/*.whl
```

### From PyPI (once published)

```bash
uv pip install sshi
```

This installs the `sshi` CLI into your environment.

## Usage

### Add a server

```bash
sshi add proj1-prod --host 12.34.56.78 --user ubuntu --key ~/.ssh/proj1-prod.pem --tags prod aws
```

### SSH into server

```bash
sshi proj1-prod
```

### Run remote command

```bash
sshi proj1-prod -- uptime
```

### List all servers

```bash
sshi ls
```

### Copy files

```bash
# local -> remote
sshi scp proj1-prod ./local.txt :/tmp/remote.txt

# remote -> local
sshi scp proj1-prod :/var/log/syslog ./syslog
```

### Connectivity test

```bash
sshi test proj1-prod
```

### Edit inventory manually

```bash
sshi edit
```

This opens the JSON file (by default: `~/.config/sshi/instances.json`) in your `$EDITOR`.

## Configuration File

Instances are stored in:

```
~/.config/sshi/instances.json
```

Example:

```json
{
  "instances": {
    "proj1-prod": {
      "host": "12.34.56.78",
      "user": "ubuntu",
      "port": 22,
      "key": "~/.ssh/proj1-prod.pem",
      "jump": "ubuntu@bastion.example.com",
      "tags": ["prod", "aws"]
    }
  }
}
```

## Development

Clone and install locally in editable mode:

```bash
git clone https://github.com/jacobsun000/sshi.git
cd sshi
uv pip install -e .
```

Run directly:

```bash
uv run sshi ls
```

## License

MIT License
