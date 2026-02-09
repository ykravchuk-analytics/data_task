import pandas as pd

def read_file(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def clean_company_name(df: pd.DataFrame, column: str) -> pd.DataFrame:
    df["company_internal"] = (
        df[column]
            .str.upper()
            .str.replace("INC.", "")
            .str.replace("INC", "")
            .str.replace("LTD.", "")
            .str.replace("LTD", "")
            .str.strip()
    )

    return df

def clean_colum(df: pd.DataFrame, column: str, replace_empty: bool = False) -> pd.DataFrame:
    if replace_empty:
        df[column] = df[column].str.strip().str.replace(" ", "")
    else:
        df[column] = df[column].str.strip()

    return df

def populate_overlap(df: pd.DataFrame) -> pd.DataFrame:
    def parts(x):
        if pd.isna(x):
            return []

        return [v.strip() for v in x if v.strip() != '']

    df['overlap'] = [
        set(set(parts(a)) & set(parts(b)))
        for a, b in zip(df['address_from_data_1'], df['address_from_data_2'])
    ]

    return df


def combine_addr(
    df: pd.DataFrame,
    result_col: str,
    street_col: str,
    city_col: str,
    state_col: str,
    country_col: str,
    zip_code_col: str,
) -> pd.DataFrame:
    sep = "|"
    cols = [street_col, city_col, state_col, country_col, zip_code_col]

    parts = []
    for c in cols:
        s = df[c] if c in df.columns else pd.Series("", index=df.index)
        s = s.fillna("").astype(str).str.strip()   # trim safely (handles NaN, non-strings)
        parts.append(s)

    res = parts[0].str.cat(parts[1:], sep=sep).str.upper()

    # if street is empty we should make result empty
    street_empty = parts[0].eq("")
    df[result_col] = res.mask(street_empty, "")

    return df

def total_multiple_match(df: pd.DataFrame) -> int:
    def nonempty_count(x) -> int:
        if pd.isna(x):
            return 0

        return sum(1 for v in x if pd.notna(v) and str(v).strip() != "")

    df2 = df.copy()

    df2["addr1_cnt"] = df2["address_from_data_1"].apply(nonempty_count)
    df2["addr2_cnt"] = df2["address_from_data_2"].apply(nonempty_count)

    multi = df2[(df2["addr1_cnt"] > 1) & (df2["addr2_cnt"] > 1)]

    total_companies = multi.index.nunique()

    return total_companies

def main():
    df1 = read_file("./data_1.csv")
    df2 = read_file("./data_2.csv")

    # cleaned company names
    df1 = clean_company_name(df1, "custname")
    df1 = clean_colum(df1, "sStreet1")
    df1 = clean_colum(df1, "sProvState")
    df1 = clean_colum(df1, "sCountry")
    df1 = clean_colum(df1, "sPostalZip", replace_empty=True)

    df2 = clean_company_name(df2, "custname")
    df2 = clean_colum(df2, "address1")
    df2 = clean_colum(df2, "address2")
    df2 = clean_colum(df2, "address3")
    df2 = clean_colum(df2, "city")
    df2 = clean_colum(df2, "state")
    df2 = clean_colum(df2, "country")
    df2 = clean_colum(df2, "zip", replace_empty=True)

    # with addresses
    df1 = combine_addr(df1, "address_1", "sStreet1", "sCity", "sProvState","sCountry","sPostalZip")
    df1 = combine_addr(df1, "address_2", "sStreet2", "sCity", "sProvState","sCountry","sPostalZip")

    # combine first df
    df1_addr_1 = df1[['company_internal', 'address_1']].rename(columns={
        "company_internal": "company",
        "address_1": "address_from_data_1",
    })

    df1_addr_2 = df1[['company_internal', 'address_2']].rename(columns={
        "company_internal": "company",
        "address_2": "address_from_data_1",
    })

    df1_result = pd.concat([df1_addr_1, df1_addr_2]).groupby('company')['address_from_data_1'].agg(set)

    # combine df 2
    df2 = combine_addr(df2, "address_1", "address1", "city", "state", "country", "zip")
    df2 = combine_addr(df2, "address_2", "address2", "city", "state", "country", "zip")
    df2 = combine_addr(df2, "address_3", "address3", "city", "state", "country", "zip")

    df2_addr_1 = df2[['company_internal', 'address_1']].rename(columns={
        "company_internal": "company",
        "address_1": "address_from_data_2",
    })

    df2_addr_2 = df2[['company_internal', 'address_2']].rename(columns={
        "company_internal": "company",
        "address_2": "address_from_data_2",
    })

    df2_addr_3 = df2[['company_internal', 'address_3']].rename(columns={
        "company_internal": "company",
        "address_3": "address_from_data_2",
    })

    df2_result = pd.concat([df2_addr_1, df2_addr_2, df2_addr_3]).groupby('company')['address_from_data_2'].agg(set)

    result_df = pd.merge(df1_result, df2_result, on='company', how='left')
    result_df = populate_overlap(result_df)

    total_values = len(result_df)
    total_overlaped = result_df["overlap"].map(len).gt(0).sum()
    total_multiple_match_companies = total_multiple_match(result_df)

    percentage_overlaped = total_overlaped / total_values

    print('Total companies:', total_values)
    print('Total overlaped:', total_overlaped)
    print(f'Percentage overlaped: {percentage_overlaped * 100:.2f}%')
    print(f'Total unmatched: {total_values - total_overlaped}')
    print(f'Unmatched percentage: {(1 - percentage_overlaped) * 100:.2f}%')
    print('Total companies that contains multiple entries in DS1 and DS2:', total_multiple_match_companies)


if __name__ == '__main__':
    main()