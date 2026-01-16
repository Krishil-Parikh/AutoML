import pandas as pd
import numpy as np
from pandas.api.types import is_object_dtype


def generate_global_suggestion(df, df_info, missing_cols):
    suggestions = {}

    for _, row in missing_cols.iterrows():
        col_name = row["column_name"]
        col_id = row["id"]
        dtype = row["dtype"]
        missing_pct = row["percentage_missing"]
        col_data = df[col_name].dropna()

        if missing_pct > 50:
            suggestions[col_id] = "drop_col"
        elif is_object_dtype(dtype) or isinstance(dtype, pd.CategoricalDtype):
            suggestions[col_id] = "mode"
        else:
            skew = col_data.skew() if len(col_data) > 0 else 0
            suggestions[col_id] = "median" if abs(skew) > 1 else "mean"

    return suggestions


def parse_user_plan(user_input):
    plan = {"mean": set(), "median": set(), "mode": set(), "drop_col": set()}

    if not user_input.strip():
        return plan

    parts = [p.strip() for p in user_input.split(";") if p.strip()]

    for part in parts:
        if part.startswith("mean"):
            action = "mean"
        elif part.startswith("median"):
            action = "median"
        elif part.startswith("mode"):
            action = "mode"
        elif part.startswith("drop"):
            action = "drop_col"
        else:
            print(f"Warning: Could not parse part '{part}'. Skipping.")
            continue

        if "-" not in part:
            print(f"Warning: No IDs found after dash in '{part}'. Skipping.")
            continue

        id_part = part.split("-", 1)[1].strip()
        ids = set()

        for sub in [s.strip() for s in id_part.split(",")]:
            if "-" in sub:
                try:
                    start, end = map(int, sub.split("-"))
                    ids.update(range(start, end + 1))
                except:
                    print(f"Invalid range '{sub}'. Skipping.")
            else:
                try:
                    ids.add(int(sub))
                except:
                    print(f"Invalid ID '{sub}'. Skipping.")

        plan[action].update(ids)

    return plan


