import streamlit as st
import pandas as pd
from datetime import datetime
from config import (
    SEVERITY_LABELS, SLEEP_QUALITY_LABELS, STRESS_LEVEL_LABELS,
    BRISTOL_SCALE, MEAL_SPEED_OPTIONS, STRESS_TYPE_OPTIONS
)
from data_manager import DataManager
from ai_analysis import AIAnalyzer
from visualizations import Visualizer
from utils import (get_today_key, get_trigger_foods, convert_to_dataframe, 
                   get_csv_export, validate_entry)

# Initialize modules
# Use st.cache_resource for these if they were expensive to init, but they are lightweight
data_manager = DataManager()
ai_analyzer = AIAnalyzer()
visualizer = Visualizer()

st.set_page_config(page_title="IBS Wellness Tracker", page_icon="🧘", layout="wide")

def page_todays_log():
    st.header("📝 Today's Log")
    today_key = get_today_key()
    
    # Check for existing data
    existing_data = data_manager.get_entry(today_key)
    
    # BLOCK 1: Physical Symptoms
    st.subheader("1. 🩺 Physical Symptoms")
    with st.expander("Symptom Details", expanded=True):
        # Reactive Slider (No Form)
        severity = st.slider("Symptom Severity (1-10)", 1, 10, value=int(existing_data.get("symptom_severity", 1)), help="1=Minimal, 10=Unbearable")
        
        # Dynamic Label - Updates immediately on interaction
        sev_label = SEVERITY_LABELS.get(int(severity), "Unknown")
        if severity <= 3:
            st.success(f"Status: **{sev_label}**")
        elif severity <= 7:
            st.warning(f"Status: **{sev_label}**")
        else:
            st.error(f"Status: **{sev_label}**")
        
        symptoms = st.multiselect(
            "Specific Symptoms",
            ["Bloating", "Abdominal Pain", "Gas", "Constipation", "Diarrhea", 
                "Nausea", "Heartburn", "Incomplete Evacuation", "Urgency"],
            default=existing_data.get("symptoms", [])
        )

    # BLOCK 2: Bowel Health
    st.subheader("2. 🚽 Bowel Health")
    with st.expander("Stool Details", expanded=True):
        # Bristol Scale Dropdown
        bristol_opts = [f"{k} - {v}" for k,v in BRISTOL_SCALE.items()]
        current_stool = existing_data.get("stool_type", 3)
        try:
            default_idx = current_stool - 1
        except:
            default_idx = 2
        
        stool_type_raw = st.selectbox("Bristol Stool Type", options=bristol_opts, index=default_idx)
        stool_type = int(stool_type_raw.split(" - ")[0])
        
        bowel_movements = st.number_input("Bowel Movements Today", min_value=0, max_value=10, value=int(existing_data.get("bowel_movements", 1)))

    # BLOCK 3: Mental Well-being
    st.subheader("3. 🧠 Mental Well-being")
    with st.expander("Stress & Sleep", expanded=True):
        stress = st.slider("Stress Level (1-10)", 1, 10, value=int(existing_data.get("stress_level", 3)), help="1=Zen, 10=Panic")
        stress_label = STRESS_LEVEL_LABELS.get(int(stress), "Unknown")
        
        if stress <= 4:
            st.success(f"Status: **{stress_label}**")
        elif stress <= 7:
            st.warning(f"Status: **{stress_label}**")
        else:
            st.error(f"Status: **{stress_label}**")
        
        current_stress_type = existing_data.get("stress_type", "None")
        try:
            st_idx = STRESS_TYPE_OPTIONS.index(current_stress_type)
        except:
            st_idx = 0
        stress_type = st.selectbox("Stress Context", STRESS_TYPE_OPTIONS, index=st_idx)
        
        st.markdown("---")
        
        c_sleep1, c_sleep2 = st.columns(2)
        with c_sleep1:
            sleep_hours = st.number_input("Sleep Duration (Hours)", 0.0, 24.0, value=float(existing_data.get("sleep_hours", 7.0)), step=0.5)
        with c_sleep2:
            sleep_quality = st.slider("Sleep Quality (1-10)", 1, 10, value=int(existing_data.get("sleep_quality", 7)))
            sq_label = SLEEP_QUALITY_LABELS.get(int(sleep_quality), "Unknown")
            if sleep_quality >= 8:
                st.success(f"Status: **{sq_label}**")
            elif sleep_quality >= 5:
                st.warning(f"Status: **{sq_label}**")
            else:
                st.error(f"Status: **{sq_label}**")

    # BLOCK 4: Lifestyle & Diet
    st.subheader("4. 🥗 Lifestyle & Diet")
    with st.expander("Diet & Habits", expanded=True):
        diet_notes = st.text_area("Diet Notes (Meals, Triggers?)", 
                                value=existing_data.get("diet_notes", ""),
                                height=100)
        
        c_life1, c_life2 = st.columns(2)
        with c_life1:
            # Meal Speed
            current_speed = existing_data.get("meal_speed", MEAL_SPEED_OPTIONS[1])
            try:
                speed_idx = MEAL_SPEED_OPTIONS.index(current_speed)
            except:
                speed_idx = 1
            meal_speed = st.selectbox("Avg. Eating Speed", MEAL_SPEED_OPTIONS, index=speed_idx)
            
            ex_mins = existing_data.get("exercise", 0)
            exercise = st.checkbox("Did you exercise today?", value=ex_mins > 0)
            if exercise:
                exercise_mins = st.number_input("Duration (mins)", 10, 180, value=ex_mins if ex_mins > 0 else 30)
            else:
                exercise_mins = 0

        with c_life2:
            water_intake = st.number_input("Water Intake (Liters)", 0.0, 5.0, value=float(existing_data.get("water_intake", 2.0)), step=0.5)

    # Use regular button instead of form_submit_button
    if st.button("Save Entry", type="primary", use_container_width=True):
        entry_data = {
            "date": str(today_key),
            "symptom_severity": severity,
            "symptoms": symptoms,
            "stool_type": stool_type,
            "bowel_movements": bowel_movements,
            "stress_level": stress,
            "stress_type": stress_type,
            "sleep_hours": sleep_hours,
            "sleep_quality": sleep_quality,
            "diet_notes": diet_notes,
            "meal_speed": meal_speed,
            "water_intake": water_intake,
            "exercise": exercise_mins if exercise else 0,
            "timestamp": str(datetime.now())
        }
        
        if data_manager.save_entry(today_key, entry_data):
            st.success("✅ Daily log saved successfully!")
            st.balloons()
        else:
            st.error("❌ Failed to save entry. Check logs.")

