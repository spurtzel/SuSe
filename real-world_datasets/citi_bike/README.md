# Citi Bike Real-World Dataset

## Dataset Source

The dataset can be downloaded from the following locations:

- [Citi Bike data index](https://s3.amazonaws.com/tripdata/index.html)
- [Direct download - Used dataset July 2023](https://s3.amazonaws.com/tripdata/202307-citibike-tripdata.csv.zip)

## Character Type Classification

To obtain the information necessary for the character type classification, we extract essential details from the dataset using the `extract_dataset_information` method. The method calculates the following:

- `busiest_stations`: The top 20 most frequently visited stations.
- `average_ride_duration`: The average duration of all rides in the dataset.
- `most_frequent_routes`: The top 50 most commonly taken routes.
- `most_central_stations`: The top 20 stations closest to the geographical center of all stations.

### Type A
- Member rides on the most frequent routes.
- Probability: 0.0057

### Type B
- Rides that occur on the most frequent routes.
- Probability: 0.0046

### Type C
- Very short-duration rides that start or end at the busiest stations. The ride duration is less than half the average ride duration.
- Probability: 0.0305

### Type D
- Short-duration rides that start or end at the busiest stations. The ride duration is less than the average ride duration.
- Probability: 0.0339

### Type E
- Rides that start or end at the busiest stations.
- Probability: 0.0370

### Type F
- Long-duration rides that start or end at the most central stations. The ride duration is greater than the average ride duration.
- Probability: 0.0116

### Type G
- Casual rides that start or end at the most central stations.
- Probability: 0.0026

### Type H
- Rides that start or end at the most central stations.
- Probability: 0.0290

### Type I
- Short-duration rides by casual users. The ride duration is less than the average ride duration.
- Probability: 0.0986

### Type J
- Member rides that start or end at non-busy stations.
- Probability: 0.6565

### Type K
- Rides that start or end at non-busy stations.
- Probability: 0.0902

### Type Z
- Rides that do not match any of the above criteria.
- Probability: 0.0

## Query Definitions

### Query Q0
- RegEx: E(H|K)\*E
- Captures patterns where rides originate from busy stations (`E`), transition through a potential combination of central (`H`) and quieter (`K`) stations, and then return to busy stations (`E`). This suggests probable areas for station enhancements or upkeep.

### Query Q1
- RegEx: (E|B|F)\+CEHF
- Captures sequences that start with rides at busy stations (`E`), popular routes (`B`), or extended rides at central stations (`F`). This is followed by short (`C`) and consecutive rides at busy stations (`E`), a ride at a central location (`H`), and concludes with a long-duration ride at a central station, hinting at peak demand transitioning to central areas.

---


