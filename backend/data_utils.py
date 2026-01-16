import pandas as pd


def load_csv_to_dataframe(log_list=None):
    file_path = r"C:\Users\krish\Downloads\daily_weather (1).csv"
    try:
        df = pd.read_csv(file_path)
        print("\nCSV loaded successfully!")
        print(f"Shape: {df.shape}")
        print("\nFirst 5 rows:\n")
        print(df.head())

        if log_list is not None:
            log_list.append(
                (
                    "Load Data",
                    [
                        f"file_path = r'{file_path}'",
                        "df = pd.read_csv(file_path)",
                        "print(f'Shape: {df.shape}')",
                        "df.head()",
                    ],
                )
            )

        return df
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def get_df_info(df):
    unique_percentages = (df.nunique() / len(df)) * 100
    missing_percentages = (df.isnull().sum() / len(df)) * 100
    dtypes = df.dtypes

    df_info = pd.DataFrame(
        {
            "id": range(1, len(df.columns) + 1),
            "column_name": df.columns,
            "dtype": dtypes.astype(str).values,
            "percentage_unique": unique_percentages.values,
            "percentage_missing": missing_percentages.values,
        }
    )

    df_info["percentage_unique"] = df_info["percentage_unique"].round(2)
    df_info["percentage_missing"] = df_info["percentage_missing"].round(2)

    return df_info