def handle_missing_values(df, df_info, log_list=None):
    missing_cols = df_info[df_info["percentage_missing"] > 0].copy()

    if missing_cols.empty:
        print("No missing values found in the DataFrame.")
        return df, df_info

    print("\nColumns with missing values:")
    print(missing_cols[["id", "column_name", "dtype", "percentage_missing"]])

    global_suggestion = generate_global_suggestion(df, df_info, missing_cols)

    print("\n=== GLOBAL SUGGESTION FOR MISSING VALUES ===")
    for col_id, action in global_suggestion.items():
        col_name = df_info[df_info["id"] == col_id]["column_name"].iloc[0]
        print(f"ID {col_id} ({col_name}): {action}")

    approve = input("\nDo you approve this global suggestion? (y/n): ").strip().lower()

    updated_df = df.copy()
    updated_info = df_info.copy()

    if approve == "y":
        user_plan = {}
        for col_id, action in global_suggestion.items():
            user_plan.setdefault(action, set()).add(col_id)
    else:
        print("\nPlease provide your custom plan in the following format:")
        print("mean -1,2,3 ; median -4,5-7 ; mode-8,9 ; drop -10,11-13;")
        user_input = input("Your plan: ").strip()
        user_plan = parse_user_plan(user_input)

    covered_ids = set()
    for ids in user_plan.values():
        covered_ids.update(ids)

    all_missing_ids = set(missing_cols["id"])
    uncovered_ids = all_missing_ids - covered_ids

    log_code = []

    def apply_actions(plan, target_ids, current_df, current_info):
        for action, col_ids in plan.items():
            valid_ids = [cid for cid in col_ids if cid in target_ids]
            for col_id in valid_ids:
                col_name = current_info[current_info["id"] == col_id]["column_name"].iloc[0]
                dtype = current_info[current_info["id"] == col_id]["dtype"].iloc[0]
                is_categorical = is_object_dtype(dtype) or isinstance(dtype, pd.CategoricalDtype)

                print(f"\nApplying '{action}' to ID {col_id} ({col_name})")

                if action in ["mean", "median"] and is_categorical:
                    print(
                        f"⚠️  WARNING: '{action}' requested on categorical column '{col_name}' (dtype={dtype})"
                    )
                    convert = input("Attempt to convert to numeric? (y/n): ").strip().lower()
                    if convert == "y":
                        try:
                            current_df[col_name] = pd.to_numeric(current_df[col_name], errors="raise")
                            print(f"Converted '{col_name}' to numeric.")
                            current_info.loc[
                                current_info["column_name"] == col_name, "dtype"
                            ] = current_df[col_name].dtype
                            log_code.append(f"df['{col_name}'] = pd.to_numeric(df['{col_name}'], errors='raise')")
                        except:
                            print("Conversion failed. Skipping this column.")
                            continue
                    else:
                        print("Skipping this column.")
                        continue

                if action == "mean":
                    val = current_df[col_name].mean()
                    if not np.isnan(val):
                        current_df[col_name] = current_df[col_name].fillna(val)
                        print(f"Filled with mean: {val:.2f}")
                        log_code.append(
                            f"df['{col_name}'].fillna(df['{col_name}'].mean(), inplace=True)"
                        )

                elif action == "median":
                    val = current_df[col_name].median()
                    if not np.isnan(val):
                        current_df[col_name] = current_df[col_name].fillna(val)
                        print(f"Filled with median: {val:.2f}")
                        log_code.append(
                            f"df['{col_name}'].fillna(df['{col_name}'].median(), inplace=True)"
                        )

                elif action == "mode":
                    mode_val = current_df[col_name].mode()
                    if not mode_val.empty:
                        current_df[col_name] = current_df[col_name].fillna(mode_val.iloc[0])
                        print(f"Filled with mode: {mode_val.iloc[0]}")
                        log_code.append(
                            f"df['{col_name}'].fillna(df['{col_name}'].mode()[0], inplace=True)"
                        )

                elif action == "drop_col":
                    current_df.drop(columns=[col_name], inplace=True)
                    current_info = current_info[current_info["id"] != col_id].reset_index(drop=True)
                    print(f"Dropped column '{col_name}'")
                    log_code.append(f"df.drop(columns=['{col_name}'], inplace=True)")

    apply_actions(user_plan, all_missing_ids, updated_df, updated_info)

    if uncovered_ids:
        print(
            f"\n⚠️  The following columns with missing values were NOT mentioned in your plan:"
        )
        print(
            missing_cols[missing_cols["id"].isin(uncovered_ids)][
                ["id", "column_name", "percentage_missing"]
            ]
        )

        while True:
            choice = input(
                "\nWhat do you want to do for these columns?\n"
                "1: Provide custom actions now\n"
                "2: Apply my original global suggestions\n"
                "3: Do nothing (leave missing values as-is)\n"
                "Enter 1, 2, or 3: "
            ).strip()

            if choice == "1":
                print("\nProvide additional plan for these columns (same format):")
                extra_input = input("Additional plan: ").strip()
                extra_plan = parse_user_plan(extra_input)
                apply_actions(extra_plan, uncovered_ids, updated_df, updated_info)
                for ids in extra_plan.values():
                    covered_ids.update(ids)
                remaining = uncovered_ids - covered_ids
                if not remaining:
                    break

            elif choice == "2":
                print("Applying original global suggestions to uncovered columns...")
                temp_plan = {}
                for col_id in uncovered_ids:
                    act = global_suggestion.get(col_id, "median")
                    temp_plan.setdefault(act, set()).add(col_id)
                apply_actions(temp_plan, uncovered_ids, updated_df, updated_info)
                break

            elif choice == "3":
                print("Leaving missing values untouched in uncovered columns.")
                break

            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

    new_missing = (updated_df.isnull().sum() / len(updated_df)) * 100
    cols_present = updated_df.columns
    updated_info = updated_info[updated_info["column_name"].isin(cols_present)].reset_index(
        drop=True
    )
    updated_info["id"] = range(1, len(updated_info) + 1)

    for col_name in updated_df.columns:
        if col_name in updated_info["column_name"].values:
            updated_info.loc[
                updated_info["column_name"] == col_name, "percentage_missing"
            ] = round(new_missing[col_name], 2)

    print(f"\nMissing value handling complete. Final shape: {updated_df.shape}")

    if log_list is not None and log_code:
        log_list.append(("Handle Missing Values", log_code))

    return updated_df, updated_info
