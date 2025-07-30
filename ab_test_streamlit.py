# streamlit run ab_test_streamlit_v4.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import chi2_contingency

# ----------------------
# Dummy Data Generator
# ----------------------
def generate_dummy_data(num_users=1000, use_seed=True):
    if use_seed:
        np.random.seed(42)
    data = {
        "user_id": [f"user_{i}" for i in range(num_users)],
        "age": np.random.randint(18, 65, size=num_users),
        "location": np.random.choice(["US", "IN", "UK", "CA"], size=num_users),
        "device": np.random.choice(["Mobile", "Desktop"], size=num_users),
        "click_rate": np.random.rand(num_users),
        "converted": np.random.choice([0, 1], size=num_users, p=[0.85, 0.15]),
        "engaged": np.random.choice([0, 1], size=num_users, p=[0.3, 0.7]),
        "signed_up": np.random.choice([0, 1], size=num_users, p=[0.5, 0.5])
    }
    return pd.DataFrame(data)

# ----------------------
# App Start
# ----------------------
st.set_page_config(page_title="A/B Testing Dashboard", layout="wide")
st.title("📊 A/B Testing Simulator")

# Sidebar - Configuration
st.sidebar.header("🔧 Configuration")
data_option = st.sidebar.radio("Choose Data Source", ["Generate Dummy Data", "Upload CSV"])

st.sidebar.markdown("---")
use_seed = st.sidebar.toggle("Use fixed random seed (42)?", value=True)

df = None
file_uploaded = False

if data_option == "Generate Dummy Data":
    num_users = st.sidebar.number_input("Number of Users", min_value=100, max_value=5000, value=1000, step=100)
    df = generate_dummy_data(int(num_users), use_seed=use_seed)

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

        # Group and calculate metrics
        metrics = df.groupby("variant").agg({
            "converted": ["count", "sum", "mean"],
            "engaged": "mean",
            "signed_up": "mean"
        })
        metrics.columns = ["Users", "Conversions", "Conversion Rate (%)", "Engagement Rate (%)", "Signup Rate (%)"]
        metrics["Conversion Rate (%)"] *= 100
        metrics["Engagement Rate (%)"] *= 100
        metrics["Signup Rate (%)"] *= 100
        metrics = metrics.rename(index={"A": variant_a, "B": variant_b})

        st.dataframe(metrics.reset_index())

        # Statistical significance
        st.subheader("Statistical Significance: Conversion Rates")
        cont_table = pd.crosstab(df["variant"], df["converted"])
        chi2, p, dof, expected = chi2_contingency(cont_table)

        significance_result = "✅ Statistically Significant" if p < 0.05 else "⚠️ Not Statistically Significant"

        st.markdown(f"**p-value:** {p:.4f} — {significance_result}")

    with tab2:
        st.subheader("Conversion Rate Comparison")
        chart_data = df.groupby("variant")["converted"].mean().reset_index()
        chart_data["converted"] *= 100
        fig = px.bar(chart_data, x="variant", y="converted", color="variant",
                     labels={"converted": "Conversion Rate (%)", "variant": "Variant"},
                     title="A/B Test: Conversion Rates")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Engagement and Signup Rate Comparison")
        for metric in ["engaged", "signed_up"]:
            chart_data = df.groupby("variant")[metric].mean().reset_index()
            chart_data[metric] *= 100
            fig = px.bar(chart_data, x="variant", y=metric, color="variant",
                         labels={metric: f"{metric.replace('_', ' ').title()} (%)", "variant": "Variant"},
                         title=f"A/B Test: {metric.replace('_', ' ').title()} Rate")
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Download Data")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download A/B Test Data as CSV", csv, "ab_test_data.csv", "text/csv")

        st.success("App ready. Share insights or plug into referral strategy!")

elif not run_analysis and df is not None:
    st.info("Configure your test and click **Run Simulation** to generate results.")

elif not df:
    st.warning("⚠️ Please upload a file or generate dummy data to continue.")
