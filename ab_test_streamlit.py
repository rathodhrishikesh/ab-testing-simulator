# streamlit run ab_test_streamlit_v3.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ----------------------
# Dummy Data Generator
# ----------------------
def generate_dummy_data(num_users=1000):
    np.random.seed(42)
    data = {
        "user_id": [f"user_{i}" for i in range(num_users)],
        "age": np.random.randint(18, 65, size=num_users),
        "location": np.random.choice(["US", "IN", "UK", "CA"], size=num_users),
        "device": np.random.choice(["Mobile", "Desktop"], size=num_users),
        "click_rate": np.random.rand(num_users),
        "converted": np.random.choice([0, 1], size=num_users, p=[0.85, 0.15])
    }
    return pd.DataFrame(data)

# ----------------------
# App Start
# ----------------------
st.set_page_config(page_title="A/B Testing Dashboard", layout="wide")
st.title("📊 A/B Testing Program - Referral Engine")

# Sidebar - Configuration
st.sidebar.header("🔧 Configuration")
data_option = st.sidebar.radio("Choose Data Source", ["Generate Dummy Data", "Upload CSV"])

df = None
file_uploaded = False

if data_option == "Generate Dummy Data":
    num_users = st.sidebar.number_input("Number of Users", min_value=100, max_value=5000, value=1000, step=100)
    df = generate_dummy_data(int(num_users))

else:
    uploaded_file = st.sidebar.file_uploader(
        "Upload a CSV file", 
        type="csv", 
        label_visibility="visible"
    )
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        file_uploaded = True
        st.sidebar.success("✅ Upload successful!")

# Variant setup
st.sidebar.markdown("---")
st.sidebar.subheader("🧪 A/B Test Setup")
variant_a = st.sidebar.text_input("Variant A Name", "Reward $5")
variant_b = st.sidebar.text_input("Variant B Name", "Reward $10")
split = st.sidebar.number_input("Split Percentage (A/B)", min_value=10, max_value=90, value=50, step=5)

# Run button
run_analysis = st.sidebar.button("🚀 Run Simulation")

if run_analysis and df is not None:

    # Assign variants
    split_index = int(len(df) * (split / 100))
    df["variant"] = ["A"] * split_index + ["B"] * (len(df) - split_index)
    df = df.sample(frac=1).reset_index(drop=True)

    # ----------------------
    # Dashboard Tabs
    # ----------------------
    tab1, tab2, tab3 = st.tabs(["📋 Summary", "📈 Charts", "📤 Export"])

    with tab1:
        st.subheader("User Data Preview")
        st.dataframe(df.head(100))

        st.subheader("Conversion Summary")
        conv_summary = df.groupby("variant")["converted"].agg(["count", "sum"])
        conv_summary["conversion_rate"] = (conv_summary["sum"] / conv_summary["count"]) * 100
        conv_summary.columns = ["Users", "Conversions", "Conversion Rate (%)"]
        st.dataframe(conv_summary.reset_index())

    with tab2:
        st.subheader("Conversion Rate Comparison")
        chart_data = df.groupby("variant")["converted"].mean().reset_index()
        chart_data["converted"] *= 100
        fig = px.bar(chart_data, x="variant", y="converted", color="variant",
                     labels={"converted": "Conversion Rate (%)", "variant": "Variant"},
                     title="A/B Test Results")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("User Distribution by Location")
        location_data = df.groupby(["variant", "location"]).size().reset_index(name="count")
        fig2 = px.bar(location_data, x="location", y="count", color="variant", barmode="group",
                      title="User Distribution by Location")
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.subheader("Download Data")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download A/B Test Data as CSV", csv, "ab_test_data.csv", "text/csv")

        st.success("App ready. Share insights or plug into referral strategy!")

elif not run_analysis and df is not None:
    st.info("✅ Configure your test and click **Run Simulation** to generate results.")

elif not df:
    st.warning("⚠️ Please upload a file or generate dummy data to continue.")
