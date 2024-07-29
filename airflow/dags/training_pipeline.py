from __future__ import annotations
import json
from textwrap import dedent
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from src.pipeline.training_pipeline import TrainingPipeline

training_pipeline = TrainingPipeline()

with DAG(
    "gemstone_training_pipeline",
    default_args={'retries': 2},
    description="It is my training pipeline",
    schedule_interval='@weekly',
    start_date=pendulum.datetime(2024, 12, 12, tz='UTC'),
    catchup=False,
    tags=['machine_learning', 'classification', 'gemstone'],
) as dag:
    
    dag.doc_md = __doc__
    
    def data_ingestion(**kwargs):
        ti = kwargs["ti"]
        train_data_path, test_data_path = training_pipeline.start_data_ingestion()
        ti.xcom_push("data_ingestion_artifact", {"train_data_path": train_data_path})

    def data_transformations(**kwargs):
        ti = kwargs["ti"]
        data_ingestion_artifact = ti.xcom_pull(task_ids='data_ingestion', key='data_ingestion_artifact')
        train_arr, test_arr = training_pipeline.start_data_transformation(data_ingestion_artifact['train_data_path'])
        train_arr = train_arr.tolist()
        test_arr = test_arr.tolist()
        ti.xcom_push("data_transformations_artifact", {"train_arr": train_arr, "test_arr": test_arr})

    def model_trainer(**kwargs):
        import numpy as np
        ti = kwargs["ti"]
        data_transformation_artifact = ti.xcom_pull(task_ids="data_transformation", key="data_transformations_artifact")
        train_arr = np.array(data_transformation_artifact["train_arr"])
        test_arr = np.array(data_transformation_artifact['test_arr'])
        training_pipeline.start_model_training(train_arr, test_arr)

    data_ingestion_task = PythonOperator(
        task_id="data_ingestion",
        python_callable=data_ingestion,
    )
    data_ingestion_task.doc_md = dedent(
        """This task creates train and test data."""
    )

    data_transformation_task = PythonOperator(
        task_id="data_transformation",
        python_callable=data_transformations,
    )
    data_transformation_task.doc_md = dedent(
        """This task performs data transformations."""
    )

    model_trainer_task = PythonOperator(
        task_id="model_trainer",
        python_callable=model_trainer,
    )
    model_trainer_task.doc_md = dedent(
        """This task trains the model."""
    )

data_ingestion_task >> data_transformation_task >> model_trainer_task
