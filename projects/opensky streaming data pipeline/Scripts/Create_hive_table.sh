create external table if not exists default.flight_status_info_table (

    icao24 string,
    callsign string,
    origin_country string,
    time_position string,
    last_contact string,
    longitude string,
    latitude string,
    baro_altitude string,
    on_ground string,
    velocity string,
    true_track string,
    vertical_rate string,
    geo_altitude string,
    spi string,
    position_source string
    
  )
  stored as parquet 
  location '/tmp/flight_status_info_table'
  tblproperties ("parquet.compress"="SNAPPY");