
import streamlit as st
import pandas as pd
import os
from io import BytesIO
import io

# Now I am setting up my first Python app
st.set_page_config(page_title="Data Sweeper", layout='wide')

# Custom CSS
st.markdown(
    """
    <style>
    .stApp {
        background-color: black;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Data and description
st.title("Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization!")

# File uploader (multiple files upload)
uploaded_files = st.file_uploader("Upload your files (accepts CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

# Check if files are uploaded
if uploaded_files:
    for file in uploaded_files:
        # Use the file's name attribute, but we need to access it properly
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Check for valid file types and read them accordingly
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # Display information about the file
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size / 1024} KB")

        # Show five rows of our data frame (df)
        st.write("Preview the head of the DataFrame")
        st.dataframe(df.head())

        # Options for data cleaning
        st.subheader(f"Data cleaning options for {file.name}")
        if st.checkbox(f"Clean data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates Removed!")

            with col2:
                if st.button(f"Fill missing values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("Missing values have been filled!")

            # Select columns to keep
            st.subheader("Select columns to keep")
            columns = st.multiselect(f"Choose columns for {file.name}", df.columns, default=df.columns)
            df = df[columns]

            # Data visualization
            st.subheader("Data Visualization")
            if st.checkbox(f"Show visualization for {file.name}"):    
                # Filter numeric columns from the dataframe
                numeric_data = df.select_dtypes(include=['number'])
                if not numeric_data.empty:
                    # Choose the first 2 columns (or adjust as necessary) to plot
                    st.bar_chart(numeric_data.iloc[:, :2])  # You can change how many columns to display
                else:
                    st.warning("No numeric data available for visualization.")

            # Conversion options
            st.subheader("Conversion Options")
            conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)

            # Define the buffer for file conversion
            buffer = io.BytesIO()

            # Ensure this block is inside the 'if st.button()' check
            if st.button(f"Convert {file.name}"):

                if conversion_type == 'CSV':
                    df.to_csv(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".csv")
                    mime_type = "text/csv"

                elif conversion_type == "Excel":
                    df.to_excel(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    buffer.seek(0)

                # Provide download button
                st.download_button(
                    label=f"Download {file.name} as {conversion_type}",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type
                )
                st.success(f"File '{file.name}' processed successfully!")

    