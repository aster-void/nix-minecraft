import os
from typing import Any, List

import httpx
import typer

from .utils import (
    fatal,
    get_service_status,
    pretty_table,
    exec,
)
from .config import load_servers_json

app = typer.Typer(help="Minecraft server management tool")


@app.callback(invoke_without_command=True)
def init(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command(help="list available minecraft instances")
def list():
    servers = load_servers_json()
    headers = ["NAME", "VERSION", "LOADER", "PORT", "STATUS"]
    result: List[List[Any]] = []
    for cfg in servers.values():
        status = get_service_status(cfg.serviceName)
        row: List[Any] = [cfg.name, cfg.mcVersion, cfg.type, cfg.port, status]
        result.append(row)

    if len(result) == 0:
        print("No servers found.")
    else:
        print(pretty_table(headers, result))


@app.command(help="show the status of the instance")
def status(instance: str):
    servers = load_servers_json()
    cfg = servers[instance]
    exec(["systemctl", "status", cfg.serviceName, "--no-pager"])


@app.command(help="send a command to the instance")
def send(instance: str, command: List[str] = typer.Argument(...)):
    servers = load_servers_json()
    cfg = servers[instance]
    if cfg.managementSystem.type == "tmux":
        cmd = " ".join(command)
        exec(
            [
                "tmux",
                "send-keys",
                "-S",
                f"{cfg.managementSystem.tmux.socketPath}",
                cmd,
                "Enter",
            ]
        )
    elif cfg.managementSystem.type == "systemd-socket":
        stdin = " ".join(command) + "\n"
        exec(
            [
                "socat",
                "-",
                f"UNIX-CONNECT:{cfg.managementSystem.systemdSocket.stdinSocket.path}",
            ],
            stdin=stdin,
        )
    else:
        fatal(f"Unknown management system: {cfg.managementSystem.type}")


@app.command(help="tail the log of the instance")
def tail(
    instance: str,
    follow: bool = False,
    retry: bool = False,
    F: bool = False,
    lines: int = 50,
):
    servers = load_servers_json()
    log_file = servers[instance].dataDir + "/logs/latest.log"
    tail_args = [log_file]

    do_follow = follow or F
    do_retry = (follow and retry) or F

    if do_follow:
        tail_args += ["--follow"]
    if do_retry:
        tail_args += ["--retry"]
    tail_args += ["--lines", str(lines)]

    if not os.path.isfile(log_file) and not do_retry:
        fatal(f"Log file not found: {log_file}")
    try:
        exec(["tail"] + tail_args)
    except KeyboardInterrupt:
        pass


@app.command(help="restart the systemd service of the instance")
def restart(instance: str):
    servers = load_servers_json()
    service = servers[instance].serviceName
    exec(["systemctl", "restart", service])


@app.command(help="start the systemd service of the instance")
def start(instance: str):
    servers = load_servers_json()
    service = servers[instance].serviceName
    exec(["systemctl", "start", service])


@app.command(help="stop the systemd service of the instance")
def stop(instance: str):
    servers = load_servers_json()
    service = servers[instance].serviceName
    exec(["systemctl", "stop", service])


@app.command(help="get the uuid of a player")
def uuid(player: str, format: str = "human"):
    resp = httpx.get(f"https://api.mojang.com/users/profiles/minecraft/{player}").json()
    if "errorMessage" in resp:
        fatal(resp["errorMessage"])
    else:
        id = resp["id"]  # without dashes
        uuid: str = f"{id[:8]}-{id[8:12]}-{id[12:16]}-{id[16:20]}-{id[20:32]}"
        name = resp["name"]
        match format:
            case "human":
                print(f"uuid for {resp['name']} is {uuid}")
            case "json":
                import json

                print(json.dumps({"name": name, "uuid": uuid}, indent=2))
            case "text":
                print(uuid)
            case unknown:
                fatal(f"Unknown format: {unknown}")

@app.command(help="get the name history of a player by uuid")
def test():
    exec(["systemctl", "status", "avahi-daemon"])

if __name__ == "__main__":
    app()
