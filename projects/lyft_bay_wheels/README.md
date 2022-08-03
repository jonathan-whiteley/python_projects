# Project 1 - Lyft Bay Wheels Recommendations
#### By Jonathan Whiteley
---
## Background
As the Bay Area's leading bike share company, Lyft Bay Wheel provides locals and vistors alike a fast and efficient means of getting around the San Franscisco, San Jose, Mountain View, Redwood City, and Palo Alto. Lyft Bay Wheels has experienced widescale adoption in its first three years of operation since its launch in August 2013. 

Current bikeshare offers:
- Single Trip
- Traditional Membership - Monthly or Annual
- Reduced Cost Membership 
    - Bike Share for All Membership
    - Corporate Membership
    - University Membership

## Key Questions
Lyft Bay Wheels has approached our team to help determine scalable solutions to drive increased ridership. Our team has analyzed the historical trips data provided in order to address the following key questions:
1. **What are the 5 most popular commuter trips?**
2. **What offers should Lyft Bay Wheels consider implementing to improve ridership?**
---

## Findings

**What are the 5 most popular commuter trips?** 

Using a custom view limiting to Commuter trips, we can see that, perhaps unsurprisingly, the most popular trips take place near transit hubs like Caltrain or along/near the BART route.
  
| rank | start_station_name | end_station_name | trip_count |
| --- | --- | --- | --- |
| 1 | Harry Bridges Plaza (Ferry Building)	| 2nd at Townsend |	4379 |
| 2 | 2nd at Townsend | Harry Bridges Plaza (Ferry Building) |	4368 |
| 3 |San Francisco Caltrain 2 (330 Townsend)	 |Townsend at 7th |	4283 |
| 4 |Embarcadero at Sansome	 | Steuart at Market	 |4122 |
| 5 |Embarcadero at Folsom	 | San Francisco Caltrain (Townsend at 4th) |	3976 |


Recommendations
---
1. Initiate promotions like free 30 day trial offers for commuters during periods of low ridership, Fall-Winter. 
2. Convert commuting non-subscribers by allowing riders to use their Clipper Card balance to pay for memberships.
3. Increase dock count at most popular start stations.


[View full analysis in Recommendation Notebook](Project_1.ipynb)
---

## Part 1 - Querying Data with BigQuery

- What's the size of this dataset? (i.e., how many trips)

  * Answer: **983648 rows**
  * SQL query:
  
```sql
SELECT COUNT(*) as trip_count
FROM `bigquery-public-data.san_francisco.bikeshare_trips`
```


- What is the earliest start date and time and latest end date and time for a trip?

  * Answer: 

- **min_time : 2013-08-29 09:08:00 UTC**
- **max_time : 2016-08-31 23:48:00 UTC**

  * SQL query:
  
```sql
SELECT min(start_date) as min_time,
max(end_date) as max_time
FROM `bigquery-public-data.san_francisco.bikeshare_trips`
```

- How many bikes are there?

  * Answer: **700 bikes**
  * SQL query:
  
```sql
SELECT count(distinct bike_number)
FROM `bigquery-public-data.san_francisco.bikeshare_trips`
```

---
### Sub-questions

- Question 1: What are the top start station locations?
  * Answer:

| rank | start_station_name | trip_count |
| --- | --- | --- |
| 1 |  San Francisco Caltrain (Townsend at 4th) | 72683 |
| 2 | San Francisco Caltrain 2 (330 Townsend) | 56100 |
| 3 | Harry Bridges Plaza (Ferry Building)| 49062 |
| 4 | Embarcadero at Sansome | 41137 |
| 5 | 2nd at Townsend | 39936 |

  * SQL query:
  
```sql
SELECT trips.start_station_name, count(*) as trip_count
FROM `bigquery-public-data.san_francisco.bikeshare_trips` as trips
GROUP BY trips.start_station_name
ORDER BY trip_count DESC
LIMIT 5
```

- Question 2: Average ride duration?
  * Answer: **16.98 mins**
  * SQL query: 
  
```sql
SELECT avg(trips.duration_sec)/60 as avg_duration_min
FROM `bigquery-public-data.san_francisco.bikeshare_trips` as trips
```

- Question 3: Subscriber Type Breakdown?
  * Answer:

| subscriber_type | type_tripcount|
| --- | --- |
| Subscriber | 846839 |
| Customer | 136809 |
  
  * SQL query:
  
```sql
SELECT trips.subscriber_type, count(*) as type_tripcount
FROM `bigquery-public-data.san_francisco.bikeshare_trips` as trips
GROUP BY trips.subscriber_type
ORDER BY trips.subscriber_type DESC
```

---
## Part 2 - Querying data from the BigQuery CLI 

1. Rerun the first 3 queries from Part 1 using bq command line tool (Paste your bq
   queries and results here, using properly formatted markdown):

  * What's the size of this dataset? (i.e., how many trips)
  
    * Once again, we see the dataset contains **983648 records**

 
 ```
    bq query --use_legacy_sql=false '
        SELECT count(*)
        FROM
           `bigquery-public-data.san_francisco.bikeshare_trips`'
 ```
  
  * What is the earliest start time and latest end time for a trip?
 
- *min_time : 2013-08-29 12:06:01*
- *max_time : 2016-08-31 23:58:59*

I notice the timezone is ommitted in the CLI query result for min and max time, but otherwise is consistent with initial result.

