import streamlit as st
import pandas as pd
from io import BytesIO

# Set the title
st.title("📊 Student Event Summary Generator")

# Define the events to count
EVENTS_TO_COUNT = ['page_blurred', 'page_focused', 'question_answered']

# File uploader
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    try:
        # Read CSV into a DataFrame
        df = pd.read_csv(uploaded_file)

        st.success("CSV loaded successfully!")

        # Display column options for selecting ID and Event columns
        st.subheader("Step 1: Select Columns")
        columns = df.columns.tolist()

        student_col = st.selectbox("Select Student Identifier Column", columns)
        event_col = st.selectbox("Select Event Column", columns)

        if st.button("Generate Summary"):
            # Filter and count events
            summary = (
                df[df[event_col].isin(EVENTS_TO_COUNT)]
                .groupby(student_col)[event_col]
                .value_counts()
                .unstack(fill_value=0)
                .reindex(columns=EVENTS_TO_COUNT, fill_value=0)
                .reset_index()
            )

            # Display summary
            st.subheader("📋 Summary Table")
            st.dataframe(summary)

            # Download link
            def convert_df(df):
                return df.to_csv(index=False).encode('utf-8')

            csv_bytes = convert_df(summary)
            st.download_button(
                label="📥 Download Summary CSV",
                data=csv_bytes,
                file_name="student_summary.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Error processing file: {e}")
