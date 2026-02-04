import os
import urllib.parse
from dotenv import load_dotenv

######### Experiment database parameters ############

# Load variables from .env if present
load_dotenv()

fit_name = "FIT"
run_name = "RUN"

# --- Database name ---
db_name = os.getenv("MONGO_DB_NAME", "fit_data_test")

# --- Strategy 1: direct MONGO_URI override ---
MONGO_URI = os.getenv("MONGO_URI")

# --- Strategy 2: compose a simple or auth URI ---
use_auth = os.getenv("MONGO_USE_AUTH", "0").lower() in ("1", "true", "yes")
host = os.getenv("MONGO_HOST", "127.0.0.1")
port = os.getenv("MONGO_PORT", "27017")
auth_source = os.getenv("MONGO_AUTH_SOURCE", "admin")
username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASSWORD")

if MONGO_URI:
	mongo_uri = MONGO_URI
else:
	if use_auth:
		if not username or not password:
			raise RuntimeError(
				"MONGO_USE_AUTH=1 but MONGO_USERNAME/MONGO_PASSWORD not set"
			)
		pw_q = urllib.parse.quote_plus(password)
		mongo_uri = (
			f"mongodb://{username}:{pw_q}@{host}:{port}/{db_name}?authSource={auth_source}"
		)
	else:
		mongo_uri = f"mongodb://{host}:{port}/{db_name}"

# Examples:
# 1) Simple local (no auth):
#    MONGO_HOST=127.0.0.1
#    MONGO_PORT=27017
#    MONGO_DB_NAME=fit_data_test
#    MONGO_USE_AUTH=0
#
# 2) Auth local/remote:
#    MONGO_HOST=127.0.0.1
#    MONGO_PORT=27017
#    MONGO_DB_NAME=fit_data_prod
#    MONGO_USE_AUTH=1
#    MONGO_AUTH_SOURCE=admin
#    MONGO_USERNAME=your_user
#    MONGO_PASSWORD=your_password
#
# 3) Full URI override (Atlas or standard):
#    MONGO_URI=mongodb+srv://user:pass@cluster.example.mongodb.net

