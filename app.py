
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
df=pd.read_csv("europe_temperature.csv",skiprows=5)
#filtering
# Sidebar filter

df.columns = df.columns.str.strip()
# fix typo in column name from the source CSV
df.rename(columns={'HadCRUT5': 'HadCRUTS'}, inplace=True)
df.replace(-9999.0, np.nan, inplace=True)
#filtering
st.sidebar.header("Filter by Year")

min_year = int(df["Year"].min())
max_year = int(df["Year"].max())

selected_year = st.sidebar.slider(
    "Select Year Range",
    min_year,
    max_year,
    (min_year, max_year)
)
if st.sidebar.button("Reset Year Filter"):
    st.rerun()

filtered_df = df[
    (df["Year"] >= selected_year[0]) &
    (df["Year"] <= selected_year[1])
]
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Average ERA5 Temperature",
        round(filtered_df["ERA5"].mean(), 2)
    )

with col2:
    st.metric(
        "Maximum ERA5 Temperature",
        round(filtered_df["ERA5"].max(), 2)
    )

with col3:
    st.metric(
        "Minimum ERA5 Temperature",
        round(filtered_df["ERA5"].min(), 2)
    )
    st.download_button(
    label="Download Filtered Data CSV",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_temperature_data.csv",
    mime="text/csv"
)
st.subheader("Data Preview")

st.dataframe(filtered_df.head(20))   
    
#tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["Temperature Trend", "Box Plot", "Distribution", "Correlation"]
)

st.title("Europe Temperature Analysis(1970-2020)")
st.sidebar.title("About This Project")

st.sidebar.info(
    """
    This dashboard analyzes European temperature trends
    from 1970 to 2020.

    Datasets:
    - ERA5
    - JRA-55
    - Berkeley Earth
    - GISTEMP
    - HadCRUTS
    - NOAAGlobalTemp
    """
)
st.write("This is a temperature analysis of Europe from 1970 to 2020 using various datasets including ERA5, JRA-55, Berkeley Earth, GISTEMP, HadCRUTS, and NOAAGlobalTemp.")
with tab1:
    st.subheader("Temperature Trend")
fig, ax = plt.subplots(figsize=(12,6))
ax.plot(filtered_df["Year"],filtered_df["ERA5"],label="ERA5")
ax.plot(filtered_df["Year"],filtered_df["JRA-55"],label="JRA-55")
ax.plot(filtered_df["Year"],filtered_df["Berkeley Earth"],label="Berkeley Earth")
ax.plot(filtered_df["Year"],filtered_df["GISTEMP"],label="GISTEMP")
ax.plot(filtered_df["Year"],filtered_df["HadCRUTS"],label="HadCRUTS")
ax.plot(filtered_df["Year"],filtered_df["NOAAGlobalTemp"],label="NOAAGlobalTemp")

ax.set_xlabel("Year")
ax.set_ylabel("Temperature (°C)")
ax.legend()
st.pyplot(fig)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv("europe_temperature.csv", skiprows=5)
df.columns = df.columns.str.strip()
st.write(df.columns)
st.title("Europe Temperature Analysis (1970-2020)")
st.write(df.head(30))

fig, ax = plt.subplots(figsize=(10,5))

ax.plot(
    df["Year"],
    df["ERA5"]
)

ax.set_xlabel("Year")
ax.set_ylabel("Temperature")

st.pyplot(fig)

#ADDING BOXPLOT
import seaborn as sns
with tab2:
    st.subheader("Temperature Box Plot")
    fig, ax = plt.subplots(figsize=(8,5))

    sns.boxplot(
        y=filtered_df["ERA5"],
        ax=ax
    )
    ax.set_ylabel("Temperature")
    st.pyplot(fig)

#adding histogram
with tab3:
    st.subheader("Temperature Distribution")
    fig, ax = plt.subplots(figsize=(8,5))
    sns.histplot(
    df["ERA5"],
    bins=30,
    kde=True,
    ax=ax
)
    ax.set_xlabel("Temperature")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

#heatmap
with tab4:
    st.subheader("Correlation Heatmap") 
    fig, ax = plt.subplots(figsize=(8,5))
    corr = df.corr(numeric_only=True)
    sns.heatmap(
    corr,
    annot=True,
    cmap="coolwarm",
    ax=ax
)
    st.pyplot(fig)