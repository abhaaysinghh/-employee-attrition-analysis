
import pandas as pd

REQUIRED_COLUMNS = [
    "Employee_ID",
    "Age",
    "Gender",
    "Department",
    "Job_Role",
    "Monthly_Income",
    "Years_At_Company",
    "Total_Working_Years",
    "OverTime",
    "Job_Satisfaction",
    "Work_Life_Balance",
    "Attrition"
]


def load_employee_data(uploaded_file):

    if uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    elif uploaded_file.name.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)

    else:
        raise ValueError("Upload a CSV or Excel file.")

    missing = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    if df.empty:
        raise ValueError("The uploaded dataset is empty.")

    return df


def clean_employee_data(df):

    df = df.copy()

    df = df.drop_duplicates()

    df = df.dropna(subset=["Employee_ID"])

    df["Employee_ID"] = (
        df["Employee_ID"].astype(str).str.strip()
    )

    df = df.drop_duplicates(
        subset=["Employee_ID"],
        keep="first"
    )

    return df
