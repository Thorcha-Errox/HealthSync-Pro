import streamlit as st
import pandas as pd
import altair as alt
import time

# 1. PREMIUM PAGE CONFIGURATION ---
st.set_page_config(
    page_title="HealthSync Enterprise",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CUSTOM CSS  ---
st.markdown("""
    <style>
        
        /* Sidebar padding control */
        section[data-testid="stSidebar"] > div {
            padding-bottom: 0.5rem !important;
        }

        /* Widget spacing */
        div[data-testid="stVerticalBlock"] {
            gap: 0.6rem !important;
        }

        /* Compact multiselect */
        div[data-baseweb="select"] {
            min-height: 36px !important;
        }
            
        /* Compact chips */
        span[data-baseweb="tag"] {
            padding: 3px 8px !important;
            font-size: 0.8rem !important;
        }

        /* Divider spacing */
        hr {
            margin: 0.6rem 0 !important;
        }


        .block-container {padding-top: 1rem; padding-bottom: 2rem;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Metric Value Text Size */
        [data-testid="stMetricValue"] {font-size: 1.8rem !important;}
        
        /* Card Styling: Uses Streamlit's theme variables */
        div[data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
            border: 1px solid rgba(128, 128, 128, 0.2);
            border-radius: 10px;
            padding: 15px;
            background-color: var(--secondary-background-color); /* Adapts to Dark Mode automatically */
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# 3. CONNECTION & DATA LOADING ---
@st.cache_data(ttl=600) 
def load_data():
    try:
        conn = st.connection("snowflake")
        df = conn.query("SELECT * FROM HEALTH_INVENTORY_DB.PUBLIC.INVENTORY_HEALTH_METRICS", ttl=0)
        return df
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return pd.DataFrame() 
df_raw = load_data()

if df_raw.empty:
    st.warning("No data found or connection failed. Please check your Snowflake credentials.")
    st.stop()

# 4. SIDEBAR (FILTERS) ---
with st.sidebar:
    st.header("HealthSync")
    st.caption("Inventory Intelligence System")
    st.markdown("---")
    
    # 1. Location Filter
    locations = sorted(df_raw['LOCATION_ID'].unique())
    selected_loc = st.multiselect("Location", locations, default=locations)
    
    # 2. Status Filter
    statuses = sorted(df_raw['STATUS'].unique())
    selected_status = st.multiselect("Stock Status", statuses, default=statuses)

    st.markdown("---")
    st.caption("System Status: Online")
    if st.button("Refresh Data", type="secondary"):
        st.cache_data.clear()
        st.rerun()

# Apply Filters
df = df_raw[
    (df_raw['LOCATION_ID'].isin(selected_loc)) & 
    (df_raw['STATUS'].isin(selected_status))
]

# 5. DASHBOARD HEADER & KPI CARDS ---
st.title("Inventory Command Center")
st.markdown("Real-time visibility into supply chain operations.")

col1, col2, col3, col4 = st.columns(4)

total_locations = df['LOCATION_ID'].nunique()
total_skus = len(df)
critical_count = len(df[df['STATUS'].str.contains('CRITICAL')])
warning_count = len(df[df['STATUS'].str.contains('WARNING')])
low_stock_pct = round(((critical_count + warning_count) / total_skus) * 100, 1) if total_skus > 0 else 0

with col1:
    st.metric(label="Active Locations", value=total_locations, help="Total facilities handled by inventory")
with col2:
    st.metric(label="Total SKUs Monitored", value=total_skus)
with col3:
    st.metric(label="Critical Stockouts", value=critical_count, delta="-Urgent" if critical_count > 0 else "Stable", delta_color="inverse")
with col4:
    st.metric(label="Approaching Low", value=warning_count, delta="Monitor", delta_color="off")

st.markdown("---")

# 6. MAIN ANALYTICS TABS ---
tab1, tab2, tab3 = st.tabs(["Overview & Heatmap", "Risk Analysis", "Procurement Desk"])

# TAB 1: VISUAL OVERVIEW ===
with tab1:
    st.subheader("Network Stock Distribution")
    
    if not df.empty:
        heatmap = alt.Chart(df).mark_rect(stroke='gray', strokeWidth=0.5).encode(
            x=alt.X('LOCATION_ID', title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('ITEM_NAME', title=None),
            color=alt.Color('DAYS_REMAINING', 
                            scale=alt.Scale(scheme='redyellowgreen', domain=[0, 45]), 
                            legend=alt.Legend(title="Days of Cover", orient="top")),
            tooltip=['LOCATION_ID', 'ITEM_NAME', 'CURRENT_STOCK', 'STATUS']
        ).properties(
            height=400,
            width='container'
        ).configure_axis(
            grid=False,
            domain=False
        ).configure_view(
            strokeWidth=0
        )
        st.altair_chart(heatmap, use_container_width=True)
    else:
        st.info("Select filters to view data.")

# TAB 2: ANALYTICS ===
with tab2:
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown("##### Stock Coverage by Item (Top Risks)")
        risk_df = df.sort_values('DAYS_REMAINING').head(10)
        
        bars = alt.Chart(risk_df).mark_bar(cornerRadius=3).encode(
            x=alt.X('DAYS_REMAINING', title='Days Remaining'),
            y=alt.Y('ITEM_NAME', sort='x', title=None),
            color=alt.Color('STATUS', scale=alt.Scale(domain=['CRITICAL (Stockout Risk)', 'WARNING (Reorder Soon)', 'GOOD'], range=['#D32F2F', '#F57C00', '#388E3C']), legend=None),
            tooltip=['LOCATION_ID', 'CURRENT_STOCK', 'AVG_DAILY_USAGE']
        ).properties(height=350)
        
        text = bars.mark_text(
            align='left',
            baseline='middle',
            dx=3 
        ).encode(
            text='DAYS_REMAINING'
        )
        
        st.altair_chart(bars + text, use_container_width=True)

    with c2:
        st.markdown("##### Alert Distribution")
        donut = alt.Chart(df).mark_arc(innerRadius=50).encode(
            theta=alt.Theta("count()", stack=True),
            color=alt.Color("STATUS", legend=alt.Legend(orient="bottom", columns=1)),
            tooltip=["STATUS", "count()"]
        ).properties(height=350)
        st.altair_chart(donut, use_container_width=True)

# TAB 3: ACTION DESK (SaaS Style Table) ===
with tab3:
    col_header, col_btn = st.columns([4, 1])
    with col_header:
        st.subheader("Procurement Reorder List")
    with col_btn:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export CSV", data=csv, file_name="procurement_list.csv", mime="text/csv", type="primary")

    action_df = df[df['STATUS'] != 'GOOD'][['LOCATION_ID', 'ITEM_NAME', 'CURRENT_STOCK', 'DAYS_REMAINING', 'SUGGESTED_REORDER_QTY', 'STATUS']]
    
    if not action_df.empty:
        st.dataframe(
            action_df,
            column_config={
                "LOCATION_ID": st.column_config.TextColumn("Location"),
                "ITEM_NAME": st.column_config.TextColumn("Item Name", width="medium"),
                "CURRENT_STOCK": st.column_config.ProgressColumn(
                    "Current Stock",
                    help="Visual indicator of stock volume",
                    format="%d",
                    min_value=0,
                    max_value=1000, 
                ),
                "DAYS_REMAINING": st.column_config.NumberColumn(
                    "Days Left",
                    format="%.1f days"
                ),
                "SUGGESTED_REORDER_QTY": st.column_config.NumberColumn(
                    "Reorder Qty",
                    help="Recommended purchase amount",
                    format="%d units"
                ),
                "STATUS": st.column_config.TextColumn("Risk Level"),
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.success("All inventory levels are healthy. No immediate actions required.")