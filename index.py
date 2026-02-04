from app import app
from layouts.layout_main import get_layout
import callbacks
from waitress import serve
from config.config import VERSION
import subprocess
import signal
import sys
import multiprocessing
import shutil
from config.params import db_name
import os
import urllib.parse
from config import params 

# Import des bons callbacks selon la version
if VERSION == "onefit":
    from callbacks import callbacks_dataset, callbacks_onefit
else:
    from callbacks import callbacks_batch

# Définition du layout Dash
app.layout = get_layout()


def start_dash(queue):
    if VERSION == "onefit":
        callbacks_onefit.set_F_queue(queue)
    else:
        callbacks_batch.set_F_queue(queue)

    # Allow overriding host/port via env (useful for Docker)
    host = os.getenv("HOST", "127.0.0.1")
    try:
        port = int(os.getenv("PORT", "8050"))
    except ValueError:
        port = 8050

    serve(app.server, host=host, port=port)


if __name__ == '__main__':
    multiprocessing.set_start_method("spawn", force=True)
    queue = multiprocessing.Queue()
    
    # Optionally disable built-in Omniboard launch (e.g., when using docker-compose)
    disable_omniboard = os.getenv("OMNIBOARD_DISABLE", "0").lower() in ("1", "true", "yes")

    if not disable_omniboard:
        # --- Pick omniboard executable per OS ---
        if sys.platform.startswith("win"):
            omniboard_bin = "omniboard.cmd"
        else:
            omniboard_bin = "omniboard"

        omniboard_path = shutil.which(omniboard_bin)
        if omniboard_path is None:
            print(f"[omniboard] {omniboard_bin} not found in PATH; starting app without Omniboard.")
            disable_omniboard = True

        # --- MongoDB connection string ---
        mongo_uri = getattr(params, "mongo_uri", None)
        if not mongo_uri:
            print("[omniboard] mongo_uri not defined in config.params; starting app without Omniboard.")
            disable_omniboard = True

        # --- Start Omniboard ---
        if not disable_omniboard:
            omniboard_proc = subprocess.Popen(
                [
                    omniboard_path,
                    "--mu", mongo_uri,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        def cleanup(signum, frame):
            print("Stopping Dash and Omniboard...")
            try:
                omniboard_proc.terminate()
            except Exception:
                pass
            sys.exit(0)
    else:
        def cleanup(signum, frame):
            print("Stopping Dash...")
            sys.exit(0)

    # Intercepter Ctrl+C et kill
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    # Lancer Dash
    start_dash(queue)

