# Ekklesia Voting

Pseudonymous voting component of the Ekklesia e-democracy platform.

## Development

See [Documentation for the Ekklesia project](https://docs.ekklesiademocracy.org/en/latest/development/index.html).


## Tech Stack

- Backend:
  - Main language: [Python 3.11](https://www.python.org)
  - Web framework: [Morepath](http://morepath.readthedocs.org)
  - Testing: [pytest](https://pytest.org),
    [WebTest](https://docs.pylonsproject.org/projects/webtest/en/latest/)
- Frontend
  - Templates [PyPugJS](https://github.com/kakulukia/pypugjs) (similar to [Pug](https://pugjs.org))
    with [Jinja](https://jinja.palletsprojects.com) as template engine.
  - [Sass](https://sass-lang.com) Framework [Bootstrap 4](https://getbootstrap.com)
  - [htmx](https://htmx.org) for "AJAX" requests directly from HTML.
- Database: [PostgreSQL 15](https://www.postgresql.com)
- Dependency management and build tool: [Nix](https://nixos.org/nix)
- Documentation: [Sphinx](https://sphinx-doc.org) with [MyST Markdown](https://myst-parser.readthedocs.io) parser.
- (Optional) Run on NixOS with the included NixOS module
## Development

To get a consistent development environment, we use
[Nix](https://nixos.org/nix) to install Python and the project
dependencies. The development environment also includes PostgreSQL,
code linters, a SASS compiler and pytest for running the tests.

### Development Quick Start

This section describes briefly how to set up a development environment to run a local instance of the application.

Setting up the environment for testing and running tests is described in the
section [Testing](https://docs.ekklesiademocracy.org/en/latest/development/testing.html)
in the Ekklesia documentation.

The following instructions assume that *Nix* is already installed, has Nix
flakes enabled, and an empty + writable PostgreSQL database can be accessed somehow.

If you don't have *Nix* with Flakes support and or can’t use an existing
PostgreSQL server, have a look at the [Development Environment](https://docs.ekklesiademocracy.org/en/latest/development/dev_env.html)
section in the Ekklesia documentation.

It's strongly recommended to also follow the instructions at
[Setting up the Cachix Binary Cache](https://docs.ekklesiademocracy.org/en/latest/development/dev_env.html#setting-up-the-cachix-binary-cache)
or the first step will take a long time to complete.

1. Clone the repository and enter nix shell in the project root folder to open a shell which is
   your dev environment:

   ```
   git clone https://github.com/edemocracy/ekklesia-voting
   cd ekklesia-voting
   nix develop --impure
   ```

2. Compile translations and CSS (look at `dodo.py` to see what this does):

   ```
   doit
   ```

3. Create a config file named `config.yml` using the config template
   from `src/ekklesia_voting/config.example.yml` or skip this to use
   the default settings from `ekklesia_voting/app.py`, `ekklesia_common/app.py`
   and `ekklesia_common/ekklesia_auth.py`.
   Make sure that the database connection string points to an
   empty + writable database.

4. Set up the dev database (look at `flake.nix` to see what this does):

   ```
   create_dev_db
   ```

5. Run the development server (look at `flake.nix` to see what this does):
   ```
   run_dev
   ```

Run `dev_help` to see all commonly used dev shell commands

## License

AGPLv3, see LICENSE

## Authors

* Tobias 'dpausp'
