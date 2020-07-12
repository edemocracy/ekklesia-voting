#!/usr/bin/env -S nix-build -o serve_app
{ sources ? null,
  appConfigFile ? null,
  listen ? "127.0.0.1:8080",
  tmpdir ? null
}:
let
  ekklesia-voting = import ../. { inherit sources; };
  inherit (ekklesia-voting) dependencyEnv deps;
  inherit (deps) pkgs gunicorn lib;
  pythonpath = "${dependencyEnv}/${dependencyEnv.sitePackages}";

  gunicornConf = pkgs.writeText
                "gunicorn_config.py"
                (import ./gunicorn_config.py.nix {
                   inherit listen pythonpath;
                });

  runGunicorn = pkgs.writeShellScriptBin "run" ''
    app_config=${if appConfigFile == null then "`pwd`/$1" else appConfigFile}
    ${lib.optionalString (tmpdir != null) "export TMPDIR=${tmpdir}"}

    ${gunicorn}/bin/gunicorn -c ${gunicornConf} \
      "ekklesia_voting.app:make_wsgi_app(settings_filepath='$app_config')"
  '';

in pkgs.buildEnv {
  name = "ekklesia-voting-serve-app";
  paths = [ runGunicorn ];
}
