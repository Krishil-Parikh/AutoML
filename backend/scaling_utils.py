import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler


def handle_feature_scaling(df, df_info, log_list=None):
    numeric_cols = df.select_dtypes(include=["float64", "int64", "int32"]).columns
    numeric_cols = [c for c in numeric_cols if df[c].nunique() > 2]

    if not numeric_cols:
        print("No numeric columns require scaling.")
        return df, df_info

    print("\n=== FEATURE SCALING ===")
    print("Normalizing the range of independent variables.\n")

    scaling_data = []
    for col in numeric_cols:
        skew = df[col].skew()
        scaling_data.append({"column_name": col, "skew": skew})

    scale_summary = pd.DataFrame(scaling_data)
    scale_info = df_info[df_info["column_name"].isin(numeric_cols)].copy()
    scale_info = scale_info.merge(scale_summary, on="column_name")

    print(scale_info[["id", "column_name", "skew"]].to_string(index=False))

    global_suggestion = {}
    for _, row in scale_info.iterrows():
        col_id = row["id"]
        if abs(row["skew"]) < 1:
            global_suggestion[col_id] = "standard"
        else:
            global_suggestion[col_id] = "minmax"

    print("\n=== GLOBAL SUGGESTION ===")
    for col_id, action in global_suggestion.items():
        col_name = df_info[df_info["id"] == col_id]["column_name"].iloc[0]
        skew = scale_info[scale_info["id"] == col_id]["skew"].iloc[0]
        print(f"ID {col_id} ({col_name}): {action} (Skew: {skew:.2f})")

    approve = input("\nDo you approve? (y/n): ").strip().lower()

    user_plan = {"standard": set(), "minmax": set(), "skip": set()}
    if approve == "y":
        for cid, act in global_suggestion.items():
            user_plan[act].add(cid)
    else:
        print("\nFormat: standard -1,2 ; minmax -3 ; skip -4 ;")
        user_input = input("Your plan: ").strip()

        parts = [p.strip() for p in user_input.split(";") if p.strip()]
        for part in parts:
            if "standard" in part:
                key = "standard"
            elif "minmax" in part:
                key = "minmax"
            elif "skip" in part:
                key = "skip"
            else:
                continue
            try:
                id_str = part.split("-")[1]
                ids = set()
                for x in id_str.split(","):
                    if "-" in x:
                        s, e = map(int, x.split("-"))
                        ids.update(range(s, e + 1))
                    else:
                        ids.add(int(x))
                user_plan[key].update(ids)
            except:
                pass

    updated_df = df.copy()
    log_code = []

    std_ids = [cid for cid in user_plan["standard"] if cid in scale_info["id"].values]
    if std_ids:
        std_cols = [df_info[df_info["id"] == cid]["column_name"].iloc[0] for cid in std_ids]
        scaler = StandardScaler()
        updated_df[std_cols] = scaler.fit_transform(updated_df[std_cols])
        print(f"StandardScaled: {len(std_cols)} columns")
        log_code.append("scaler = StandardScaler()")
        log_code.append(f"df[{std_cols}] = scaler.fit_transform(df[{std_cols}])")

    mm_ids = [cid for cid in user_plan["minmax"] if cid in scale_info["id"].values]
    if mm_ids:
        mm_cols = [df_info[df_info["id"] == cid]["column_name"].iloc[0] for cid in mm_ids]
        scaler = MinMaxScaler()
        updated_df[mm_cols] = scaler.fit_transform(updated_df[mm_cols])
        print(f"MinMaxScaled: {len(mm_cols)} columns")
        log_code.append("scaler = MinMaxScaler()")
        log_code.append(f"df[{mm_cols}] = scaler.fit_transform(df[{mm_cols}])")

    if log_list is not None and log_code:
        log_list.append(("Feature Scaling", log_code))

    return updated_df, df_info
