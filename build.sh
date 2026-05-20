set -o errexit

poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main

python manage.py collectstatic --no-input

python manage.py migrate
