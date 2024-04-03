FROM python:3.8-slim

RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    pip install psycopg2 sqlalchemy requests numpy pandas

COPY etl_script.py .

CMD ["python", "etl_script.py"]
