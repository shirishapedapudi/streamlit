import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

# Load dataset
@st.cache_data  # Cache data to improve performance
def load_data():
    file_path = "IndianMigrationHistory.csv"  # Ensure correct path
    df = pd.read_csv(file_path)
    df = df.rename(columns=lambda x: x.strip())  # Remove leading/trailing spaces
    return df

df = load_data()

# Sidebar Filters
st.title("📊 Indian Migration Analysis Dashboard")
st.sidebar.header("🔍 Filters")

# Destination Country Filter (Multi-Select)
countries = df["Country Dest Name"].dropna().unique()
selected_countries = st.sidebar.multiselect("Select Destination Country", options=countries, default=countries[:3])

# Gender Filter (Multi-Select)
genders = df["Migration by Gender Name"].dropna().unique()
selected_genders = st.sidebar.multiselect("Select Gender", options=genders, default=genders)

# Year Selection
year_columns = [col for col in df.columns if col.endswith("[2000]") or col.endswith("[1990]") or col.endswith("[1980]")]
selected_year = st.sidebar.selectbox("Select Year for Analysis", year_columns)

# Filter Data
filtered_df = df[df["Country Dest Name"].isin(selected_countries) & df["Migration by Gender Name"].isin(selected_genders)]

# Data Visualization
st.subheader("📈 Migration Trends Over Time")
df_melted = df.melt(id_vars=["Country Dest Name", "Migration by Gender Name"],
                    var_name="Year", value_name="Migration Count")
fig = px.line(df_melted, x="Year", y="Migration Count", color="Country Dest Name",
              title="Migration Trends Over Years", markers=True)
st.plotly_chart(fig, use_container_width=True)

st.subheader("📊 Gender-wise Migration Analysis")
fig2 = px.bar(filtered_df, x="Migration by Gender Name", y=selected_year,
              title="Migration Distribution by Gender",
              color="Migration by Gender Name", text_auto=True)
st.plotly_chart(fig2, use_container_width=True)

# Geographical Visualization with PyDeck
st.subheader("🌍 Geographical Migration Distribution")

# Prepare data for PyDeck
geo_data = filtered_df.copy()
geo_data["latitude"] = [28.6139 if "India" in c else 0 for c in geo_data["Country Dest Name"]]  # Dummy values
geo_data["longitude"] = [77.2090 if "India" in c else 0 for c in geo_data["Country Dest Name"]]

layer = pdk.Layer(
    "ScatterplotLayer",
    geo_data,
    get_position='[longitude, latitude]',
    get_radius=f'{selected_year}',
    get_color='[200, 30, 0, 160]',
    pickable=True,
)

view_state = pdk.ViewState(
    latitude=20.5937, longitude=78.9629, zoom=2, pitch=50
)

st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "Migration Count: {selected_year}"}))

st.write("### 🧐 Key Insights")
st.write(f"📌 **Total Migration Count in {selected_year}:** {filtered_df[selected_year].sum():,.0f}")
