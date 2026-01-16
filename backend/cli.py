from data_utils import load_csv_to_dataframe, get_df_info
from column_ops import drop_columns_by_id
from missing_values import handle_missing_values
from outliers import detect_and_handle_outliers
from analysis import univariate_analysis, bivariate_analysis
from correlation_utils import handle_high_correlation
from encoding_utils import handle_categorical_encoding
from scaling_utils import handle_feature_scaling
from notebook_utils import save_to_ipynb


def run_cli():
    notebook_log = []

    df = load_csv_to_dataframe(notebook_log)
    if df is None:
        return

    info = get_df_info(df)
    print("\nInitial column info:")
    print(info)

    df = drop_columns_by_id(df, info, notebook_log)
    if df.shape[1] != info.shape[0]:
        info = get_df_info(df)
        print("\nUpdated column info after dropping columns:")
        print(info)

    df, info = handle_missing_values(df, info, notebook_log)

    print("\nFinal column info after missing value handling:")
    print(info)

    df, info = detect_and_handle_outliers(df, info, notebook_log)

    print("\nFinal column info after outlier handling:")
    print(info)

    do_univariate = input(
        "\nDo you want to perform univariate analysis (stats + optional plots)? (y/n): "
    ).strip().lower()
    if do_univariate == "y":
        univariate_analysis(df, info, notebook_log)

    do_bivariate = input(
        "\nDo you want to perform bivariate analysis (correlation heatmap + pairplot)? (y/n): "
    ).strip().lower()
    if do_bivariate == "y":
        bivariate_analysis(df, info, notebook_log)

        do_drop_corr = input(
            "\nDo you want to drop highly correlated columns based on the analysis? (y/n): "
        ).strip().lower()
        if do_drop_corr == "y":
            thresh_input = input("Enter correlation threshold (default 0.90): ").strip()
            try:
                threshold = float(thresh_input)
            except:
                threshold = 0.90

            df, info = handle_high_correlation(df, info, notebook_log, threshold)

    do_encode = input(
        "\nDo you want to encode categorical columns (One-Hot/Label)? (y/n): "
    ).strip().lower()
    if do_encode == "y":
        df, info = handle_categorical_encoding(df, info, notebook_log)
        print("\nUpdated column info after encoding:")
        print(info)

    do_scale = input(
        "\nDo you want to scale numeric features (Standard/MinMax)? (y/n): "
    ).strip().lower()
    if do_scale == "y":
        df, info = handle_feature_scaling(df, info, notebook_log)

    print("\n=== FINAL CLEAN DATASET READY ===")
    print(f"Shape: {df.shape}")
    print(info)

    print("\n" + "=" * 50)
    print("WORKFLOW COMPLETE")
    print("=" * 50)
    gen_nb = input(
        "Do you want to download the Python Code (.ipynb) for this workflow? (y/n): "
    ).strip().lower()
    if gen_nb == "y":
        fname = input("Enter filename for notebook (default: workflow.ipynb): ").strip()
        if not fname:
            fname = "workflow.ipynb"
        save_to_ipynb(notebook_log, filename=fname)

    save = input("\nSave cleaned dataset to CSV? (y/n): ").strip().lower()
    if save == "y":
        filename = input("Enter filename (e.g., clean_weather.csv): ").strip()
        if not filename.endswith(".csv"):
            filename += ".csv"
        df.to_csv(filename, index=False)
        print(f"Saved to {filename}")
