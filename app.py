import streamlit as st
import pandas as pd
import sys
import os
import traceback

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Modules.classifier import classify_component
from Modules.feeder_optimizer import feeder_summary
from Modules.cost_calculator import calculate_cost
from Modules.report_generator import generate_report
from Modules.parser import normalize_bom
from Modules.database_manager import init_db, save_component, load_database, delete_component

# ---------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------
st.set_page_config(
    page_title="Factory-Quant | SMT Resource Planner",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# INITIALIZE DATABASE
# ---------------------------------------------------
init_db()

# ---------------------------------------------------
# CUSTOM CSS - MODERN AESTHETIC DESIGN
# ---------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:400,500,600,700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main > div {
        padding: 2rem 2rem 2rem 2rem;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
        border-right: 1px solid rgba(37, 99, 235, 0.2);
    }
    
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        background: linear-gradient(135deg, #60A5FA 0%, #A78BFA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(37, 99, 235, 0.3);
    }
    
    [data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(37, 99, 235, 0.2);
        border-radius: 16px;
        padding: 1rem;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-weight: 700;
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .status-success {
        background: rgba(16, 185, 129, 0.2);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .status-warning {
        background: rgba(245, 158, 11, 0.2);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .status-danger {
        background: rgba(239, 68, 68, 0.2);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .total-cost-box {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 2px solid #10B981;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .total-cost-label {
        font-size: 0.9rem;
        color: #94A3B8;
        font-weight: 500;
        text-transform: uppercase;
    }
    
    .total-cost-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #10B981;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# TITLE SECTION
# ---------------------------------------------------
col_title1, col_title2, col_title3 = st.columns([1, 2, 1])
with col_title2:
    st.markdown("# 🏭 Factory-Quant")
    st.markdown("#### *Automated SMT Resource & Cost Planner*")
    st.markdown("---")

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------
if 'all_results' not in st.session_state:
    st.session_state.all_results = {}
if 'comparison_mode' not in st.session_state:
    st.session_state.comparison_mode = False
if 'processed_file_names' not in st.session_state:
    st.session_state.processed_file_names = set()
if 'last_config' not in st.session_state:
    st.session_state.last_config = {}
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False
if 'clear_files' not in st.session_state:
    st.session_state.clear_files = False
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

# ---------------------------------------------------
# SIDEBAR CONFIGURATION
# ---------------------------------------------------
st.sidebar.markdown("## ⚙️ Factory Configuration")
st.sidebar.markdown("---")

hourly_rate = st.sidebar.number_input("💰 Hourly Line Rate (₹/hour)", value=2500, step=100)
production_volume = st.sidebar.number_input("📊 Production Volume", value=1, min_value=1, step=50)
efficiency_percentage = st.sidebar.slider("⚡ Line Efficiency (%)", min_value=50, max_value=100, value=85)
efficiency_factor = efficiency_percentage / 100.0
setup_cost = st.sidebar.number_input("🔧 Setup Cost (₹)", value=2000, step=100)
overhead_per_hour = st.sidebar.number_input("🏭 Overhead Cost (₹/hour)", value=500, step=50)
machine_capacity = st.sidebar.number_input("🎛️ Machine Feeder Capacity (Slots)", value=50, step=1)

st.sidebar.markdown("---")
st.sidebar.caption("💡 *Configure your factory parameters above*")

st.session_state.debug_mode = st.sidebar.checkbox("🐛 Debug Mode", value=st.session_state.debug_mode)

current_config = {
    'hourly_rate': hourly_rate,
    'production_volume': production_volume,
    'efficiency_factor': efficiency_factor,
    'efficiency_percentage': efficiency_percentage,
    'setup_cost': setup_cost,
    'overhead_per_hour': overhead_per_hour,
    'machine_capacity': machine_capacity
}

# ---------------------------------------------------
# RECALCULATE COSTS
# ---------------------------------------------------
def recalculate_all_costs():
    if st.session_state.all_results:
        for file_name, result_data in st.session_state.all_results.items():
            opt_savings = 0
            if 'feeder_recommendations' in result_data['summary']:
                opt_savings = result_data['summary']['feeder_recommendations']['optimization_summary'].get('estimated_time_savings_seconds', 0)
            
            new_cost_result = calculate_cost(
                total_placement_time_seconds=result_data['summary']["total_placement_time"],
                production_volume=production_volume,
                hourly_rate=hourly_rate,
                setup_cost=setup_cost,
                overhead_per_hour=overhead_per_hour,
                efficiency=efficiency_factor,
                optimized_time_savings=opt_savings
            )
            
            st.session_state.all_results[file_name]['cost_result'] = new_cost_result
            st.session_state.all_results[file_name]['cost_per_board'] = new_cost_result['cost_per_board']
            st.session_state.all_results[file_name]['total_cost'] = new_cost_result['total_cost']

if st.session_state.last_config != current_config:
    recalculate_all_costs()
    st.session_state.last_config = current_config

# ---------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------
col_upload1, col_upload2, col_upload3 = st.columns([1, 2, 1])
with col_upload2:
    uploaded_files = st.file_uploader(
        "📁 Upload BOM Files (Multiple files allowed)",
        type=["csv", "xlsx"],
        accept_multiple_files=True,
        key=f"bom_uploader_{st.session_state.uploader_key}",
        help="Supported formats: CSV, XLSX"
    )
    st.caption("Supported formats: CSV, XLSX | Upload multiple files to compare different BOMs")
    
    if st.session_state.all_results:
        st.markdown("---")
        st.markdown("**📄 Currently Loaded BOMs:**")
        file_list = list(st.session_state.all_results.keys())
        cols = st.columns(min(len(file_list), 3))
        
        for idx, file_name in enumerate(file_list):
            col_idx = idx % 3
            result = st.session_state.all_results[file_name]
            with cols[col_idx]:
                st.markdown(f"""
                <div style='background: rgba(30,41,59,0.5); border-radius: 8px; padding: 8px; margin: 4px;'>
                    <small>📄 {file_name[:25]}...</small><br>
                    <small>{result['total_components']} comps | ₹{result['cost_per_board']}/board</small>
                </div>
                """, unsafe_allow_html=True)
        
        col_clear1, col_clear2, col_clear3 = st.columns([1, 2, 1])
        with col_clear2:
            if st.button("🗑️ Clear All BOMs", use_container_width=True, key="clear_all_btn"):
                st.session_state.all_results = {}
                st.session_state.processed_file_names = set()
                st.session_state.uploader_key += 1
                st.session_state.clear_files = True
                st.rerun()

if st.session_state.clear_files:
    st.session_state.clear_files = False
    st.session_state.all_results = {}
    st.session_state.processed_file_names = set()
    st.rerun()

# ---------------------------------------------------
# PROCESS FILES
# ---------------------------------------------------
if uploaded_files is not None and len(uploaded_files) > 0:
    current_file_names = {file.name for file in uploaded_files}
    
    if current_file_names != st.session_state.processed_file_names:
        st.session_state.all_results = {}
        st.session_state.processed_file_names = current_file_names
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing {uploaded_file.name}... ({idx + 1}/{len(uploaded_files)})")
            
            try:
                if uploaded_file.name.endswith(".csv"):
                    raw_df = pd.read_csv(uploaded_file)
                else:
                    raw_df = pd.read_excel(uploaded_file)
                
                if st.session_state.debug_mode:
                    st.write(f"📄 Debug: Raw file '{uploaded_file.name}' loaded with {len(raw_df)} rows")
                    st.write(f"📄 Debug: Columns found: {list(raw_df.columns)}")
                    st.dataframe(raw_df.head(3))
                    st.write("---")
                
                df = normalize_bom(raw_df)
                
                if st.session_state.debug_mode:
                    st.write(f"✅ Debug: Normalized BOM has {len(df)} rows")
                    st.write(f"✅ Debug: Columns: {list(df.columns)}")
                    st.dataframe(df.head(5))
                    st.write("---")
                
                if len(df) == 0:
                    st.error(f"❌ No valid rows found in {uploaded_file.name}!")
                    continue
                
                classification_results = df.apply(classify_component, axis=1)
                df["Component_Type"] = classification_results.apply(lambda x: x["Component_Type"])
                df["Feeder"] = classification_results.apply(lambda x: x["Feeder"])
                df["Placement_Time"] = classification_results.apply(lambda x: x["Placement_Time"])
                
                if st.session_state.debug_mode:
                    st.write(f"✅ Debug: Classification complete for {len(df)} components")
                    st.write(f"📊 Debug: Component types: {df['Component_Type'].value_counts().to_dict()}")
                    st.write("---")
                
                summary = feeder_summary(df)
                
                if st.session_state.debug_mode:
                    st.write(f"✅ Debug: Feeder summary complete")
                    st.write(f"📊 Debug: Total components: {summary['total_components']}")
                    st.write(f"📊 Debug: Total placement time: {summary['total_placement_time']:.2f} seconds")
                    st.write(f"📊 Debug: Feeder counts: {summary['feeder_counts']}")
                    st.write("---")
                
                opt_savings = 0
                if 'feeder_recommendations' in summary:
                    opt_savings = summary['feeder_recommendations']['optimization_summary'].get('estimated_time_savings_seconds', 0)
                    if st.session_state.debug_mode:
                        st.write(f"📊 Debug: Optimization savings: {opt_savings:.2f} seconds")
                        st.write("---")
                
                cost_result = calculate_cost(
                    total_placement_time_seconds=summary["total_placement_time"],
                    production_volume=production_volume,
                    hourly_rate=hourly_rate,
                    setup_cost=setup_cost,
                    overhead_per_hour=overhead_per_hour,
                    efficiency=efficiency_factor,
                    optimized_time_savings=opt_savings
                )
                
                if st.session_state.debug_mode:
                    st.write(f"✅ Debug: Cost calculation complete")
                    st.write(f"💰 Debug: Total cost: ₹{cost_result['total_cost']:,.2f}")
                    st.write(f"💰 Debug: Cost per board: ₹{cost_result['cost_per_board']:,.2f}")
                    st.write("---")
                
                st.session_state.all_results[uploaded_file.name] = {
                    'df': df,
                    'summary': summary,
                    'cost_result': cost_result,
                    'total_slots': sum(summary['feeder_counts'].values()),
                    'total_components': summary['total_components'],
                    'placement_time': round(summary['total_placement_time'], 2),
                    'cost_per_board': cost_result['cost_per_board'],
                    'total_cost': cost_result['total_cost']
                }
                
                st.success(f"✅ Successfully processed {uploaded_file.name}")
                
            except Exception as e:
                st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                if st.session_state.debug_mode:
                    st.code(traceback.format_exc())
            
            progress_bar.progress((idx + 1) / len(uploaded_files))
        
        status_text.text("✅ All files processed successfully!")
        progress_bar.empty()
        
        if not st.session_state.debug_mode:
            st.rerun()
        else:
            st.info("🔍 Debug mode is ON. Debug information shown above.")

elif (uploaded_files is None or len(uploaded_files) == 0) and st.session_state.all_results:
    st.session_state.all_results = {}
    st.session_state.processed_file_names = set()
    st.rerun()

# ---------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------
def display_detailed_calculation(result, production_volume, hourly_rate, overhead_per_hour, setup_cost, efficiency_percentage, efficiency_factor):
    ideal_time = result['summary']["total_placement_time"]
    actual_time = result['cost_result'].get('time_per_board_seconds', ideal_time / efficiency_factor)
    total_time_hours = result['cost_result'].get('total_production_hours', (actual_time * production_volume) / 3600)
    
    labor_cost = result['cost_result']['labor_cost']
    overhead_cost = result['cost_result']['overhead_cost']
    setup_cost_value = result['cost_result']['setup_cost']
    total_cost = result['cost_result']['total_cost']
    cost_per_board = result['cost_result']['cost_per_board']
    
    st.subheader("📊 Time Analysis")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Ideal Placement Time", f"{ideal_time:.2f} sec")
    with col2:
        st.metric(f"Actual Time ({efficiency_percentage}% eff)", f"{actual_time:.2f} sec")
    with col3:
        if total_time_hours >= 1:
            st.metric("Total Production Time", f"{total_time_hours:.2f} hours")
        else:
            st.metric("Total Production Time", f"{total_time_hours * 60:.1f} minutes")
    
    st.subheader("💰 Cost Breakdown")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏭 Labor Cost", f"₹ {labor_cost:,.2f}", f"{total_time_hours:.4f} hrs @ ₹{hourly_rate}/hr")
    with col2:
        st.metric("⚡ Overhead Cost", f"₹ {overhead_cost:,.2f}", f"{total_time_hours:.4f} hrs @ ₹{overhead_per_hour}/hr")
    with col3:
        st.metric("🔧 Setup Cost", f"₹ {setup_cost_value:,.2f}", "one-time")
    with col4:
        st.metric("🎯 Cost Per Board", f"₹ {cost_per_board:,.2f}", f"Total: ₹{total_cost:,.2f}")
    
    labor_pct = (labor_cost / total_cost) * 100 if total_cost > 0 else 0
    overhead_pct = (overhead_cost / total_cost) * 100 if total_cost > 0 else 0
    setup_pct = (setup_cost_value / total_cost) * 100 if total_cost > 0 else 0
    
    st.caption(f"📊 Cost Breakdown: Labor {labor_pct:.1f}% | Overhead {overhead_pct:.1f}% | Setup {setup_pct:.1f}%")
    st.progress(labor_pct / 100 if labor_pct > 0 else 0)
    
    with st.expander("📊 View Detailed Cost Calculation", expanded=False):
        st.markdown(f"""
        | Parameter | Value | Calculation |
        |-----------|-------|-------------|
        | **Time Calculations** | | |
        | Ideal Placement Time | {ideal_time:.2f} sec | Sum of all component placement times |
        | Efficiency | {efficiency_percentage}% | User setting |
        | Actual Time per Board | {actual_time:.2f} sec | {ideal_time:.2f} ÷ {efficiency_factor:.2f} |
        | Total Time for Batch | {total_time_hours:.4f} hours | {actual_time:.2f} sec × {production_volume} ÷ 3600 |
        | | | |
        | **Cost Calculations** | | |
        | Labor Cost | ₹{labor_cost:,.2f} | {total_time_hours:.4f} hrs × ₹{hourly_rate}/hr |
        | Overhead Cost | ₹{overhead_cost:,.2f} | {total_time_hours:.4f} hrs × ₹{overhead_per_hour}/hr |
        | Setup Cost | ₹{setup_cost_value:,.2f} | Fixed one-time cost |
        | **Total Batch Cost** | **₹{total_cost:,.2f}** | Labor + Overhead + Setup |
        | **Cost Per Board** | **₹{cost_per_board:,.2f}** | Total ÷ {production_volume} |
        """)
        
        st.code("""
Formula Used:

Actual Time = Ideal Time ÷ Efficiency
Total Hours = (Actual Time × Production Volume) ÷ 3600
Labor Cost = Total Hours × Hourly Rate
Overhead Cost = Total Hours × Overhead Rate
Total Cost = Labor + Overhead + Setup
Cost Per Board = Total Cost ÷ Production Volume
        """)

def display_feeder_optimization(result, machine_capacity, production_volume):
    if 'feeder_recommendations' not in result['summary']:
        return
    
    recommendations = result['summary']['feeder_recommendations']
    opt_summary = recommendations['optimization_summary']
    
    st.subheader("🎯 Feeder Optimization Recommendations")
    st.info(f"📊 **Optimization Insight:** {opt_summary['optimization_message']}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Unique Parts", opt_summary['total_unique_parts'])
    with col2:
        st.metric("High Volume (>80%)", opt_summary['high_volume_parts_count'], delta="Place in CENTER", delta_color="inverse")
    with col3:
        st.metric("Medium Volume", opt_summary['medium_volume_parts_count'], delta="Place in MIDDLE")
    with col4:
        st.metric("Low Volume", opt_summary['low_volume_parts_count'], delta="Place on EDGE")
    
    if opt_summary['estimated_time_savings_seconds'] > 0:
        time_saved = opt_summary['estimated_time_savings_seconds']
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"⏱️ **Time Savings:** {time_saved:.2f} seconds per board")
    
    with st.expander("📋 Detailed Feeder Placement Plan", expanded=False):
        if recommendations['center_feeder_positions']:
            st.markdown("### 🔴 CENTER ZONE (High Speed Zone)")
            center_df = pd.DataFrame(recommendations['center_feeder_positions'])
            display_cols = ['part_number', 'quantity', 'quantity_percentage', 'feeder_width', 'component_type']
            available_cols = [col for col in display_cols if col in center_df.columns]
            center_df = center_df[available_cols]
            center_df.columns = ['Part Number', 'Quantity', '% of Total', 'Feeder Width', 'Type']
            st.dataframe(center_df, hide_index=True, use_container_width=True)
        
        if recommendations['edge_feeder_positions']:
            st.markdown("### 🟢 EDGE ZONE (Lower Priority Zone)")
            edge_df = pd.DataFrame(recommendations['edge_feeder_positions'])
            available_cols = [col for col in display_cols if col in edge_df.columns]
            edge_df = edge_df[available_cols]
            edge_df.columns = ['Part Number', 'Quantity', '% of Total', 'Feeder Width', 'Type']
            st.dataframe(edge_df, hide_index=True, use_container_width=True)

# ---------------------------------------------------
# DISPLAY RESULTS
# ---------------------------------------------------
if st.session_state.all_results:
    if len(st.session_state.all_results) == 1:
        file_name = list(st.session_state.all_results.keys())[0]
        result = st.session_state.all_results[file_name]
        
        st.success(f"✅ BOM '{file_name}' Uploaded and Processed Successfully!")
        
        with st.expander("📋 View Processed BOM", expanded=False):
            st.dataframe(result['df'], use_container_width=True)
        
        st.subheader("📊 Feeder Requirements")
        feeder_df = pd.DataFrame(list(result['summary']["feeder_counts"].items()), columns=["Feeder Width", "Quantity Required"])
        st.dataframe(feeder_df, hide_index=True, use_container_width=True)
        
        total_slots = result['total_slots']
        if total_slots > machine_capacity:
            st.markdown(f'<div class="status-badge status-danger">⚠️ WARNING</div><p>Requires {total_slots} feeders, exceeds capacity of {machine_capacity}.</p>', unsafe_allow_html=True)
        elif total_slots > machine_capacity * 0.9:
            st.markdown(f'<div class="status-badge status-warning">⚠️ CAUTION</div><p>Feeder capacity nearly full ({total_slots}/{machine_capacity})</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-badge status-success">✅ CAPACITY OK</div><p>Feeder capacity OK ({total_slots}/{machine_capacity})</p>', unsafe_allow_html=True)
        
        display_feeder_optimization(result, machine_capacity, production_volume)
        display_detailed_calculation(result, production_volume, hourly_rate, overhead_per_hour, setup_cost, efficiency_percentage, efficiency_factor)
        
        st.markdown(f"""
        <div class="total-cost-box">
            <div class="total-cost-label">TOTAL BATCH COST</div>
            <div class="total-cost-value">₹ {result['cost_result']['total_cost']:,.2f}</div>
            <div class="total-cost-desc">For {production_volume} boards</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        col_report1, col_report2, col_report3 = st.columns([1, 2, 1])
        with col_report2:
            report_file = generate_report(
                result['summary'], result['cost_result'], production_volume, efficiency_percentage,
                machine_capacity, overhead_per_hour, hourly_rate, setup_cost,
                file_name.replace('.csv', '').replace('.xlsx', '')
            )
            with open(report_file, "rb") as pdf_file:
                st.download_button("📥 Download SMT Report PDF", data=pdf_file, file_name=f"SMT_Report_{file_name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf", mime="application/pdf", use_container_width=True)
    
    else:
        st.subheader("📊 BOM Comparison Dashboard")
        st.markdown(f"**Comparing {len(st.session_state.all_results)} BOM files**")
        
        comparison_data = []
        for name, result in st.session_state.all_results.items():
            comparison_data.append({
                "BOM File": name,
                "Components": result['total_components'],
                "Ideal Time": f"{result['placement_time']} sec",
                "Feeder Slots": result['total_slots'],
                "Cost/Board": f"₹{result['cost_per_board']:,.2f}",
                "Status": "⚠️" if result['total_slots'] > machine_capacity else "✅"
            })
        st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)
        
        st.subheader("📊 Cost Per Board Comparison")
        cost_chart_data = pd.DataFrame([{"BOM": name, "Cost Per Board (₹)": result['cost_per_board']} for name, result in st.session_state.all_results.items()])
        st.bar_chart(cost_chart_data.set_index("BOM"))
        
        st.subheader("🔍 Detailed BOM Viewer")
        tab_names = list(st.session_state.all_results.keys())
        tabs = st.tabs(tab_names)
        
        for tab, (file_name, result) in zip(tabs, st.session_state.all_results.items()):
            with tab:
                with st.expander("📋 View Processed BOM Table", expanded=False):
                    st.dataframe(result['df'], use_container_width=True)
                
                st.write("**Feeder Requirements:**")
                feeder_df = pd.DataFrame(list(result['summary']["feeder_counts"].items()), columns=["Feeder Width", "Quantity Required"])
                st.dataframe(feeder_df, hide_index=True, use_container_width=True)
                
                if result['total_slots'] > machine_capacity:
                    st.markdown(f'<div class="status-badge status-danger">⚠️ WARNING</div><p>Exceeds capacity ({result["total_slots"]}/{machine_capacity})</p>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="status-badge status-success">✅ CAPACITY OK</div><p>{result["total_slots"]}/{machine_capacity} slots used</p>', unsafe_allow_html=True)
                
                display_feeder_optimization(result, machine_capacity, production_volume)
                display_detailed_calculation(result, production_volume, hourly_rate, overhead_per_hour, setup_cost, efficiency_percentage, efficiency_factor)
                
                st.markdown(f"""
                <div class="total-cost-box">
                    <div class="total-cost-label">TOTAL BATCH COST</div>
                    <div class="total-cost-value">₹ {result['cost_result']['total_cost']:,.2f}</div>
                    <div class="total-cost-desc">For {production_volume} boards</div>
                </div>
                """, unsafe_allow_html=True)
                
                report_file = generate_report(
                    result['summary'], result['cost_result'], production_volume, efficiency_percentage,
                    machine_capacity, overhead_per_hour, hourly_rate, setup_cost,
                    file_name.replace('.csv', '').replace('.xlsx', '')
                )
                with open(report_file, "rb") as pdf_file:
                    st.download_button(f"📥 Download PDF Report", data=pdf_file, file_name=f"SMT_Report_{file_name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf", mime="application/pdf", use_container_width=True)
        
        if st.button("📥 Download All Reports as ZIP", use_container_width=True):
            import zipfile, io, os
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for name, result in st.session_state.all_results.items():
                    report_file = generate_report(
                        result['summary'], result['cost_result'], production_volume, efficiency_percentage,
                        machine_capacity, overhead_per_hour, hourly_rate, setup_cost,
                        name.replace('.csv', '').replace('.xlsx', '')
                    )
                    zip_file.write(report_file, f"SMT_Report_{name}.pdf")
                    os.remove(report_file)
            zip_buffer.seek(0)
            st.download_button("📦 Download All Reports (ZIP)", data=zip_buffer, file_name=f"SMT_Reports_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.zip", mime="application/zip", use_container_width=True)

# ---------------------------------------------------
# MASTER COMPONENT DATABASE UI
# ---------------------------------------------------
st.markdown("---")
st.header("🗄️ Master Component Database")
st.markdown("*Teach the software new components by their VALUE (e.g., '100K', '10K', '100ohm')*")

current_db = load_database()
tab1, tab2 = st.tabs(["➕ Add / Edit Component", "🗑️ Delete Component"])

with tab1:
    with st.form("add_component_form", clear_on_submit=True):
        st.info("💡 Add components by their VALUE as it appears in your BOM")
        col1, col2 = st.columns(2)
        with col1:
            component_value = st.text_input("📌 Component Value (from BOM)", placeholder="e.g., 100K, 10K, STM32F103")
            new_type = st.selectbox("🏷️ Component Type", ["Passive", "Discrete", "Standard IC", "Advanced IC", "Connector"])
        with col2:
            new_feeder = st.selectbox("📏 Feeder Width", ["8mm", "12mm", "16mm", "24mm", "32mm", "Tray", "Manual/Odd"])
            new_time = st.number_input("⏱️ Placement Time (seconds)", value=0.10, step=0.05, min_value=0.01)
            part_number_optional = st.text_input("📦 Manufacturer Part Number (Optional)")
        
        if st.form_submit_button("💾 Save to Database", use_container_width=True):
            if component_value:
                save_component(component_value, new_type, new_feeder, new_time, part_number_optional)
                st.success(f"✨ Component '{component_value}' saved!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Please enter a Component Value")

with tab2:
    if not current_db.empty:
        with st.form("delete_component_form"):
            component_to_delete = st.selectbox("🔍 Select Component to Delete", current_db["component_value"].tolist())
            if st.form_submit_button("🗑️ Delete from Database", use_container_width=True):
                delete_component(component_to_delete)
                st.warning(f"⚠️ Component '{component_to_delete}' removed!")
                st.rerun()
    else:
        st.info("📭 Database is empty.")

st.subheader("📚 Saved Components Library")
final_db = load_database()
if not final_db.empty:
    st.dataframe(final_db, use_container_width=True, column_config={
        "component_value": "Component Value",
        "component_type": "Type",
        "feeder": "Feeder Width",
        "placement_time": st.column_config.NumberColumn("Time (sec)", format="%.2f"),
        "part_number": "MPN"
    })
    st.caption(f"📊 Total: {len(final_db)} components")
else:
    st.info("📭 Database is empty. Add components above.")

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748B;'>🏭 Factory-Quant | Intelligent SMT Resource Planning</p>", unsafe_allow_html=True)
