import pandas as pd
from sklearn.preprocessing import LabelEncoder

from data_utils import get_df_info


def handle_categorical_encoding(df, df_info, log_list=None):
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    if len(cat_cols) == 0:
        print("No categorical columns found. Skipping encoding.")
        return df, df_info

    print("\n=== CATEGORICAL ENCODING ===")
    print("Converting text columns to numbers for ML models.\n")

    cat_data = []
    for col in cat_cols:
        unique_count = df[col].nunique()
        cat_data.append({"column_name": col, "unique_count": unique_count})

    cat_summary = pd.DataFrame(cat_data)

    cat_info = df_info[df_info["column_name"].isin(cat_cols)].copy()
    cat_info = cat_info.merge(cat_summary, on="column_name")

    print(cat_info[["id", "column_name", "unique_count"]].to_string(index=False))

    global_suggestion = {}
    for _, row in cat_info.iterrows():
        col_id = row["id"]
        if row["unique_count"] <= 10:
            global_suggestion[col_id] = "one_hot"
        else:
            global_suggestion[col_id] = "label"

    print("\n=== GLOBAL SUGGESTION ===")
    for col_id, action in global_suggestion.items():
        col_name = df_info[df_info["id"] == col_id]["column_name"].iloc[0]
        u_count = cat_info[cat_info["id"] == col_id]["unique_count"].iloc[0]
        print(f"ID {col_id} ({col_name}): {action} (Unique: {u_count})")

    approve = input("\nDo you approve? (y/n): ").strip().lower()

    if approve == "y":
        user_plan = {"one_hot": set(), "label": set(), "skip": set()}
        for cid, act in global_suggestion.items():
            user_plan[act].add(cid)
    else:
        print("\nFormat: one_hot -1,2 ; label -3 ; skip -4 ;")
        user_input = input("Your plan: ").strip()

        user_plan = {"one_hot": set(), "label": set(), "skip": set()}
        parts = [p.strip() for p in user_input.split(";") if p.strip()]
        for part in parts:
            if "one_hot" in part:
                key = "one_hot"
            elif "label" in part:
                key = "label"
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
                print(f"Error parsing '{part}'")

    updated_df = df.copy()
    log_code = []

    le_ids = [cid for cid in user_plan["label"] if cid in cat_info["id"].values]
    for col_id in le_ids:
        col_name = df_info[df_info["id"] == col_id]["column_name"].iloc[0]
        le = LabelEncoder()
        updated_df[col_name] = le.fit_transform(updated_df[col_name].astype(str))
        print(f"Label Encoded: {col_name}")
        log_code.append("le = LabelEncoder()")
        log_code.append(f"df['{col_name}'] = le.fit_transform(df['{col_name}'].astype(str))")

    oh_ids = [cid for cid in user_plan["one_hot"] if cid in cat_info["id"].values]
    cols_to_dummy = [df_info[df_info["id"] == cid]["column_name"].iloc[0] for cid in oh_ids]

    if cols_to_dummy:
        print(f"One-Hot Encoding: {cols_to_dummy}")
        updated_df = pd.get_dummies(updated_df, columns=cols_to_dummy, drop_first=True)
        log_code.append(f"df = pd.get_dummies(df, columns={cols_to_dummy}, drop_first=True)")

    if log_list is not None and log_code:
        log_list.append(("Categorical Encoding", log_code))

    new_info = get_df_info(updated_df)
    return updated_df, new_info
