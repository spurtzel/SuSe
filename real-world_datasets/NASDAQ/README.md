# NASDAQ Stock Event Stream Generator

## Dataset Source

**Note**: This is a **commercial** dataset and is **not available for free**.

- [NASDAQ datasets](https://data.nasdaq.com/)


## Character Type Classification

To obtain the information necessary for the character type classification, we extract essential details from the dataset using the `create_objects_from_file(file_path)` method. The method calculates the following:

- `volume_90th_percentile`: The trading volume at the 90th percentile among all records.
- `volume_10th_percentile`: The trading volume at the 10th percentile among all records.

### Type A
- Price rise - closing price is greater than 1.005 times the opening price.
- Probability: 0.0173

### Type B
- Price drop - Closing price is less than 0.995 times the opening price.
- Probability: 0.0179

### Type C
- Characters surpassing the 90th percentile volume.
- Probability: 0.0926

### Type D
- Closing price is the highest.
- Probability: 0.5657

### Type E
- Closing price is the lowest.
- Probability: 0.2021

### Type F
- Lack of volatility, where the absolute difference between the high and low prices is less than 0.005 times the opening price.
- Probability: 0.1038

### Type G
- Market uncertainty characterized by minimal change between opening and closing prices.
- Probability: 0.0005

### Type H
- Low trading volume events, falling below the 10th percentile volume.
- Probability: 0.0

### Type X
- Characters that do not match any of the above criteria.
- Probability: 0.0

## Query Definitions

### Query Q0
- RegEx: A(B|G)\*A
- Captures an initial price rise (`A`), followed by any number of price drops (`B`) or uncertain market periods (`G`), and ends with a subsequent price rise (`A`). This potentially signals a fluctuating stock price ascent.

### Query Q1
- RegEx: A\*G(A|B)\*G\*A
- Captures zero or more initial price rises (`A`), followed by market uncertainty (`G`), then zero or more occurrences of either significant price rises (`A`) or drops (`B`), a potential period of market uncertainty (`G`), and ends with a price rise (`A`). The query indicates a trend that, despite its volatility and periods of uncertainty, ends with a bullish behavior.

---
