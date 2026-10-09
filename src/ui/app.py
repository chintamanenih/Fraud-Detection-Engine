# src/ui/app.py
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import networkx as nx

# Page configuration
st.set_page_config(
    page_title="Enterprise Fraud & Risk Command Center",
    page_icon="🛡️",
    layout="wide"
)

# Enterprise Custom CSS Styling
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #161b22;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #30363d;
    }
    .fraud-alert {
        padding: 20px;
        border-radius: 8px;
        background-color: rgba(248, 81, 73, 0.1);
        border: 1px solid #f85149;
        color: #f85149;
        font-weight: bold;
    }
    .safe-pass {
        padding: 20px;
        border-radius: 8px;
        background-color: rgba(46, 160, 67, 0.1);
        border: 1px solid #2ea043;
        color: #2ea043;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Safe API URL resolution with container startup handling
API_URL = "http://api:8000"
try:
    res = requests.get("http://api:8000/health", timeout=1)
    if res.status_code != 200:
        API_URL = "http://127.0.0.1:8000"
except requests.exceptions.ConnectionError:
    API_URL = "http://api:8000"

# Header Section
st.title("🛡️ Enterprise Fraud & Risk Command Center")
st.markdown("Real-time transaction anomaly detection powered by **Isolation Forest** ML pipelines and **NetworkX** graph syndicate analytics.")
st.divider()

# Navigation Tabs
tab1, tab2, tab3 = st.tabs(["⚡ Live Triage & Scoring", "📊 Audit Ledger & Analytics", "🕸️ Syndicate Network Intelligence"])

# --- TAB 1: LIVE TRIAGE ---
with tab1:
    col_form, col_result = st.columns([1, 1.5], gap="large")
    
    with col_form:
        st.subheader("💳 Transaction Ingestion")
        with st.form("transaction_form"):
            tx_id = st.text_input("Transaction ID", value=f"tx_{int(datetime.utcnow().timestamp())}")
            user_id = st.text_input("User ID", value="user_99")
            amount = st.number_input("Transaction Amount ($)", min_value=1.0, max_value=100000.0, value=250.50)
            device_id = st.text_input("Device ID", value="device_abc")
            ip_address = st.text_input("IP Address", value="192.168.1.15")
            
            submit_btn = st.form_submit_button("Evaluate Risk Profile", use_container_width=True)

    with col_result:
        st.subheader("🔍 Real-Time Evaluation Result")
        if submit_btn:
            payload = {
                "transaction_id": tx_id,
                "user_id": user_id,
                "amount": amount,
                "device_id": device_id,
                "ip_address": ip_address
            }
            
            try:
                response = requests.post(f"{API_URL}/v1/score", json=payload)
                if response.status_code == 200:
                    res_data = response.json()
                    
                    risk_pct = res_data['risk_score'] * 100
                    if risk_pct > 50 or res_data['is_anomaly'] or res_data['collusive_ring_detected']:
                        st.markdown(f'<div class="fraud-alert">🚨 HIGH RISK / ANOMALY DETECTED (Risk Score: {risk_pct:.1f}%)</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="safe-pass">✅ TRANSACTION APPROVED (Risk Score: {risk_pct:.1f}%)</div>', unsafe_allow_html=True)
                    
                    st.write("")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Isolation Forest Anomaly", str(res_data['is_anomaly']))
                    m2.metric("Collusive Ring Flag", str(res_data['collusive_ring_detected']))
                    m3.metric("Engine Latency", f"{res_data['latency_ms']} ms")
                else:
                    st.error(f"API Error: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Connection failed. Ensure the FastAPI backend is running.")
        else:
            st.info("Submit a transaction profile on the left to execute multi-dimensional risk scoring.")

# --- TAB 2: AUDIT LEDGER ---
with tab2:
    st.subheader("📜 Historical Transaction Ledger & Compliance")
    try:
        history_res = requests.get(f"{API_URL}/v1/transactions")
        if history_res.status_code == 200:
            data = history_res.json()
            if data:
                df = pd.DataFrame(data)
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Scored", len(df))
                c2.metric("Flagged Anomalies", int(df["is_anomaly"].sum()))
                c3.metric("Syndicate Rings", int(df["collusive_ring_detected"].sum()))
                c4.metric("Avg Risk Score", f"{df['risk_score'].mean() * 100:.1f}%")
                
                st.write("")
                
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Regulatory Compliance Report (CSV)",
                    data=csv_data,
                    file_name=f"fraud_audit_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                st.write("")
                search_query = st.text_input("🔍 Filter Ledger by User ID or Transaction ID", "")
                if search_query:
                    df = df[df["user_id"].str.contains(search_query, case=False) | df["transaction_id"].str.contains(search_query, case=False)]
                
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No recorded transactions found in the database yet.")
    except Exception as e:
        st.warning("Could not connect to database storage layer.")

# --- TAB 3: NETWORK INTELLIGENCE ---
with tab3:
    st.subheader("🕸️ Graph Collusion & Infrastructure Mapping")
    try:
        history_res = requests.get(f"{API_URL}/v1/transactions")
        if history_res.status_code == 200 and history_res.json():
            df_net = pd.DataFrame(history_res.json())
            
            G = nx.Graph()
            for _, row in df_net.iterrows():
                G.add_edge(row["user_id"], row["device_id"], relation="uses_device")
                G.add_edge(row["user_id"], row["ip_address"], relation="connects_from_ip")
            
            nc1, nc2, nc3 = st.columns(3)
            nc1.metric("Tracked Entities (Nodes)", G.number_of_nodes())
            nc2.metric("Infrastructure Links (Edges)", G.number_of_edges())
            nc3.metric("Connected Components", nx.number_connected_components(G))
            
            st.markdown("This graph layer tracks multi-user infrastructure intersections. When multiple distinct users share matching devices and IP addresses concurrently, the engine flags syndicate ring activity.")
        else:
            st.info("Insufficient data to build network topology graph.")
    except Exception:
        st.info("Network graph service unavailable.")