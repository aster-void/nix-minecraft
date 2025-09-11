{ python313 }:
let
  py = python313;
in
py.pkgs.buildPythonApplication {
  name = "minecraftctl";
  pyproject = true;
  src = ./.;
  nativeBuildInputs = [ py.pkgs.setuptools ];
  propagatedBuildInputs = with py.pkgs; [ requests ];
  pythonImportsCheck = [ "main" ];
}
