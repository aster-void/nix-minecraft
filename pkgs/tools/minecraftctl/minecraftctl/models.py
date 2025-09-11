from typing import Literal, Union
from pydantic import BaseModel, RootModel

class TmuxConfig(BaseModel):
    socketPath: str


class TmuxManagement(BaseModel):
    type: Literal["tmux"]
    tmux: TmuxConfig


class SystemdStdinSocketConfig(BaseModel):
    path: str


class SystemdSocketConfig(BaseModel):
    stdinSocket: SystemdStdinSocketConfig


class SystemdSocketManagement(BaseModel):
    type: Literal["systemd-socket"]
    systemdSocket: SystemdSocketConfig


ManagementSystem = Union[TmuxManagement, SystemdSocketManagement]

MCServerType = Literal[
    "vanilla",
    "fabric",
    "legacy fabric", "quilt", "paper", "velocity"]


class MinecraftServer(BaseModel):
    name: str
    type: MCServerType
    mcVersion: str | None # velocity doesn't have a mcVersion
    port: int
    dataDir: str
    serviceName: str
    managementSystem: ManagementSystem

class InternalServersJson(RootModel[dict[str, MinecraftServer]]):
    pass

class ServersJson:
    _dict: dict[str, MinecraftServer]

    def __init__(self, json: dict[str, MinecraftServer]):
        self._dict = InternalServersJson.model_validate(json).root

    def __getitem__(self, key: str) -> MinecraftServer:
        return self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def values(self):
        return self._dict.values()