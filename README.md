<div align="center">

# ModelXplorer

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](#)
[![Built with Dash](https://img.shields.io/badge/Built%20with-Dash-20BEFF.svg)](https://dash.plotly.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-brightgreen.svg)](#docker-deployment)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#contributing)

</div>

ModelXplorer is a Dash application to explore, fit, and analyze Ordinary Differential Equations. It supports interactive single-trace fitting (onefit) and batch dataset fits, with optional experiment tracking in MongoDB via Sacred and visualization in Omniboard.


![alt text](figure_papier_webapp.png)

## Features

- Interactive single-trace fitting (onefit mode)
- Batch fitting across uploaded datasets (batch mode)
- Sacred experiment tracking and optional Omniboard dashboard
- Clean Dash UI with Bootstrap styling
- Waitress production server

## Quick start

### Local (Python 3.11+)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

# Optional: set app mode (onefit | batch)
echo "APP_VERSION=onefit" >> .env

python index.py
```

App default: http://127.0.0.1:8050

### Docker Compose

```bash
cp .env.example .env  # then edit
docker compose up -d --build
```

- App: http://localhost:8050
- Omniboard: http://localhost:9000

## Configuration

Copy `.env.example` to `.env` in the project root.

Root-only authentication (recommended for this stack):

```dotenv
MONGO_DB_NAME=fit_data_test
MONGO_DB=fit_data_test
PORT=8050

# Root credentials for MongoDB (used by both app and Omniboard)
MONGO_ROOT_USER=root
MONGO_ROOT_PASSWORD=changeme_admin

# App auth mapping (handled by compose):
MONGO_USE_AUTH=1
MONGO_AUTH_SOURCE=admin
MONGO_USERNAME=${MONGO_ROOT_USER}
MONGO_PASSWORD=${MONGO_ROOT_PASSWORD}
```

Full URI override (e.g., Atlas):

```dotenv
MONGO_URI=mongodb+srv://user:pass@cluster.example.mongodb.net
```

App modes (set in `.env`):

```dotenv
APP_VERSION=onefit  # or: batch
```

Internally, `config/config.py` reads `APP_VERSION` and defaults to `onefit` if invalid.

## Project structure

```
app.py                 # Dash app instance
index.py               # Entrypoint (Waitress + mode selection + Omniboard optional)
layouts/               # UI layouts
callbacks/             # Dash callbacks (onefit, batch, dataset, system)
model_new.py           # NPQ model
fit_params_parallel.py # Fitting routines
tools.py               # Utilities (plotting, file IO, normalization)
config/params.py       # MongoDB config (env-driven)
Dockerfile             # App image
docker-compose.yml     # App + Mongo + Omniboard stack
```

## Dependencies & notes

- `pdf2image` requires Poppler installed and on PATH (Windows: add `bin` to PATH).
- LaTeX image generation requires `pdflatex`.
  - Docker image includes TeX Live and enables images by default (`DISABLE_LATEX_IMAGE=0`).
  - Bare metal: install TeX Live or set `DISABLE_LATEX_IMAGE=1` to skip.
- Sacred + Omniboard requires a reachable MongoDB.
- App uses Waitress in `index.py`.


## Workflow

- Branches: `main` (stable), feature branches for changes; current working branch example: `docker`.
- Releases & tags: use semantic versioning (e.g., `v1.2.0`).
### Pushing a Git tag

Use annotated tags for releases so you can include a message and signature.

1. Create an annotated tag locally

  ```bash
  git tag -a v1.2.3 -m "Release v1.2.3"
  ```

2. Push a single tag to origin

  ```bash
  git push origin v1.2.3
  ```

  Or push all local tags:

  ```bash
  git push --tags
  ```

3. Verify the tag exists on the remote

  ```bash
  git ls-remote --tags origin
  ```

4. Update (force-move) a tag — use with caution

  ```bash
  git tag -f v1.2.3
  git push --force origin v1.2.3
  ```

5. Delete a tag (local and remote)

  ```bash
  git tag -d v1.2.3
  git push origin :refs/tags/v1.2.3
  ```

6. Create a GitHub release (optional)

  - Web UI: open the tag on GitHub → “Draft a new release”
  - CLI (requires GitHub CLI):

    ```bash
    gh release create v1.2.3 --notes "Changelog and highlights"
    ```

Tips:

- Keep tag names consistent (`vMAJOR.MINOR.PATCH`).
- Tag the commit on the main branch you intend to release.
- CI/CD can be triggered on tags to build and publish release artifacts.

- Commits: keep small, descriptive messages; consider Conventional Commits for clarity.
  - Example:
    - `fix(callbacks): correct outputs and safer batch concurrency`
    - `chore(docker): remove app healthcheck`
    - `refactor(index): fail-safe Omniboard startup`

## Contributing

We welcome pull requests!

1. Fork the repo and create a feature branch.
2. Make focused changes with clear commit messages.
3. Update README or docs when behavior changes.
4. Open a PR; include screenshots or logs when relevant.

Issue triage:

- Use labels: `bug`, `enhancement`, `docs`, `question`.
- Provide steps to reproduce and environment details.

## Security

- Do not commit secrets: keep `.env` out of version control (it’s ignored).
- In Docker, MongoDB is unexposed by default; the app connects via the compose network.
- Use MongoDB authentication in production (`SCRAM-SHA-256`, TLS for remote).
- Run containers as non-root (Dockerfile config).

## Troubleshooting

- Omniboard not found: install globally (`npm i -g omniboard`) or set `OMNIBOARD_DISABLE=1`.
- MongoDB auth errors: verify `MONGO_AUTH_SOURCE` and credentials.
- `pdf2image` issues: ensure Poppler is installed and on PATH.
- See logs for app mode selection; set `CONFIG_DEBUG=1` to print selected mode.

## License

GPL-3.0. See [LICENSE](LICENSE).

## Acknowledgements

- Built with [Dash](https://dash.plotly.com), [SciPy](https://scipy.org/), [Sacred](https://github.com/IDSIA/sacred), and [Omniboard](https://github.com/vivekratnavel/omniboard).
