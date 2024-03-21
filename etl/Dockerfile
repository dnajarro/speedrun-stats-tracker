FROM python:3.8-slim

RUN apt-get update && apt-get install -y postgresql-client && pip3 install srcomapi

COPY etl_script.py .

CMD ["python", "etl_script.py"]
