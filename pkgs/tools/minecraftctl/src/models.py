from dataclasses import dataclass
from typing import Literal, Union


@dataclass
class TmuxConfig:
    socketPath: str


@dataclass
class TmuxManagement:
    type: Literal["tmux"]
    tmux: TmuxConfig


@dataclass
class SystemdStdinSocketConfig:
    path: str


@dataclass
class SystemdSocketConfig:
    stdinSocket: SystemdStdinSocketConfig


@dataclass
class SystemdSocketManagement:
    type: Literal["systemd-socket"]
    systemdSocket: SystemdSocketConfig


ManagementSystem = Union[TmuxManagement, SystemdSocketManagement]

MCServerType = Literal["vanilla", "fabric", "legacy fabric", "quilt", "paper"]


@dataclass
class MinecraftServer:
    name: str
    type: MCServerType
    mcVersion: str
    port: int
    dataDir: str
    serviceName: str
    managementSystem: ManagementSystem


ServersJson = dict[str, MinecraftServer]
