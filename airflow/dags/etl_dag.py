# from datetime import datetime, timedelta
# from airflow import DAG
# from docker.types import Mount
# from airflow.operators.python_operator import PythonOperator
# from airflow.operators.bash import BashOperator
# from airflow.providers.docker.operators.docker import DockerOperator
# import subprocess

# default_args = {
#     'owner': 'airflow',
#     'depends_on_past': False,
#     'email_on_failure': False,
#     'email_on_retry': False,
# }


# def run_etl_script():
#     script_path = "/opt/airflow/etl/elt_script.py"
#     result = subprocess.run(["python", script_path],
#                             capture_output=True, text=True)
#     if result.returncode != 0:
#         raise Exception(f"Script failed with error: {result.stderr}")
#     else:
#         print(result.stdout)


# dag = DAG(
#     'elt_and_dbt',
#     default_args=default_args,
#     description='An ETL workflow with dbt',
#     start_date=datetime(2023, 10, 29),
#     catchup=False,
# )

# t1 = PythonOperator(
#     task_id="run_etl_script",
#     python_callable=run_etl_script,
#     dag=dag
# )

# t2 = DockerOperator(
#     task_id="dbt_run",
#     image='ghcr.io/dbt-labs/dbt-postgres:1.4.7',
#     command=[
#         "run",
#         "--profiles-dir",
#         "/root",
#         "--project-dir",
#         "/opt/dbt"
#     ],
#     auto_remove=True,
#     docker_url="unix://var/run/docker.sock",
#     network_mode="bridge",
#     mounts=[
#         Mount(source='{location_of_postgres_db}',
#               target='/opt/dbt', type='bind'),
#         Mount(source='{location_of_dbt_hidden_file}',
#               target='/root', type='bind')
#     ],
#     dag=dag
# )

# t1 >> t2
