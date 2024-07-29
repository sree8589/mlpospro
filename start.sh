#!/bin/sh

# Start the Airflow scheduler in the background
nohup airflow scheduler &

# Start the Airflow webserver
airflow webserver

