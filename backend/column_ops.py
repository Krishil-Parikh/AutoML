import pandas as pd


def drop_columns_by_id(df, df_info, log_list=None):
    if df_info is None or df_info.empty:
        print("No column info available. Cannot drop columns.")
        return df

    print("\nAvailable columns:")
    print(df_info[["id", "column_name", "dtype", "percentage_unique", "percentage_missing"]])

    user_input = input("\nEnter IDs to drop (e.g., '1, 2, 3, 5-8, 9') or 'none' to skip: ").strip()

    if user_input.lower() == "none":
        print("No columns dropped.")
        return df

    ids_to_drop = set()
    parts = [part.strip() for part in user_input.split(",")]

    for part in parts:
        if "-" in part:
            try:
                start, end = map(int, part.split("-"))
                if start > end:
                    print(f"Warning: Invalid range '{part}' (start > end). Skipping.")
                    continue
                ids_to_drop.update(range(start, end + 1))
            except ValueError:
                print(f"Warning: Invalid range '{part}'. Skipping.")
        else:
            try:
                ids_to_drop.add(int(part))
            except ValueError:
                print(f"Warning: Invalid ID '{part}'. Skipping.")

    valid_ids = {i for i in ids_to_drop if 1 <= i <= len(df_info)}
    invalid_ids = ids_to_drop - valid_ids

    if invalid_ids:
        print(f"Warning: Invalid IDs out of range: {sorted(invalid_ids)}. Skipping them.")

    if not valid_ids:
        print("No valid IDs to drop.")
        return df

    columns_to_drop = df_info[df_info["id"].isin(valid_ids)]["column_name"].tolist()
    print(f"Dropping columns: {columns_to_drop}")
    df_updated = df.drop(columns=columns_to_drop)
    print(f"Updated DataFrame shape: {df_updated.shape}")

    if log_list is not None:
        log_list.append(
            (
                "Drop Columns",
                [
                    f"columns_to_drop = {columns_to_drop}",
                    "df.drop(columns=columns_to_drop, inplace=True)",
                    "print(f'Dropped columns: {columns_to_drop}')",
                ],
            )
        )

    return df_updated
