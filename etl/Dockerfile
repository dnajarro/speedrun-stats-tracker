FROM python:3.8-slim

RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    pip install psycopg2 sqlalchemy requests numpy pandas

# RUN apt-get update && apt-get install -y postgresql-client && pip install requests pandas numpy

COPY etl_script.py .

CMD ["python", "etl_script.py"]
