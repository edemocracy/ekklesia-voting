let
  pkgs = import ./requirements/nixpkgs.nix;
in pkgs.stdenv.mkDerivation {
  src = null;
  name = "ekklesia_voting";
  phases = [];
  buildInputs = with pkgs.python37Packages; [ pkgs.sassc pyflakes pkgs.pipenv pkgs.zsh pkgs.postgresql100 python  ];
  #shellHook = "PYTHONPATH= SHELL=`which zsh` pipenv shell --fancy";
}
