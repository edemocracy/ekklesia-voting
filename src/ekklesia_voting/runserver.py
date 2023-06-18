import argparse
import datetime
import glob
import os
import os.path
import sys
import tempfile

import werkzeug.serving
from eliot import log_message
from werkzeug.middleware.shared_data import SharedDataMiddleware

tmpdir = tempfile.gettempdir()
parser = argparse.ArgumentParser("Ekklesia Voting runserver.py")

parser.add_argument(
    "-b",
    "--bind",
    default="localhost",
    help="hostname / IP to bind to, default ekklesia-voting-localhost",
)
parser.add_argument(
    "-p", "--http_port", default=8080, type=int, help="HTTP port to use, default 8080"
)
parser.add_argument(
    "-d", "--debug", action="store_true", help="enable werkzeug debugger / reloader"
)
parser.add_argument("-r", "--reload", action="store_true", help="enable code reload")
parser.add_argument(
    "-c", "--config-file", help=f"path to config file in YAML / JSON format"
)


def run():
    from ekklesia_voting.app import make_wsgi_app

    args = parser.parse_args()
    wsgi_app = make_wsgi_app(args.config_file)

    wrapped_app = SharedDataMiddleware(
        wsgi_app,
        {
            "/static": ("ekklesia_voting", "static"),
            "/static/debug": ("ekklesia_common.debug", "static"),
            "/static/deform": ("deform", "static"),
            "/static/webfonts": os.environ.get("WEBFONTS_PATH"),
            "/static/js": os.environ.get("JS_PATH"),
        },
    )

    if args.debug:
        # use ipdb as default breakpoint() hook (Python 3.7 feature)
        try:
            import ipdb
        except ImportError:
            pass
        else:
            sys.breakpointhook = ipdb.set_trace
    else:

        def breakpoint_in_production(*args, **kwargs):
            pass

        sys.breakpointhook = breakpoint_in_production

    with open(os.path.join(tmpdir, "ekklesia_voting.started"), "w") as wf:
        wf.write(datetime.datetime.now().isoformat())
        wf.write("\n")

    # reload when translation MO files change
    extra_reload_files = glob.glob(
        "src/ekklesia_voting/translations/**/*.mo", recursive=True
    )
    if args.config_file is not None:
        extra_reload_files.append(args.config_file)

    log_message("werkzeug-reload-extra", extra_reload_files=extra_reload_files)

    werkzeug.serving.run_simple(
        args.bind,
        args.http_port,
        wrapped_app,
        use_reloader=args.debug or args.reload,
        extra_files=extra_reload_files,
        use_debugger=args.debug,
    )


if __name__ == "__main__":
    run()