def page_analytics():
    st.header("📊 Analytics")
    stats = data_manager.get_statistics()
    
    # Key Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Severity", stats.get("avg_severity", 0))
    c2.metric("Avg Sleep", f"{stats.get('avg_sleep', 0)}h")
    c3.metric("Avg Stress", stats.get("avg_stress", 0))
    
    # Load data for charts
    range_data = data_manager.get_date_range(8) # Last 8 days
    df = convert_to_dataframe(range_data)
    
    st.subheader("Interactive Trends")
    # New Plotly Charts
    with st.expander("Symptom Severity", expanded=True):
        st.plotly_chart(visualizer.create_symptom_chart(df), use_container_width=True)
        
    with st.expander("Sleep Patterns", expanded=True):
        st.plotly_chart(visualizer.create_sleep_chart(df), use_container_width=True)
        
    with st.expander("Stress Levels", expanded=True):
        st.plotly_chart(visualizer.create_stress_chart(df), use_container_width=True)
        
    st.subheader("🧩 Causal Analysis (Advanced)")
    
    # Get processed data with lags
    processed_df = data_manager.get_processed_data()
    
    if not processed_df.empty:
        # Lagged Correlation
        with st.expander("Symptom Drivers (Lag Analysis)", expanded=True):
            st.caption("Does yesterday's stress/sleep affect you today? (A positive lag correlation means Yes)")
            st.plotly_chart(visualizer.create_lagged_correlation_chart(processed_df), use_container_width=True)
            
        # Rolling Averages Context
        if 'severity_7d_avg' in processed_df.columns:
            recent_avg = processed_df['severity_7d_avg'].iloc[-1] if not processed_df['severity_7d_avg'].isna().all() else 0
            st.metric("7-Day Symptom Trend", f"{recent_avg:.1f}/10", 
                     delta=f"{recent_avg - stats.get('avg_severity', 0):.1f} vs All-time")
    
    st.subheader("Complex Analysis")
    with st.expander("Correlation Heatmap", expanded=True):
        st.caption("How do your lifestyle factors interact?")
        st.plotly_chart(visualizer.create_correlation_heatmap(df), use_container_width=True)
    
    # Trigger Analysis
    st.subheader("Potential Triggers")
    triggers = get_trigger_foods(range_data)
    if triggers:
        for date, meals in triggers.items():
            st.warning(f"**{date}** (High Severity): {meals}")
    else:
        st.info("No high symptom days recorded recently.")

