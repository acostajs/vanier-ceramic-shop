set -o errexit
uv sync --frozen
uv run manage.py collectstatic --no-input
uv run manage.py migrate --no-input