"""
Monitor the official DeepRace Robomaker image so that we
can react to updates
"""

from airflow import DAG
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator
from airflow.hooks.S3_hook import S3Hook
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2015, 6, 1),
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

monitor_deepracer_simapp_dag = DAG('monitor_deepracer_simapp', 
    schedule_interval=timedelta(minutes=30),
    catchup=False,
    default_args=default_args)

def s3_head(bucket, key):
    # s3://deepracer-managed-resources-us-east-1/deepracer-simapp.tar.gz
    return S3Hook().get_conn().head_object(
        Bucket=bucket,
        Key=key)

def compare_modified_dates():
    DEEPRACER_MANAGED_BUCKET = 'deepracer-managed-resources-us-east-1'
    DEEPRACER_MANAGED_KEY = 'deepracer-simapp.tar.gz'
    OWNED_BUCKET = 'aws-deepracer-b6c3c104-eef5-4878-a257-d981cd204d62'
    OWNED_KEY = 'deepracer-simapp-custom.tar.gz'
    source = s3_head(DEEPRACER_MANAGED_BUCKET, DEEPRACER_MANAGED_KEY)
    dest = s3_head(OWNED_BUCKET, OWNED_KEY)
    source_modified = parsedate_to_datetime(source['ResponseMetadata']['HTTPHeaders']['last-modified'])
    print("source last-modified")
    print(source_modified)
    dest_modified = parsedate_to_datetime(dest['ResponseMetadata']['HTTPHeaders']['last-modified'])
    print("dest last-modified")
    print(dest_modified)
    if (source_modified < dest_modified):
        print("Skipping slack notification")
        return 'skip_notify_slack'
    else:
        return 'notify_slack'

compare_deepracer_simapp_timestamps = BranchPythonOperator(
    task_id='compare_deepracer_simapp_timestamps',
    python_callable=compare_modified_dates,
    dag=monitor_deepracer_simapp_dag)

notify_slack = SlackWebhookOperator(
    task_id='notify_slack',
    channel='#airflow',
    username='airflow',
    message='Deepracer SimApp has been modified!',
    http_conn_id='slack_default',
    dag=monitor_deepracer_simapp_dag)

skip_notify_slack = DummyOperator(
    task_id='skip_notify_slack',
    dag=monitor_deepracer_simapp_dag)

compare_deepracer_simapp_timestamps >> [notify_slack, skip_notify_slack]
