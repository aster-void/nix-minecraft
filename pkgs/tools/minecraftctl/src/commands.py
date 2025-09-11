from utils import fatal, load_servers_json
import argparse, os
from typing import List
import requests

from models import MinecraftServer, ServersJson
from utils import (
    get_service_status,
    pretty_table,
    printerr,
    get_instance,
    run,
    get_instance,
)

main_parser = argparse.ArgumentParser()
commands_parser = main_parser.add_subparsers(dest="command", required=False)

def help_cmd(_args):
    printerr(
        """
minecraftctl: A minecraft instance controller for nix-minecraft

Usage: minecraftctl <command>

Commands:
  help                       show help
  list                       list available minecraft instances
  status <instance>          show status of the instance
  tail <instance>            tail the log of the instance
  send <instance> <command>  send command to the instance
  start <instance>           start the server
  stop <instance>            stop the server
  restart <instance>         restart the server
  uuid <player>              get the uuid of a player
"""
    )
main_parser.set_defaults(func=help_cmd)
help_parser = commands_parser.add_parser("help")
help_parser.set_defaults(func=help_cmd)


def list_cmd(_args):
    servers = load_servers_json()
    headers = ["NAME", "VERSION", "LOADER", "PORT", "STATUS"]
    result: List[List[str]] = []
    for cfg in servers.values():
        cfg = MinecraftServer(**cfg)
        status = get_service_status(cfg.serviceName)
        row = [cfg.name, cfg.mcVersion, cfg.type, cfg.port, status]
        result.append(row)

    if len(result) == 0:
        print("No servers found.")
    else:
        print(pretty_table(headers, result))

list_parser = commands_parser.add_parser("list")
list_parser.set_defaults(func=list_cmd)


def status_cmd(args):
    servers = load_servers_json()
    cfg = get_instance(servers, args.instance)
    run(["systemctl", "status", cfg.serviceName])

status_parser = commands_parser.add_parser("status")
status_parser.add_argument("instance")
status_parser.set_defaults(func=status_cmd)


def send_cmd(args):
    servers = load_servers_json()
    cfg = get_instance(servers, args.instance)
    match cfg.managementSystem.type:
        case "tmux":
            command = " ".join(args[1:]) + "\n"
            run(
                [
                    "tmux",
                    "send-keys",
                    "-S",
                    f"{cfg.managementSystem.tmux.socketPath}",
                    command,
                    "Enter",
                ]
            )
        case "systemd-socket":
            stdin = " ".join(args[1:]) + "\n"
            run(
                [
                    "socat",
                    "-",
                    f"UNIX-CONNECT:{cfg.managementSystem.systemdSocket.stdinSocket.path}",
                ],
                stdin=stdin,
            )
        case unknown:
            fatal(f"Unknown management system: {unknown}")

send_parser = commands_parser.add_parser("send")
send_parser.add_argument("instance")
send_parser.add_argument("command", nargs=argparse.REMAINDER)
send_parser.set_defaults(func=send_cmd)


def tail_cmd(args):
    servers = load_servers_json()

    log_file = get_instance(servers, args.instance).dataDir + "/logs/latest.log"
    tail_args = [log_file]

    if args.follow or args.F:
        tail_args += ["--follow"]
    if args.retry or args.F:
        tail_args += ["--retry"]
    tail_args += ["--lines", str(args.lines)]

    if not os.path.isfile(log_file) and not (args.F or (args.follow and args.retry)):
        fatal(f"Log file not found: {log_file}")
    try:
        run(["tail"] + tail_args)
    except KeyboardInterrupt:
        pass

tail_parser = commands_parser.add_parser("tail")
tail_parser.add_argument("instance")
tail_parser.add_argument("-f", "--follow", action="store_true")
tail_parser.add_argument("--retry", action="store_true")
tail_parser.add_argument("-F", action="store_true")
tail_parser.add_argument("-n", "--lines", type=int, default=50)
tail_parser.set_defaults(func=tail_cmd)


def restart_cmd(args):
    servers = load_servers_json()
    service = get_instance(servers, args.instance).serviceName
    run(["systemctl", "restart", service])

restart_parser = commands_parser.add_parser("restart")
restart_parser.add_argument("instance")
restart_parser.set_defaults(func=restart_cmd)


def start_cmd(args):
    servers = load_servers_json()
    service = get_instance(servers, args.instance).serviceName
    run(["systemctl", "start", service])

start_parser = commands_parser.add_parser("start")
start_parser.add_argument("instance")
start_parser.set_defaults(func=start_cmd)


def stop_cmd(args):
    servers = load_servers_json()
    service = get_instance(servers, args.instance).serviceName
    run(["systemctl", "stop", service])

stop_parser = commands_parser.add_parser("stop")
stop_parser.add_argument("instance")
stop_parser.set_defaults(func=stop_cmd)


def uuid_cmd(args):
    player = args.player
    resp = requests.get(
        f"https://api.mojang.com/users/profiles/minecraft/{player}"
    ).json()
    if "errorMessage" in resp:
        fatal(resp["errorMessage"])
    else:
        id = resp["id"]  # without dashes
        uuid = f"{id[:8]}-{id[8:12]}-{id[12:16]}-{id[16:20]}-{id[20:32]}"
        name = resp["name"]
        match args.format:
            case "plain":
                print(f"uuid for {resp['name']} is {uuid}")
            case "json":
                import json

                print(json.dumps({"name": name, "uuid": uuid}, indent=2))

uuid_parser = commands_parser.add_parser("uuid")
uuid_parser.add_argument("player")
uuid_parser.add_argument("--format", "-f", choices=["plain", "json"], default="plain")
uuid_parser.set_defaults(func=uuid_cmd)