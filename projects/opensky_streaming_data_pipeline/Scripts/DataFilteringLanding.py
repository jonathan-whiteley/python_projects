#!/usr/bin/env python
"""Extract events from kafka and write them to hdfs
"""
import json
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import udf, from_json
from pyspark.sql.types import StructType, StructField, StringType
from pyspark.sql import SQLContext
from pyspark.sql.functions import from_json, col


def main():
    """main
    """
    spark = SparkSession \
        .builder \
        .appName("FilterFlightInfo") \
        .getOrCreate()

    raw_events = spark \
        .read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "planes1") \
        .option("startingOffsets", "earliest") \
        .option("endingOffsets", "latest") \
        .load()
    
    raw_events.cache()
    
    flight_info = raw_events\
        .select(raw_events.value.cast('string')) \
        .rdd\
        .map(lambda x: json.loads(x.value))\
        .toDF()
    
    flight_info\
        .filter(flight_info.on_ground ==True)\
        .write\
        .parquet("/tmp/flight_info_on_ground",mode='append')

    flight_info\
        .filter(flight_info.on_ground !=True)\
        .write\
        .parquet("/tmp/flight_info_off_ground",mode='append')
    
    flight_info\
        .filter(flight_info.origin_country =='United States')\
        .write\
        .parquet("/tmp/flight_info_domestic",mode='append')   
    
    flight_info\
        .filter(flight_info.origin_country !='United States')\
        .write\
        .parquet("/tmp/flight_info_international",mode='append')        
    

    flight_info.show(1)
if __name__ == "__main__":
    main()