FROM python:3.11-slim



WORKDIR /app

RUN apt-get update && apt-get install -y \

    gcc \

    python3-dev \

    libpq-dev \

    && rm -rf /var/lib/apt/lists/*

COPY requirements/ /app/requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

COPY . /app/

RUN groupadd -r django && useradd -r -g django django && \

    chown -R django:django /app



USER django

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


