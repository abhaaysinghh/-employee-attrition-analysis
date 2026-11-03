
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(
    0,
    os.path.join(BASE_DIR, "modules")
)

from data_management import (
    load_employee_data,
    clean_employee_data
)

st.set_page_config(
    page_title="Employee Attrition Analytics",
    layout="wide"
)

st.title("Employee Attrition & Workforce Analytics")
st.caption("HR Analytics and Decision Support System")

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Module",
    [
        "Dashboard",
        "Employee Data",
        "Workforce Analytics",
        "HR Recommendations"
    ]
)

st.sidebar.divider()

uploaded_file = st.sidebar.file_uploader(
    "Upload Employee Dataset",
    type=["csv", "xlsx", "xls"]
)

if uploaded_file is not None:

    try:
        df = load_employee_data(uploaded_file)
        df = clean_employee_data(df)

        st.sidebar.success("Dataset loaded successfully")

    except Exception as e:
        st.error(str(e))
        st.stop()

else:

    sample_path = os.path.join(
        BASE_DIR,
        "data",
        "employee_data.csv"
    )

    if os.path.exists(sample_path):
        df = pd.read_csv(sample_path)
        df = clean_employee_data(df)
        st.sidebar.info("Using sample employee data")

    else:
        st.warning("Please upload an employee dataset.")
        st.stop()


# Validate numerical fields and categories

numeric_columns = [
    "Age",
    "Monthly_Income",
    "Years_At_Company",
    "Job_Satisfaction",
    "Work_Life_Balance"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=numeric_columns)

if df.empty:
    st.error("No valid employee records available.")
    st.stop()

if not df["Attrition"].isin(["Yes", "No"]).all():
    st.error("Attrition must contain Yes or No values.")
    st.stop()


# KPI calculations

total = len(df)

left = (df["Attrition"] == "Yes").sum()

rate = left / total * 100

avg_salary = df["Monthly_Income"].mean()

avg_tenure = df["Years_At_Company"].mean()


if page == "Dashboard":

    st.header("Workforce Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Employees", f"{total:,}")
    c2.metric("Employees Left", f"{left:,}")
    c3.metric("Attrition Rate", f"{rate:.2f}%")
    c4.metric("Average Tenure", f"{avg_tenure:.1f} Years")

    c5, c6 = st.columns(2)

    c5.metric(
        "Average Monthly Salary",
        f"₹{avg_salary:,.0f}"
    )

    c6.metric(
        "Employees Retained",
        f"{total-left:,}"
    )

    st.subheader("Attrition Distribution")

    fig = px.pie(
        df,
        names="Attrition",
        title="Employees Who Left vs Retained",
        hole=0.4
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Department-wise Attrition")

    dept = (
        df.groupby("Department")
        .agg(
            Total=("Employee_ID", "count"),
            Left=("Attrition",
                  lambda x: (x == "Yes").sum())
        )
        .reset_index()
    )

    dept["Attrition Rate"] = (
        dept["Left"] / dept["Total"] * 100
    )

    fig = px.bar(
        dept,
        x="Department",
        y="Attrition Rate",
        title="Department Attrition Rate",
        text_auto=".2f"
    )

    st.plotly_chart(fig, use_container_width=True)


elif page == "Employee Data":

    st.header("Employee Data Management")

    st.write("Total records:", len(df))

    st.dataframe(
        df,
        use_container_width=True
    )

    st.subheader("Data Quality")

    quality = pd.DataFrame({
        "Missing Values": df.isnull().sum(),
        "Data Type": df.dtypes.astype(str)
    })

    st.dataframe(quality)

    st.download_button(
        "Download Employee Data",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="employee_data.csv",
        mime="text/csv"
    )


elif page == "Workforce Analytics":

    st.header("Workforce Analytics")

    selected_department = st.selectbox(
        "Select Department",
        ["All"] + sorted(df["Department"].dropna().unique().tolist())
    )

    filtered = df.copy()

    if selected_department != "All":
        filtered = filtered[
            filtered["Department"] == selected_department
        ]

    st.subheader("Salary vs Attrition")

    fig = px.box(
        filtered,
        x="Attrition",
        y="Monthly_Income",
        title="Salary Distribution by Attrition"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Overtime vs Attrition")

    overtime = (
        filtered.groupby("OverTime")
        .apply(
            lambda x: (x["Attrition"] == "Yes").mean() * 100,
            include_groups=False
        )
        .reset_index(name="Attrition Rate")
    )

    fig = px.bar(
        overtime,
        x="OverTime",
        y="Attrition Rate",
        title="Overtime Attrition Rate"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Job Satisfaction vs Attrition")

    satisfaction = (
        filtered.groupby("Job_Satisfaction")
        .apply(
            lambda x: (x["Attrition"] == "Yes").mean() * 100,
            include_groups=False
        )
        .reset_index(name="Attrition Rate")
    )

    fig = px.bar(
        satisfaction,
        x="Job_Satisfaction",
        y="Attrition Rate",
        title="Job Satisfaction vs Attrition"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Tenure vs Attrition")

    tenure = (
        filtered.groupby("Years_At_Company")
        .apply(
            lambda x: (x["Attrition"] == "Yes").mean() * 100,
            include_groups=False
        )
        .reset_index(name="Attrition Rate")
    )

    fig = px.line(
        tenure,
        x="Years_At_Company",
        y="Attrition Rate",
        markers=True,
        title="Tenure vs Attrition"
    )

    st.plotly_chart(fig, use_container_width=True)


elif page == "HR Recommendations":

    st.header("HR Recommendations")

    overtime_rates = (
        df.groupby("OverTime")
        .apply(
            lambda x: (x["Attrition"] == "Yes").mean() * 100,
            include_groups=False
        )
    )

    if (
        "Yes" in overtime_rates.index
        and "No" in overtime_rates.index
        and overtime_rates["Yes"] > overtime_rates["No"]
    ):

        st.warning(
            "Review overtime distribution and employee workload."
        )

    satisfaction_rates = (
        df.groupby(
            df["Job_Satisfaction"] <= 2
        )
        .apply(
            lambda x: (x["Attrition"] == "Yes").mean() * 100,
            include_groups=False
        )
    )

    if (
        True in satisfaction_rates.index
        and False in satisfaction_rates.index
        and satisfaction_rates[True] > satisfaction_rates[False]
    ):

        st.warning(
            "Investigate job satisfaction and employee engagement."
        )

    new = df[df["Years_At_Company"] <= 2]
    experienced = df[df["Years_At_Company"] > 2]

    if len(new) and len(experienced):

        if (
            (new["Attrition"] == "Yes").mean()
            >
            (experienced["Attrition"] == "Yes").mean()
        ):

            st.info(
                "Consider improving onboarding and mentoring programmes."
            )

    st.caption(
        "Recommendations are generated from observed group-level "
        "patterns and should be reviewed by HR managers."
    )
