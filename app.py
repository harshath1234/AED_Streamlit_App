import streamlit as st
import pandas as pd
import datetime
import os
import matplotlib.pyplot as plt

# -------------------------------------------------
# Page configuration
# -------------------------------------------------
st.set_page_config(
    page_title="AED Patient Data Management System",
    layout="wide"
)

# -------------------------------------------------
# Logging utility
# -------------------------------------------------
LOG_FILE = "activity_log.txt"

def log_action(action):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {action}\n")

# -------------------------------------------------
# Load dataset
# -------------------------------------------------
DATA_FILE = "AED4weeks.csv"

if not os.path.exists(DATA_FILE):
    st.error("AED4weeks.csv not found in the current directory.")
    st.stop()

df = pd.read_csv(DATA_FILE)

# Convert Breachornot to binary
df["Breach_binary"] = df["Breachornot"].map({
    "non-breach": 0,
    "breach": 1
})

# -------------------------------------------------
# App title
# -------------------------------------------------
st.title("🩺 AED Patient Data Management System")
st.markdown("Interactive system for managing and analysing Accident & Emergency Department data.")

# -------------------------------------------------
# Sidebar menu
# -------------------------------------------------
menu = st.sidebar.radio(
    "Select an action",
    [
        "Dashboard",
        "Search Patient by ID",
        "Filter Patients",
        "Modify Patient Data",
        "Delete Patient Data"
    ]
)

# =================================================
# DASHBOARD
# =================================================
if menu == "Dashboard":
    st.subheader("📊 Dashboard Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Patients", len(df))
    col2.metric("Breach Cases", int(df["Breach_binary"].sum()))
    col3.metric("Average Length of Stay", round(df["LoS"].mean(), 2))

    st.markdown("### Breach vs Non-Breach Distribution")
    fig, ax = plt.subplots()
    df["Breach_binary"].value_counts().rename(
        {0: "Non-breach", 1: "Breach"}
    ).plot(kind="bar", ax=ax)
    ax.set_xlabel("Patient Outcome")
    ax.set_ylabel("Number of Patients")
    st.pyplot(fig)

    st.markdown("### Length of Stay Distribution")
    fig2, ax2 = plt.subplots()
    df["LoS"].hist(bins=30, ax=ax2)
    ax2.set_xlabel("Length of Stay (minutes)")
    ax2.set_ylabel("Frequency")
    st.pyplot(fig2)

    log_action("Viewed dashboard")

# =================================================
# SEARCH PATIENT BY ID
# =================================================
elif menu == "Search Patient by ID":
    st.subheader("🔍 Search Patient by ID")

    patient_id = st.text_input("Enter Patient ID")

    if st.button("Search"):
        result = df[df["ID"] == patient_id]

        if result.empty:
            st.warning("No patient found with this ID.")
            log_action(f"Searched Patient ID {patient_id} – Not found")
        else:
            st.success("Patient record found.")
            st.dataframe(result)
            log_action(f"Retrieved Patient ID {patient_id}")

# =================================================
# FILTER PATIENTS
# =================================================
elif menu == "Filter Patients":
    st.subheader("🎯 Filter Patients by Range")

    numeric_columns = [
        "Age", "LoS", "noofinvestigation",
        "nooftreatment", "noofpatients"
    ]

    column = st.selectbox("Select variable", numeric_columns)

    min_val = int(df[column].min())
    max_val = int(df[column].max())

    selected_range = st.slider(
        f"Select range for {column}",
        min_val, max_val, (min_val, max_val)
    )

    filtered_df = df[
        (df[column] >= selected_range[0]) &
        (df[column] <= selected_range[1])
    ]

    st.write(f"Patients with {column} in range {selected_range}")
    st.dataframe(filtered_df)

    log_action(f"Filtered patients by {column} range {selected_range}")

elif menu == "Modify Patient Data":
    st.subheader("✏️ Modify Patient Record")

    patient_id = st.text_input("Enter Patient ID to modify")

    if patient_id in df["ID"].values:
        patient = df[df["ID"] == patient_id].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            age = st.number_input("Age", value=int(patient["Age"]))
            los = st.number_input("Length of Stay", value=int(patient["LoS"]))

        with col2:
            investigations = st.number_input(
                "Number of Investigations",
                value=int(patient["noofinvestigation"])
            )
            treatments = st.number_input(
                "Number of Treatments",
                value=int(patient["nooftreatment"])
            )

        breach = st.selectbox(
            "Breach",
            ["non-breach", "breach"],
            index=0 if patient["Breachornot"] == "non-breach" else 1
        )

        if st.button("Update Record"):
            # Get the row index
            row_index = df.index[df["ID"] == patient_id][0]

            # Update column by column
            df.at[row_index, "Age"] = age
            df.at[row_index, "LoS"] = los
            df.at[row_index, "noofinvestigation"] = investigations
            df.at[row_index, "nooftreatment"] = treatments
            df.at[row_index, "Breachornot"] = breach

            # Save safely
            temp_file = "AED4weeks_temp.csv"
            df.to_csv(temp_file, index=False)
            os.replace(temp_file, DATA_FILE)

            st.success("Patient record updated successfully.")
            log_action(f"Modified Patient ID {patient_id}")

    else:
        st.info("Enter a valid Patient ID to modify.")


# =================================================
# DELETE PATIENT DATA
# =================================================
elif menu == "Delete Patient Data":
    st.subheader("🗑️ Delete Patient Record")

    patient_id = st.text_input("Enter Patient ID to delete")
    confirm = st.checkbox("I confirm that I want to permanently delete this record")

    if st.button("Delete"):
        if not confirm:
            st.warning("Please confirm deletion before proceeding.")
        elif patient_id in df["ID"].values:
            df = df[df["ID"] != patient_id]
            df.to_csv(DATA_FILE, index=False)
            st.success("Patient record deleted successfully.")
            log_action(f"Deleted Patient ID {patient_id}")
        else:
            st.warning("Patient ID not found.")
            log_action(f"Attempted delete for Patient ID {patient_id} – Not found")

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.write("📄 All user actions are logged for audit purposes.")


