import os

_SERVERS_JSON_DEFAULT_PATH = "/run/minecraft/servers.json"
serversJsonPath = (
    os.environ.get("NIX_MINECRAFT_MINECRAFTCTL_SERVERS_JSON")
    or _SERVERS_JSON_DEFAULT_PATH
)
