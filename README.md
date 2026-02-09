## Company Matching – Technical Documentation

Objective:
    Match companies between two datasets based on company name and location data and produce a merged output.

1. Input Data
    - Two datasets containing:
        * company name
        * address information (street, city, state/province, country, postal code)
    - Dataset 1 is the primary dataset.
    - All unique companies from Dataset 1 are preserved in the final output.

2. Matching Approach
    - Company Name Normalization
        * converted to uppercase
        * removed legal suffixes (INC, INC., LTD, LTD.)
        * trimmed leading and trailing spaces
    - A normalized internal key (company_internal) is used for matching.
3. Address Normalization
    - Each address component is cleaned independently:
        * trimmed spaces
        * postal codes stripped of internal spaces
        * missing values handled safely
    - A canonical address string is created:
        STREET | CITY | STATE | COUNTRY | POSTAL_CODE
        Addresses without street value are excluded.
4. Address Aggregation
    * multiple address columns are consolidated
    * all addresses per company are stored as unique sets
    * Dataset 1 → address_from_data_1
    * Dataset 2 → address_from_data_2

5.  Matching Logic
    * left join on normalized company name
    * all Dataset 1 companies retained
    * Dataset 2 companies added where matches exist
6.  Overlapping Locations
    * intersection of address sets is calculated
    * overlapping addresses stored in overlap
    * if no overlap exists, the column remains empty
7.  Output
    - Merged dataset contains:
        * company name
        * list of locations from Dataset 1
        * list of locations from Dataset 2
        * overlapping locations (if any)
8.  Metrics
    - Calculated metrics:
        * match rate: % of Dataset 1 companies with overlapping locations
        * unmatched records: % of companies without overlaps
        * one-to-many matches: number of companies with multiple locations in both datasets
9.  Data Quality Issues Identified
    - inconsistent company name formatting
    - inconsistent address capitalization
    - duplicate company names with multiple locations
    - multiple address fields per record
    - missing or misaligned address components
10.  Tools
    - Python
    - Pandas
11.  Execution
    - pip install pandas
    - python main.py
12.  Notes
    The solution uses deterministic, explainable matching logic and is designed to be extensible for additional matching rules if required.
13. Result:
    Total companies: 1043
    Total overlaped: 32
    Percentage overlaped: 3.07%
    Total unmatched: 1011
    Unmatched percentage: 96.93%

    Total companies that contains multiple entries in DS1 and DS2: 70