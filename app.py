import streamlit as st
import pandas as pd
import os
import io
import openpyxl

# Set up Streamlit page
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

# App title
st.title("Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization!")

# File uploader (supports multiple files)
uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

# Process uploaded files
if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Read file into DataFrame
        try:
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file, engine="openpyxl")
            else:
                st.error(f"Unsupported file type: {file_ext}")
                continue
        except Exception as e:
            st.error(f"Error reading file {file.name}: {e}")
            continue

        # Display file information
        st.subheader(f"File: {file.name}")
        st.write(f"**File Size:** {file.size / 1024:.2f} KB")
        st.write("**Preview:**")
        st.dataframe(df.head())

        # Data cleaning options
        st.subheader(f"Data Cleaning for {file.name}")
        
        if st.checkbox(f"Clean data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("✅ Duplicates removed!")

            with col2:
                if st.button(f"Fill missing values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("✅ Missing values filled with column mean!")

            # Select columns to keep
            selected_columns = st.multiselect(f"Select columns to keep for {file.name}", df.columns, default=df.columns)
            df = df[selected_columns]

        # Data visualization
        st.subheader(f"Data Visualization for {file.name}")
        if st.checkbox(f"Show visualization for {file.name}"):
            numeric_data = df.select_dtypes(include=['number'])
            if not numeric_data.empty:
                try:
                    st.bar_chart(numeric_data)
                except Exception as e:
                    st.error(f"Error displaying chart: {e}")
            else:
                st.warning("No numeric data available for visualization.")

        # Conversion options
        st.subheader(f"Convert {file.name}")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)

        # Convert and download
        if st.button(f"Convert and Download {file.name}"):
            buffer = io.BytesIO()
            new_file_name = file.name.replace(file_ext, f".{conversion_type.lower()}")
            mime_type = ""

            try:
                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    mime_type = "text/csv"
                elif conversion_type == "Excel":
                    df.to_excel(buffer, index=False, engine="openpyxl")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                buffer.seek(0)
                st.download_button(
                    label=f"Download {new_file_name}",
                    data=buffer,
                    file_name=new_file_name,
                    mime=mime_type
                )
                st.success(f"✅ {file.name} processed successfully!")
            except Exception as e:
                st.error(f"Error converting {file.name}: {e}")
