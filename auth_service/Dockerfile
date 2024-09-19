FROM python:3.12

ARG AUTH_CONFIG__RUN__PORT

# Runtime environment variable (available in the container), default to 8000 if not set
ENV AUTH_CONFIG__RUN__PORT=${AUTH_CONFIG__RUN__PORT:-8000}

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Run alembic migrations and start the app using gunicorn
CMD ["bash", "-c", "alembic upgrade head && gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${AUTH_CONFIG__RUN__PORT}"]
