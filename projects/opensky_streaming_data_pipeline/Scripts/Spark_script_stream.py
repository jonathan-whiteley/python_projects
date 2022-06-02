#!/usr/bin/env python
"""Extract events from kafka and write them to hdfs
"""

import json
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import udf, from_json
from pyspark.sql.types import StructType, StructField, StringType
from pyspark.sql import SQLContext


# extract question level information
def extract_info_level1(row):
    data = json.loads(row.value)
    result_list = []
    
    for flight_info in data["states"]:
        flight_info_row={"time":data["time"],
                        "icao24" : flight_info[0],
                        "callsign": flight_info[1],
                        "origin_country": flight_info[2],
                        "time_position": flight_info[3],
                        "last_contact":flight_info[4],
                        "longitude":flight_info[5],
                         "latitude":flight_info[6],
                         "baro_altitude":flight_info[7],
                         "on_ground":flight_info[8],
                         "velocity":flight_info[9],
                         "true_track":flight_info[10],
                         "vertical_rate":flight_info[11],
#                          "sensors":flight_info[12],
                         "geo_altitude":flight_info[13],
#                          "squawk":flight_info[14],
                         "spi":flight_info[15],
                         "position_source":flight_info[16]
                        }
        result_list.append(Row(**flight_info_row))
        
    return result_list

def flight_status_schema():
    """
    root
    'icao24',
    'callsign',
    'origin_country',
    'time_position',
    'last_contact',
    'longitude',
    'latitude',
    'baro_altitude',
    'on_ground',
    'velocity',
    'true_track',
    'vertical_rate',
    'geo_altitude',
    'spi',
    'position_source'
    """
    return StructType([
        StructField("icao24", StringType(), True),
        StructField("callsign", StringType(), True),
        StructField("origin_country", StringType(), True),
        StructField("time_position", StringType(), True),
        StructField("last_contact", StringType(), True),
        StructField("longitude", StringType(), True),
        StructField("latitude", StringType(), True),
        StructField("time_position", StringType(), True),
        StructField("baro_altitude", StringType(), True),
        StructField("on_ground", StringType(), True),
        StructField("velocity", StringType(), True),
        StructField("true_track", StringType(), True),
        StructField("vertical_rate", StringType(), True),
#         StructField("sensors", StringType(), True),
        StructField("geo_altitude", StringType(), True),
#         StructField("squawk", StringType(), True),
        StructField("spi", StringType(), True),
        StructField("position_source", StringType(), True),
    ])


def main():
    """main
    """
    
    spark = SparkSession \
        .builder \
        .appName("ExtractPlanStatus") \
        .getOrCreate()

    raw_events = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "planes") \
        .load()

    # save data in hadoop
    flight_status_info = raw_events \
        .select(from_json(raw_events.value.cast('string'),flight_status_schema()).alias('json')) \
        .select('json.*')
#     \
#         .rdd \
#         .flatMap(extract_info_level1) \
#         .toDF()

    
    write_action0= flight_status_info \
        .writeStream \
        .format("console") \
        .start()

    write_action1=flight_status_info \
        .writeStream \
        .outputMode("append") \
        .option("checkpointLocation", "/tmp/checkpoints_for_flight_status_info_table1") \
        .option("path", "/tmp/flight_status_info_table") \
        .trigger(processingTime="60 seconds") \
        .start()
    
    # save table for hive
#     flight_status_info.registerTempTable("flight_status_events")

#     spark.sql("""
#             create external table flight_status
#             stored as parquet
#             location '/tmp/flight_status_info_hive'
#             as
#             select * from flight_status_events
#         """)
    
   # filter the data and land them in hadoop    
    write_action2=flight_status_info\
        .filter(flight_status_info.on_ground ==True)\
        .writeStream \
        .outputMode("append") \
        .option("checkpointLocation", "/tmp/checkpoints_for_flight_info_on_ground") \
        .option("path", "/tmp/flight_info_on_ground") \
        .trigger(processingTime="60 seconds") \
        .start()

    write_action3=flight_status_info\
        .filter(flight_status_info.on_ground !=True) \
        .writeStream \
        .outputMode("append") \
        .option("checkpointLocation", "/tmp/checkpoints_for_flight_info_off_ground") \
        .option("path", "/tmp/flight_info_off_ground") \
        .trigger(processingTime="60 seconds") \
        .start()
        
#     flight_status_info\
#         .filter(flight_status_info.origin_country =='United States')\
#         .writeStream \
#         .parquet("/tmp/flight_info_domestic",mode='append')   
    
#     flight_status_info\
#         .filter(flight_status_info.origin_country !='United States')\
#         .writeStream \
#         .parquet("/tmp/flight_info_international",mode='append')        
    
#     write_action.awaitTermination()

    write_action0.awaitTermination()
    write_action1.awaitTermination()
    write_action2.awaitTermination()
    write_action3.awaitTermination()
    
if __name__ == "__main__":
    main()