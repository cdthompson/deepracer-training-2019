"""
Submit models to DeepRacer Virtual Circuit.  This
DAG does not stage the model, but simply resubmits
whichever model is staged already.
"""

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
import deepracer_console as dr

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2019, 10, 10),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

# 30 minutes is enforced backoff but I have seen
# it take just a bit longer
deepracer_submit_dag = DAG('deepracer_submit', 
    schedule_interval=timedelta(minutes=35),
    catchup=False,
    default_args=default_args)

def submit_model():
    return dr.deepracer_submit_model_to_virtual_race('NOV',
                                           Variable.get('aws-console-account-id'),
                                           Variable.get('aws-console-username'),
                                           Variable.get('aws-console-password'))

submit_operator = PythonOperator(
    task_id='submit_model',
    python_callable=submit_model,
    dag=deepracer_submit_dag)

# TODO: Later we can make this job spin until the submitted model has been evaluated and we receive results
