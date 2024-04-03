from datetime import datetime, timedelta
from airflow import DAG
from docker.types import Mount
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.docker.operators.docker import DockerOperator
import subprocess

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
}


def run_etl_script():
    script_path = "/opt/airflow/etl/etl_script.py"
    result = subprocess.run(["python", script_path],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Script failed with error: {result.stderr}")
    else:
        print(result.stdout)


dag = DAG(
    'etl',
    default_args=default_args,
    description='An ETL workflow',
    start_date=datetime(2024, 4, 3),
    schedule_interval='@weekly',
    catchup=False,
)

t1 = PythonOperator(
    task_id="run_etl_script",
    python_callable=run_etl_script,
    dag=dag
)

t1
