# W205_Project_3

* `docker-compose.yaml`: Docker compose file to start infrastructure
* `OpenSkyFlask.py`: Flask server file to run in MIDS container, used to call, then to get results from API, then to push to flask
* `Spark_script_stream.py`: Script to extract transform the event data from kafka and land them in hadoop.
* [Final Notebook](Final_Notebook.ipynb): Notebook for querying presto, running analytics


# Helper Scripts & Steps
There are a number of helper .sh files, with commands in them to run to do various setup steps. These are listed below, in the order they should be executed from within the directory:
1. `Start_Docker_Stack.sh`: Start docker stack (`docker-compose up -d`)
2. `Create_Kafka_Topic.sh`: Create the Kafka *"planes"* topic in the kafka container. Must wait for Kafka server to have started, ~ 15 seconds.
3. `Check_Kafka_Topic.sh`: check that Kafka topic has been created.
4. `Start_Flask.sh`: Start the flask server in the *mids* container.
5. `Call_Flask_Planes.sh`: Do a CURL on the recently started Flask server. This CURL will call the OpenSkies API, and load the results into the Kafka container in the previously-created topic.
6. `Call_Flask_Planes_Loop.sh`: Same as 5, but will loop every 10 seconds.
7. `Check_Kafka_Queue.sh`: Use KafkaCat to make sure that events have been loaded
8. `Start_Streaming_Pyspark.sh`: Start to streaming the Pyspark, transform the data and land in hadoop
9. `Check_Hadoop.sh`: Check the hadoop files
10. `Run_hive.sh`: Start up hive
11. Create `default.flight_status_info_table` using hive CLI - command found in `Create_hive_table.sh`
12. Launch gcloud sdk, jupyter notebook from localhost:8889
13. Query using presto, create analytics from notebook


To connect from desktop, use: `gcloud compute ssh w205 --ssh-flag="-L 8889:127.0.0.1:8889" --ssh-flag="-L 4040:127.0.0.1:4040" --ssh-flag="-L 8080:127.0.0.1:8080" --ssh-flag="-L 50070:127.0.0.1:50070"
`
To track a flight, use the following API call, replacing `FLIGHTNO` with the flight number:
`docker-compose exec mids curl 0.0.0.0:5000/post_flight?callsign=FLIGHTNO`
To clear the tracked flights, restart the mids container.