def page_ai_analysis():
    st.header("🤖 Advanced AI Analysis")
    
    analysis_type = st.radio("Select Analysis Type", ["Daily", "Weekly"], horizontal=True)
    
    if st.button("Generate Insights", type="primary"):
        with st.spinner("Consulting AI Specialist..."):
            if analysis_type == "Daily":
                today_key = get_today_key()
                data = data_manager.get_entry(today_key)
                if not data:
                    st.warning("No data found for today. Please log data first.")
                else:
                    result = ai_analyzer.analyze_daily(data)
                    _display_ai_output(result, is_daily=True)
            else:
                data = data_manager.get_date_range(7)
                if not data:
                    st.warning("No data found for the last 7 days.")
                else:
                    result = ai_analyzer.analyze_weekly(data)
                    _display_ai_output(result, is_daily=False)

def _display_ai_output(result, is_daily=True):
    """Helper to display structured AI output."""
    if "error" in result:
        st.error(f"Analysis Failed: {result.get('message')}")
        with st.expander("Debug Info"):
            st.write(result)
        return

    # Display Wellness Score
    score = result.get("wellness_score", 0)
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.metric("Wellness Score", f"{score}/100", delta=None)
        st.progress(score / 100)
    
    with col2:
        if is_daily:
            st.subheader("Daily Summary")
            st.info(result.get("summary", "No summary provided."))
        else:
            st.subheader("Trend Analysis")
            st.info(result.get("trend_analysis", "No analysis provided."))

    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("🚨 Detected Triggers")
        triggers = result.get("triggers" if is_daily else "identified_triggers", [])
        if not triggers:
            st.success("No specific triggers identified yet.")
        else:
            for item in triggers:
                if isinstance(item, dict):
                    st.warning(f"**{item.get('trigger')}** (Confidence: {item.get('confidence')})")
                else:
                    st.warning(f"• {item}")

    with col_r:
        st.subheader("💡 Recommendations")
        recs = result.get("recommendations", [])
        for rec in recs:
            st.success(f"• {rec}")
            
    # Raw JSON fallback for debugging
    with st.expander("View Raw API Response"):
        st.json(result)

def page_history():
    st.header("📋 History")
    data = data_manager.load_data()
    
    if not data:
        st.info("No history available.")
        return

    # Download buttons
    c1, c2 = st.columns(2)
    csv_data = get_csv_export(data)
    c1.download_button("Download CSV", csv_data, "ibs_data.csv", "text/csv")
    
    import json
    json_data = json.dumps(data, indent=2)
    c2.download_button("Download JSON", json_data, "ibs_data.json", "application/json")
    
    # Display entries
    st.subheader("Log Entries")
    # Sort keys reverse chronologically
    for date in sorted(data.keys(), reverse=True):
        entry = data[date]
        with st.expander(f"{date} - Severity: {entry.get('symptom_severity')}"):
            st.json(entry)
            if st.button("Delete Entry", key=f"del_{date}"):
                if data_manager.delete_entry(date):
                    st.success("Entry deleted.")
                    st.rerun()

def main():
    st.sidebar.title("IBS Tracker 🧘")
    page = st.sidebar.radio("Navigation", ["Today's Log", "Analytics", "AI Analysis", "History"])
    
    if page == "Today's Log":
        page_todays_log()
    elif page == "Analytics":
        page_analytics()
    elif page == "AI Analysis":
        page_ai_analysis()
    elif page == "History":
        page_history()

if __name__ == "__main__":
    main()
