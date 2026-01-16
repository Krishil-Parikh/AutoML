import pandas as pd
import numpy as np

from data_utils import get_df_info


def parse_outlier_plan(user_input):
    plan = {"cap": set(), "remove_rows": set(), "none": set()}

    if not user_input.strip():
        return plan

    parts = [p.strip() for p in user_input.split(";") if p.strip()]

    for part in parts:
        action = None
        if part.startswith("cap"):
            action = "cap"
        elif part.startswith("remove_rows"):
            action = "remove_rows"
        elif part.startswith("none"):
            action = "none"
        else:
            print(f"Warning: Unknown action in '{part}'. Skipping.")
            continue

        if "-" not in part:
            print(f"Warning: No IDs found in '{part}'. Skipping.")
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


def detect_and_handle_outliers(df, df_info, log_list=None):
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    if len(numeric_cols) == 0:
        print("No numeric columns found for outlier detection.")
        return df, df_info

    print("\n=== OUTLIER DETECTION (IQR Method) ===")
    print("Analyzing numeric columns for outliers...\n")

    outlier_summary = []
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers_count = df[(df[col] < lower_bound) | (df[col] > upper_bound)].shape[0]
        outliers_pct = (outliers_count / len(df)) * 100

        if outliers_count > 0:
            outlier_summary.append(
                {
                    "column_name": col,
                    "outliers_count": outliers_count,
                    "outliers_pct": round(outliers_pct, 2),
                    "lower_bound": round(lower_bound, 2),
                    "upper_bound": round(upper_bound, 2),
                }
            )

    if not outlier_summary:
        print("No outliers detected in any numeric column using IQR method. Great!")
        return df, df_info

    outlier_df = pd.DataFrame(outlier_summary).sort_values("outliers_pct", ascending=False)

    print("Columns with detected outliers:")
    print(outlier_df.to_string(index=False))

    outlier_cols_info = df_info[df_info["column_name"].isin(outlier_df["column_name"])].copy()
    outlier_cols_info = (
        outlier_cols_info[["id", "column_name"]]
        .merge(
            outlier_df[
                ["column_name", "outliers_count", "outliers_pct", "lower_bound", "upper_bound"]
            ],
            on="column_name",
        )
        .sort_values("outliers_pct", ascending=False)
        .reset_index(drop=True)
    )

    print("\nColumns with outliers (use these IDs for your plan):")
    print(outlier_cols_info[["id", "column_name", "outliers_count", "outliers_pct"]])

    global_suggestion = {}
    for _, row in outlier_cols_info.iterrows():
        col_id = row["id"]
        col_name = row["column_name"]
        pct = row["outliers_pct"]

        if pct > 10:
            global_suggestion[col_id] = "remove_rows"
        elif "rain" in col_name.lower():
            global_suggestion[col_id] = "cap"
        else:
            global_suggestion[col_id] = "cap"

    print("\n=== GLOBAL SUGGESTION FOR OUTLIERS ===")
    for col_id, action in global_suggestion.items():
        col_name = outlier_cols_info[outlier_cols_info["id"] == col_id]["column_name"].iloc[0]
        pct = outlier_cols_info[outlier_cols_info["id"] == col_id]["outliers_pct"].iloc[0]
        print(f"ID {col_id} ({col_name}): {action} (outliers: {pct}%)")

    approve = input("\nDo you approve this global suggestion? (y/n): ").strip().lower()

    updated_df = df.copy()
    updated_info = df_info.copy()

    if approve == "y":
        user_plan = {}
        for col_id, action in global_suggestion.items():
            user_plan.setdefault(action, set()).add(col_id)
    else:
        print("\nProvide your custom plan in this format:")
        print("cap -1,2,3 ; remove_rows -4-6 ; none -7,8 ;")
        user_input = input("Your plan: ").strip()
        user_plan = parse_outlier_plan(user_input)

    covered_ids = set()
    for ids in user_plan.values():
        covered_ids.update(ids)

    all_outlier_ids = set(outlier_cols_info["id"])
    uncovered_ids = all_outlier_ids - covered_ids

    log_code = []

    def apply_outlier_logic(plan, target_ids, current_df):
        for action, col_ids in plan.items():
            valid_ids = [cid for cid in col_ids if cid in target_ids]
            for col_id in valid_ids:
                col_name = updated_info[updated_info["id"] == col_id]["column_name"].iloc[0]
                bounds = outlier_cols_info[outlier_cols_info["id"] == col_id][
                    ["lower_bound", "upper_bound"]
                ].iloc[0]
                lower, upper = bounds["lower_bound"], bounds["upper_bound"]

                print(f"\nApplying '{action}' to ID {col_id} ({col_name})")

                if action == "cap":
                    current_df[col_name] = current_df[col_name].clip(lower=lower, upper=upper)
                    print(f"  Capped to [{lower}, {upper}]")
                    log_code.append(f"# Cap Outliers: {col_name}")
                    log_code.append(f"Q1 = df['{col_name}'].quantile(0.25)")
                    log_code.append(f"Q3 = df['{col_name}'].quantile(0.75)")
                    log_code.append("IQR = Q3 - Q1")
                    log_code.append(
                        f"df['{col_name}'] = df['{col_name}'].clip(lower=Q1-1.5*IQR, upper=Q3+1.5*IQR)"
                    )

                elif action == "remove_rows":
                    initial_rows = len(current_df)
                    mask = (current_df[col_name] >= lower) & (current_df[col_name] <= upper)
                    current_df = current_df[mask].reset_index(drop=True)
                    removed = initial_rows - len(current_df)
                    print(f"  Removed {removed} rows with outliers in '{col_name}'")
                    log_code.append(f"# Remove Rows Outliers: {col_name}")
                    log_code.append(f"Q1 = df['{col_name}'].quantile(0.25)")
                    log_code.append(f"Q3 = df['{col_name}'].quantile(0.75)")
                    log_code.append("IQR = Q3 - Q1")
                    log_code.append(
                        f"df = df[(df['{col_name}'] >= Q1-1.5*IQR) & (df['{col_name}'] <= Q3+1.5*IQR)]"
                    )

                elif action == "none":
                    print("  No action taken.")
        return current_df

    updated_df = apply_outlier_logic(user_plan, all_outlier_ids, updated_df)

    if uncovered_ids:
        print(f"\n⚠️  The following columns with outliers were NOT mentioned:")
        print(
            outlier_cols_info[outlier_cols_info["id"].isin(uncovered_ids)][
                ["id", "column_name", "outliers_pct"]
            ]
        )

        while True:
            choice = input(
                "\nWhat to do with these columns?\n"
                "1: Provide custom actions now\n"
                "2: Apply my original global suggestions\n"
                "3: Do nothing (leave outliers as-is)\n"
                "Enter 1, 2, or 3: "
            ).strip()

            if choice == "1":
                print("\nProvide additional plan for these columns:")
                extra_input = input("Additional plan: ").strip()
                extra_plan = parse_outlier_plan(extra_input)
                updated_df = apply_outlier_logic(extra_plan, uncovered_ids, updated_df)
                break

            elif choice == "2":
                print("Applying original global suggestions to uncovered columns...")
                temp_plan = {}
                for col_id in uncovered_ids:
                    act = global_suggestion.get(col_id, "cap")
                    temp_plan.setdefault(act, set()).add(col_id)
                updated_df = apply_outlier_logic(temp_plan, uncovered_ids, updated_df)
                break

            elif choice == "3":
                print("Leaving outliers untouched in uncovered columns.")
                break

            else:
                print("Invalid choice. Try again.")

    print(f"\nOutlier handling complete. Final shape: {updated_df.shape}")
    updated_info = get_df_info(updated_df)

    if log_list is not None and log_code:
        log_list.append(("Handle Outliers", log_code))

    return updated_df, updated_info
