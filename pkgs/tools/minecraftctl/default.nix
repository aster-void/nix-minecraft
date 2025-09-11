{ lib, python313, socat, tmux, coreutils, pyright }:
let
  py = python313;
in
py.pkgs.buildPythonApplication {
  name = "minecraftctl";
  pyproject = true;
  src = ./.;
  nativeBuildInputs = [ py.pkgs.setuptools ];
  propagatedBuildInputs = [
    py.pkgs.httpx
    py.pkgs.typer
    py.pkgs.pydantic
  ];
  buildInputs = [
    socat # systemd-socket
    tmux  # tmux
    coreutils # tail
  ];

  pythonImportsCheck = [ "minecraftctl.main" ];

  checkPhase = ''
    ${lib.getExe py.pkgs.black} .
    ${lib.getExe pyright} minecraftctl
  '';
}
