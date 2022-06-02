docker-compose exec spark \
  env \
    PYSPARK_DRIVER_PYTHON=jupyter \
    PYSPARK_DRIVER_PYTHON_OPTS='notebook --no-browser --port 8888 --ip 0.0.0.0 --allow-root --notebook-dir=/spark-2.2.0-bin-hadoop2.6/W205_Project_3/' \
  pyspark