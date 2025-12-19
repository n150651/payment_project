FROM apache/airflow:2.10.3-python3.12

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow
# Add pandas and pymysql here!
RUN pip install --no-cache-dir \
    apache-airflow-providers-mysql \
    mysqlclient \
    pymysql \
    pandas