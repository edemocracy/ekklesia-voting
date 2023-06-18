# This Flake uses devenv and flake-parts.
# https://devenv.sh
# https://flake.parts
# https://devenv.sh/guides/using-with-flake-parts/
{
  description = "ekklesia-voting";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.11";
    devenv.url = "github:cachix/devenv";
    poetry2nix = {
      url = "github:dpausp/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    mk-shell-bin.url = "github:rrbutani/nix-mk-shell-bin";
  };

  outputs = inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [
        inputs.devenv.flakeModule
        inputs.flake-parts.flakeModules.easyOverlay
      ];
      systems = [ "x86_64-linux" "x86_64-darwin" "aarch64-darwin" ];

      perSystem = { config, self', inputs', pkgs, system, ... }:
        let
          deps = import ./nix/deps.nix {
            poetry2nix = inputs'.poetry2nix.legacyPackages;
            poetry = inputs'.poetry2nix.packages.poetry;
            inherit pkgs;
          };

          app = pkgs.callPackage ./nix/app.nix deps;

          serveApp = pkgs.callPackage ./nix/serve_app.nix {
            inherit app;
            inherit (deps) gunicorn;
          };

          staticFiles = pkgs.callPackage ./nix/static_files.nix deps;

          venv = pkgs.buildEnv {
            name = "ekklesia-voting-venv";
            ignoreCollisions = true;
            paths = with deps;
              [ pythonDev ] ++
              linters;
          };
        in
        {
          # Per-system attributes can be defined here. The self' and inputs'
          # module parameters provide easy access to attributes of the same
          # system.
          # The Nix overlay is available as `overlays.default`.
          overlayAttrs = {
            inherit (config.packages)
              ekklesia-voting
              ekklesia-voting-static
              ekklesia-voting-serve-app;
          };

          checks = {
            inherit (config.packages) ekklesia-voting-serve-app;
          };

          formatter = pkgs.nixpkgs-fmt;


          packages = {
            # The `nix run` command uses the `default` attribute here.
            # Runs the application using the `gunicorn` app server.
            default = serveApp;
            # Build Python 'virtualenv'.
            inherit venv;
            # ekklesia-voting-* packages are also exported via the default overlay.
            ekklesia-voting = app;
            ekklesia-voting-static = staticFiles;
            ekklesia-voting-serve-app = serveApp;
          };

          devenv.shells.default =
            {
              name = "ekklesia-voting";
              env = {
                PYTHONPATH = "./src:../ekklesia-common/src";
                JS_PATH = deps.jsPath;
                SASS_PATH = deps.sassPath;
                WEBFONTS_PATH = deps.webfontsPath;
              };

              packages = deps.shellInputs;

              scripts = {
                build_python_venv.exec = ''
                  nix build .#venv -o venv
                  echo "Created directory 'venv' which is similar to a Python virtualenv."
                  echo "Provides linters and a Python interpreter with runtime dependencies and test tools."
                  echo "The 'venv' should be picked up py IDE as a possible project interpreter (restart may be required)."
                  echo "Tested with VSCode, Pycharm."
                '';
                run_dev.exec = ''
                  python src/ekklesia_voting/runserver.py -b localhost --reload -p 8080 -c config.yml | tee run_dev.log.json | eliot-tree -l0
                '';
                debug_dev.exec = ''
                  python src/ekklesia_voting/runserver.py -b localhost -p 8080 -c config.yml --debug
                '';
                create_dev_db.exec = ''
                  python tests/create_test_db.py --config-file config.yml
                '';
                create_test_db.exec = ''
                  python tests/create_test_db.py
                '';
                doit_auto.exec = ''
                  echo "Recompiling CSS and translation files if source files change..."
                  ls src/ekklesia_voting/translations/*/*/*.po src/ekklesia_voting/sass/*.sass | entr doit
                '';
                help.exec = ''
                  cat << END
                  # Development Shell Commands
                  (standard tools + commands defined in flake.nix)

                  ## Basic
                  doit                     Build CSS and translation files (once).
                  create_test_db           Set up PostgreSQL database for testing, using config.yml.
                  pytest                   Run Python test suite.
                  run_dev                  Run application in dev mode with formatted log output.

                  ## Development
                  doit_auto                Build CSS and translation files (when inputs change).
                  doit babel_extractupdate Extract translatable strings from code.
                  debug_dev                Debug application in dev mode (use this with breakpoints).
                  build_python_venv        Build 'virtualenv' for IDE integration.
                  console                  Run IPython REPL for interaction with application objects.
                  END
                '';
              };
            };

        };

      flake = {
        # The usual flake attributes can be defined here, including system-
        # agnostic ones like nixosModule and system-enumerating ones, although
        # those are more easily expressed in perSystem.

        # Using this NixOS module requires the default overlay from here.
        # Example, when `ekklesiaVoting` is the Flake:
        # nixpkgs.overlays = [ ekklesiaVoting.overlays.default ];
        # imports = [ ekklesiaVoting.nixosModules.default ];
        nixosModules.default = import nix/modules/default.nix;
      };
    };
}
