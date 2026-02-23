import streamlit as st
import pandas as pd
import plotly.express as px

# --- APP CONFIG ---
st.set_page_config(page_title="Nepal PR Seat Calculator", page_icon="🇳🇵")

st.title("🇳🇵 Nepal PR Seat Calculator")
st.markdown("""
This tool calculates Proportional Representation (PR) seats for the Nepal House of Representatives 
using the **Sainte-Laguë Method**.
""")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Configuration")
total_seats = st.sidebar.number_input("Total PR Seats", value=110)
threshold_pct = st.sidebar.slider("Threshold (%)", 0.0, 5.0, 3.0) / 100
use_modified = st.sidebar.checkbox("Use Modified Sainte-Laguë (1.4 first divisor)", value=False)

st.sidebar.divider()
st.sidebar.write("### Input Party Data")
st.sidebar.info("Enter data as: Party Name, Votes (or %)")

# Default Data
default_data = """Nepali Congress, 25.71
CPN-UML, 26.95
CPN-Maoist Centre, 11.13
Rastriya Swatantra Party, 10.70
Rastriya Prajatantra Party, 5.58
Janata Samajbadi Party, 3.99
Janamat Party, 3.74
CPN (Unified Socialist), 2.83
Loktantrik Samajbadi Party, 1.58
Nagarik Unmukti Party, 2.57
Others, 5.22"""

user_input = st.text_area("Paste votes/percentages here:", default_data, height=300)

# --- CALCULATION LOGIC ---
def run_calculation(data_str):
    try:
        # Parse Input
        rows = [line.split(',') for line in data_str.strip().split('\n')]
        raw_data = {r[0].strip(): float(r[1].strip()) for r in rows}
        total_votes = sum(raw_data.values())
        
        # Apply Threshold
        eligible = {p: v for p, v in raw_data.items() if (v / total_votes) >= threshold_pct}
        excluded = {p: v for p, v in raw_data.items() if (v / total_votes) < threshold_pct}
        
        # Sainte-Laguë Loop
        seats = {p: 0 for p in eligible}
        for _ in range(total_seats):
            best_q = -1
            winner = None
            for p, v in eligible.items():
                # Standard: 1, 3, 5... | Modified: 1.4, 3, 5...
                if seats[p] == 0 and use_modified:
                    divisor = 1.4
                else:
                    divisor = 2 * seats[p] + 1
                
                q = v / divisor
                if q > best_q:
                    best_q = q
                    winner = p
            if winner: seats[winner] += 1
            
        return seats, excluded, raw_data
    except Exception as e:
        st.error(f"Error in data format: {e}")
        return {}, {}, {}

# --- DISPLAY RESULTS ---
seats_won, excluded_parties, raw_data = run_calculation(user_input)

if seats_won:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Seat Distribution")
        df = pd.DataFrame(list(seats_won.items()), columns=["Party", "Seats"]).sort_values("Seats", ascending=False)
        st.table(df)
        
    with col2:
        st.subheader("Visual Analysis")
        fig = px.pie(df, values='Seats', names='Party', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Threshold Details")
    if excluded_parties:
        st.warning(f"The following parties did not meet the {threshold_pct*100}% threshold and received 0 seats:")
        for p, v in excluded_parties.items():
            st.write(f"- **{p}**: {(v/sum(raw_data.values()))*100:.2f}%")
