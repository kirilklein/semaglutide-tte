import numpy as np
import pandas as pd
import polars as pl
from great_tables import GT, loc, style
import os

def prettify_name(name: str) -> str:
    """
    Custom renaming rules.
    """
    if pd.isna(name):
        return ""
    if name == "age_at_index_date":
        return "Patient Age"
    if name == "diabetes":
        return "Duration of diabetes"
    
    name = name.replace("_", " ")
    return name[0].upper() + name[1:]

def format_cell(row: pd.Series, group: str, col_suffix: str = "") -> tuple[str, str]:
    """
    Returns: (formatted_string, type_flag)
    type_flag is one of 'mean_sd', 'n_pct', 'none'
    """
    g_key = f"{group}{col_suffix}"
    
    mean = row.get(f"mean_{g_key}", np.nan)
    sd = row.get(f"std_{g_key}", np.nan)
    count = row.get(f"count_{g_key}", np.nan)
    pct = row.get(f"percentage_{g_key}", np.nan)

    if pd.notna(mean) and pd.notna(sd):
        return f"{mean:.2f} (±{sd:.2f})", "mean_sd"
    elif pd.notna(count) and pd.notna(pct):
        return f"{int(count):,} ({pct:.1f}%)", "n_pct"
    else:
        return np.nan, "none"

def process_dataset(binary_df, numeric_df, group_name, output_suffix=""):
    """
    Reshapes binary and numeric data for a specific group into wide format.
    """
    # Filter for the group
    bin_g = binary_df[binary_df["group"] == group_name].copy()
    num_g = numeric_df[numeric_df["group"] == group_name].copy()
    
    # Pivot Binary
    if not bin_g.empty:
        bin_wide = bin_g.set_index("criterion")[["count", "percentage"]]
        bin_wide.columns = [f"{c}_{group_name}{output_suffix}" for c in bin_wide.columns]
    else:
        bin_wide = pd.DataFrame()

    # Pivot Numeric
    if not num_g.empty:
        # Remove _numeric_value suffix for matching
        num_g["criterion_clean"] = np.where(
            num_g["criterion"].str.endswith("_numeric_value"),
            num_g["criterion"].str.replace(r"_numeric_value$", "", regex=True),
            num_g["criterion"],
        )
        num_wide = num_g.set_index("criterion_clean")[["mean", "std"]]
        num_wide.columns = [f"{c}_{group_name}{output_suffix}" for c in num_wide.columns]
    else:
        num_wide = pd.DataFrame()
        
    # Merge
    return bin_wide.join(num_wide, how="outer")

def main():
    # Configuration
    unit_dict = {
        "age_at_index_date": "years",
        "diabetes": "days",
        "estimated_glomerular_filtration_rate": "ml/min/1.73m²",
        "hemoglobin_a1c": "mmol/mol",
        "low_density_lipoprotein": "mmol/L",
        "high_density_lipoprotein": "mmol/L",
        "triglycerides": "mmol/L",
    }

    remove_rows = [
        "diabetes_icd10",
        "icd10_do24",
        "icd10_do244",
        "icd10_do24_excluding_do244",
        "diabetes_atc_antihyperglycemic",
        "weights",
        "Thiazolidinediones"
        "Glucagon-like peptide 1 agonists"

    ]
    
    # Paths (assuming script run from project root)
    DATA_DIR = "data/stats"
    FIGURES_DIR = "figures/table"
    
    try:
        binary_df = pd.read_csv(os.path.join(DATA_DIR, "raw_binary.txt"))
        numeric_df = pd.read_csv(os.path.join(DATA_DIR, "raw_numeric.txt"))
        binary_weighted_df = pd.read_csv(os.path.join(DATA_DIR, "raw_binary_weighted.txt"))
        numeric_weighted_df = pd.read_csv(os.path.join(DATA_DIR, "raw_numeric_weighted.txt"))
        print("Data loaded successfully.")
    except FileNotFoundError as e:
        print(f"Error loading data: {e}")
        print("Please run this script from the project root directory.")
        return

    # 1. Control (Unweighted)
    df_control = process_dataset(binary_df, numeric_df, "Control")

    # 2. Exposed (Unweighted)
    df_exposed = process_dataset(binary_df, numeric_df, "Exposed")

    # 3. Weighted Control (from Weighted files, group="Control")
    df_weighted_control = process_dataset(binary_weighted_df, numeric_weighted_df, "Control", output_suffix="_Weighted")

    # Combine all
    combined_raw = df_control.join(df_exposed, how="outer").join(df_weighted_control, how="outer")
    combined_raw.index.name = "criterion"
    combined_raw = combined_raw.reset_index()

    # Exclude rows
    if remove_rows:
        combined_raw = combined_raw[~combined_raw["criterion"].isin(remove_rows)]

    # Format Rows
    rows = []
    for _, row in combined_raw.iterrows():
        criterion = row["criterion"]
        
        val_ctrl, type_ctrl = format_cell(row, "Control")
        val_exp, type_exp = format_cell(row, "Exposed")
        val_w_ctrl, type_w_ctrl = format_cell(row, "Control", col_suffix="_Weighted")
        
        # Determine row type
        row_type = "none"
        for t in [type_ctrl, type_exp, type_w_ctrl]:
            if t != "none":
                row_type = t
                break
                
        unit = unit_dict.get(criterion)
        
        if row_type == "mean_sd":
            label_suffix = f" (mean {unit}, SD)" if unit else " (mean, SD)"
        elif row_type == "n_pct":
            label_suffix = " (n, %)"
        else:
            label_suffix = ""
            
        label = f"{prettify_name(criterion)}{label_suffix}"
        
        rows.append({
            "Confounder": label,
            "Control": val_ctrl,
            "Exposed": val_exp,
            "Weighted Control": val_w_ctrl
        })

    final_df = pd.DataFrame(rows)
    
    # Create Great Table
    final_pl = pl.from_pandas(final_df)

    gt_tbl = (
        GT(final_pl, rowname_col="Confounder")
        .tab_header(
            title="Baseline characteristics by exposure status",
            subtitle="Values are mean (SD) or n (%) as indicated in the row label."
        )
        .cols_label(
            Control="Control",
            Exposed="Exposed",
            **{"Weighted Control": "Weighted Control"}
        )
        .tab_spanner(
            label="Unweighted",
            columns=["Control", "Exposed"]
        )
        .tab_spanner(
            label="Weighted",
            columns=["Weighted Control"]
        )
        .tab_style(style.text(weight="bold"), loc.body(columns="Confounder"))
        .opt_row_striping()
        .opt_table_outline()
        .opt_vertical_padding(scale=0.8)
        .opt_horizontal_padding(scale=1.0)
        .opt_table_font(font="Times New Roman")
    )

    # Save
    os.makedirs(FIGURES_DIR, exist_ok=True)
    output_path = os.path.join(FIGURES_DIR, "baseline_characteristics.html")
    
    html_content = gt_tbl.as_raw_html()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Table saved to {output_path}")

if __name__ == "__main__":
    main()

