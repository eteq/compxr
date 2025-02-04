{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages (python-pkgs: with python-pkgs; [
      numpy
      scipy
      matplotlib
      jupyterlab
      python-uinput
    ]))
  ];


  shellHook = ''
    export LD_LIBRARY_PATH=$HOME/src/viture_one_linux_sdk_1.0.7/libs
  '';
}