```
bq query --use_legacy_sql=false '
SELECT min(time) as min_time,
max(time) as max_time
FROM `bigquery-public-data.san_francisco.bikeshare_status`'
```

  * How many bikes are there?
  
**700 bikes**

```
bq query --use_legacy_sql=false '
SELECT count(distinct bike_number)
FROM `bigquery-public-data.san_francisco.bikeshare_trips`'
```


2. New Query

  * How many trips are in the morning vs in the afternoon?
  
| Time of Day | num_trips |
| --- | --- |
| AM | 412339 |
| PM | 571309 |

 
 ```
bq query --use_legacy_sql=false '
SELECT FORMAT_DATETIME("%p", start_date) as am_pm, 
COUNT(*) as num_trips,
FROM `bigquery-public-data.san_francisco.bikeshare_trips` as trips
GROUP BY am_pm
ORDER BY am_pm ASC'
```


### Project Questions


- **Question 1: Who is riding?**

  * Answer: Over the entire period, we see around 14% of riders are non-subcribers. This is the group we want to target with promotions and offers to push them towards becoming subscribers.

  * SQL query: 
```sql
SELECT trips.subscriber_type, count(*) as type_tripcount
FROM `bigquery-public-data.san_francisco.bikeshare_trips` as trips
GROUP BY trips.subscriber_type
ORDER BY trips.subscriber_type DESC
```
---
- **Question 2: When are they riding?** 
  * Answer: Weekdays appear to be far busier than weekdays, indicating the importance of commuter ridership. 
  
| day_of_week | num_trips |
| --- | --- |
| Tuesday | 184405 |
| Wednesday | 180767 |
| Thursday | 176908 | 
| Monday | 169937 | 
| Friday | 159977 |
| Saturday | 60279 | 
| Sunday | 51375 | 
 
  * SQL query:
 
 ```sql
SELECT FORMAT_DATETIME('%A', start_date) as day_of_week, 
COUNT(*) as num_trips
FROM `bigquery-public-data.san_francisco.bikeshare_trips` as trips
GROUP BY day_of_week
ORDER BY  num_trips ASC;
```

---
- **Question 3: What are the busiest hours of the day?** 
  * Answer: 8am and 5pm are the busiest, with the bulk of rides occurring in what most would consider rush hour or commuting hours.
  * SQL query:
  
 ```sql
SELECT FORMAT_DATETIME('%k', start_date) as start_hour, 
COUNT(*) as num_trips
FROM `bigquery-public-data.san_francisco.bikeshare_trips`
GROUP BY start_hour
ORDER BY start_hour ASC
 ```

---
- **Question 4: What defines a commuter trip? How many were there?**
  * Answer: 471481 Commuter trips = a trip during rush hour on M-F, that was not a round trip 
  * SQL query:
  
```sql
SELECT EXTRACT (DAYOFWEEK FROM start_date) as day_of_week_n,
EXTRACT (HOUR FROM start_date) as hour_n,*
FROM `bigquery-public-data.san_francisco.bikeshare_trips`
WHERE start_station_id != end_station_id
AND EXTRACT (DAYOFWEEK FROM start_date) BETWEEN 1 AND 5
AND (EXTRACT (HOUR FROM start_date) BETWEEN 7 AND 9 
OR EXTRACT (HOUR FROM start_date) BETWEEN 16 AND 18)
```

---
- **Question 5: What are the 5 most popular commuter trips?** 
  * Answer: Using a view I constructed from the above query limiting to Commuter trips, we can see that, perhaps unsurprisingly, the most popular trips take place near transit hubs like Caltrain or along/near the BART route.
  
| rank | start_station_name | end_station_name | trip_count |
| --- | --- | --- | --- |
| 1 | Harry Bridges Plaza (Ferry Building)	| 2nd at Townsend |	4379 |
| 2 | 2nd at Townsend | Harry Bridges Plaza (Ferry Building) |	4368 |
| 3 |San Francisco Caltrain 2 (330 Townsend)	 |Townsend at 7th |	4283 |
| 4 |Embarcadero at Sansome	 | Steuart at Market	 |4122 |
| 5 |Embarcadero at Folsom	 | San Francisco Caltrain (Townsend at 4th) |	3976 |

  
  * SQL query:
  
 ```sql
SELECT trips.start_station_name,
trips.end_station_name, 
count(*) as trip_count
FROM `my-project-85244-313100.san_francisco_citi_bike_jw.bikeshare_commuter_trips` as trips
GROUP BY start_station_id,
end_station_id, trips.start_station_name, trips.end_station_name
ORDER BY trip_count DESC
LIMIT 5;
 ```
 
---

- **Question 6: Do the busiest stations have the most dock capacity?** 
  * Answer: The 5 most popular stations are not the stations with the most number of docks.

  * SQL query: 
 ```sql
SELECT name,
dockcount
FROM `bigquery-public-data.san_francisco.bikeshare_stations`
ORDER BY dockcount DESC
```

---

## Part 3 - Jupyter Notebook

#### Conclusion
---
1. Initiate promotions like free 30 day trial offers for commuters during periods of low ridership, Fall-Winter. 
2. Convert commuting non-subscribers by allowing riders to use their Clipper Card balance to pay for memberships.
3. Increase dock count at most popular start stations.

[Recommendation Notebook](Project_1.ipynb)