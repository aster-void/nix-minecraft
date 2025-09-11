{ python313 }:
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
  pythonImportsCheck = [ "minecraftctl.main" ];
}
