# We use Airflow 2.10 which has full native support for Python 3.12
FROM apache/airflow:2.10.3-python3.12

# Switch to root to install system-level MySQL libraries
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         default-libmysqlclient-dev \
         gcc \
         pkg-config \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Switch back to the airflow user to install Python providers
USER airflow
RUN pip install --no-cache-dir \
    apache-airflow-providers-mysql \
    mysqlclient
