import pandas as pd
import numpy as np


def parse_correlation_plan(user_input):
    plan = {"drop": set(), "keep": set()}

    if not user_input.strip():
        return plan

    parts = [p.strip() for p in user_input.split(";") if p.strip()]

    for part in parts:
        action = None
        if part.startswith("drop"):
            action = "drop"
        elif part.startswith("keep"):
            action = "keep"
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


def handle_high_correlation(df, df_info, log_list=None, threshold=0.90):
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    if len(numeric_cols) < 2:
        print("Not enough numeric columns to check for correlation.")
        return df, df_info

    print(f"\n=== HIGH CORRELATION CHECK (Threshold > {threshold}) ===")

    corr_matrix = df[numeric_cols].corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))

    high_corr_data = []
    high_corr_cols = set()

    for col in upper.columns:
        high_corr_series = upper[col][upper[col] > threshold]
        if not high_corr_series.empty:
            high_corr_cols.add(col)
            for match_col, val in high_corr_series.items():
                high_corr_data.append(
                    {"column_name": col, "correlated_with": match_col, "val": val}
                )

    if not high_corr_cols:
        print("No columns found with correlation above the threshold. Good to go!")
        return df, df_info

    corr_summary = pd.DataFrame(high_corr_data)

    print(f"\nDetected {len(high_corr_cols)} columns that are highly correlated with others:\n")

    cols_with_issues = df_info[df_info["column_name"].isin(high_corr_cols)].copy()

    for idx, row in cols_with_issues.iterrows():
        c_name = row["column_name"]
        c_id = row["id"]
        conflicts = corr_summary[corr_summary["column_name"] == c_name]
        conflict_str = ", ".join(
            [f"{r['correlated_with']} ({r['val']:.2f})" for _, r in conflicts.iterrows()]
        )
        print(f"ID {c_id} | {c_name} <--> {conflict_str}")

    global_suggestion = {row["id"]: "drop" for _, row in cols_with_issues.iterrows()}

    print("\n=== GLOBAL SUGGESTION FOR CORRELATION ===")
    for col_id, action in global_suggestion.items():
        col_name = df_info[df_info["id"] == col_id]["column_name"].iloc[0]
        print(f"ID {col_id} ({col_name}): {action}")

    approve = input("\nDo you approve this global suggestion? (y/n): ").strip().lower()

    updated_df = df.copy()
    updated_info = df_info.copy()

    if approve == "y":
        user_plan = {"drop": set(global_suggestion.keys()), "keep": set()}
    else:
        print("\nProvide your custom plan in this format:")
        print("drop -1,2 ; keep -3,4 ;")
        print("(Note: 'keep' means you accept the high correlation and do nothing)")
        user_input = input("Your plan: ").strip()
        user_plan = parse_correlation_plan(user_input)

    covered_ids = set()
    for ids in user_plan.values():
        covered_ids.update(ids)

    all_issue_ids = set(cols_with_issues["id"])
    uncovered_ids = all_issue_ids - covered_ids

    log_code = []

    ids_to_drop = [cid for cid in user_plan["drop"] if cid in all_issue_ids]

    for col_id in ids_to_drop:
        col_name = updated_info[updated_info["id"] == col_id]["column_name"].iloc[0]
        print(f"Dropping correlated column: {col_name}")
        updated_df.drop(columns=[col_name], inplace=True)
        updated_info = updated_info[updated_info["id"] != col_id]
        log_code.append(f"df.drop(columns=['{col_name}'], inplace=True)")

    ids_to_keep = [cid for cid in user_plan["keep"] if cid in all_issue_ids]
    for col_id in ids_to_keep:
        col_name = df_info[df_info["id"] == col_id]["column_name"].iloc[0]
        print(f"Keeping correlated column: {col_name}")

    if uncovered_ids:
        print(
            f"\n⚠️  The following correlated columns were NOT mentioned:"
        )
        print(
            cols_with_issues[cols_with_issues["id"].isin(uncovered_ids)][
                ["id", "column_name"]
            ]
        )

        while True:
            choice = input(
                "\nWhat to do with these columns?\n"
                "1: Provide custom actions now\n"
                "2: Apply original suggestion (Drop all)\n"
                "3: Keep all (Do nothing)\n"
                "Enter 1, 2, or 3: "
            ).strip()

            if choice == "1":
                extra_input = input("Additional plan (drop -X; keep -Y): ").strip()
                extra_plan = parse_correlation_plan(extra_input)

                extra_drops = [cid for cid in extra_plan["drop"] if cid in uncovered_ids]
                for col_id in extra_drops:
                    col_name = df_info[df_info["id"] == col_id]["column_name"].iloc[0]
                    if col_name in updated_df.columns:
                        print(f"Dropping: {col_name}")
                        updated_df.drop(columns=[col_name], inplace=True)
                        updated_info = updated_info[updated_info["id"] != col_id]
                        log_code.append(f"df.drop(columns=['{col_name}'], inplace=True)")

                extra_keeps = [cid for cid in extra_plan["keep"] if cid in uncovered_ids]
                for col_id in extra_keeps:
                    col_name = df_info[df_info["id"] == col_id]["column_name"].iloc[0]
                    print(f"Keeping: {col_name}")
                break

            elif choice == "2":
                print("Dropping remaining highly correlated columns...")
                for col_id in uncovered_ids:
                    col_name = df_info[df_info["id"] == col_id]["column_name"].iloc[0]
                    if col_name in updated_df.columns:
                        print(f"Dropping: {col_name}")
                        updated_df.drop(columns=[col_name], inplace=True)
                        updated_info = updated_info[updated_info["id"] != col_id]
                        log_code.append(f"df.drop(columns=['{col_name}'], inplace=True)")
                break

            elif choice == "3":
                print("Keeping remaining columns.")
                break
            else:
                print("Invalid choice.")

    updated_info.reset_index(drop=True, inplace=True)
    updated_info["id"] = range(1, len(updated_info) + 1)

    print(f"\nCorrelation handling complete. Final shape: {updated_df.shape}")

    if log_list is not None and log_code:
        log_list.append(("Handle Multicollinearity", log_code))

    return updated_df, updated_info
