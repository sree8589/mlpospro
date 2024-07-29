FROM python:3.8-slim-buster

# Install system dependencies
RUN apt-get update -y && apt-get install -y \
    gcc \
    libffi-dev \
    libpq-dev \
    bash \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
USER root
# Create and set the working directory
RUN mkdir /app
COPY . /app/
WORKDIR /app


# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install apache-airflow==2.5.0 \
    connexion==2.10.0 \
    flask-session \
    flask==2.2.3 \
    werkzeug==2.2.2
RUN pip install -r requirements.txt

# Set Airflow environment variables
ENV AIRFLOW_HOME="/app/airflow"
ENV AIRFLOW_CORE_DAGBAG_IMPORT_TIMEOUT=1000
ENV AIRFLOW_CORE_ENABLE_XCOM_PICKLING=True

# Initialize Airflow database and create user
RUN airflow db init
RUN airflow users create \
    --username admin \
    --firstname mahesh \
    --lastname kumar \
    --email maheshsree98@gmail.com \
    --role Admin \
    --password admin

# Copy and set permissions for start script

RUN chmod 777 start.sh

# Use /bin/sh for compatibility
ENTRYPOINT ["/bin/sh"]
CMD ["start.sh"]
