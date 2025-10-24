import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime
from rag_pipeline import load_full_data, main

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Argo Float Dashboard", page_icon="🌊")


mode = st.sidebar.radio("Select Mode:", ["ChatBot", "Dashboard"])
if mode == "ChatBot":
    st.title("HEXAWAVE — ChatBot+RAG (ARGO)")

    query = st.text_input("Ask a question about ARGO profiles (e.g., 'Show me salinity profiles near the bay of bangal in Febuary 2025')")

    if st.button("Run"):
        if not query.strip():
            st.error("Enter a question.")
        else:
            with st.spinner("Running retrieval + LLM → SQL → DB..."):
                try:
                    df,ca_output = main(query)
                    # st.write("DEBUG sample row:", df.iloc[0].to_dict())

                except Exception as e:
                    st.error(f"Error: {e}")
                    st.stop()
            st.success(f"Returned {len(df)} rows")
            st.markdown(ca_output)
            if df.empty:
                st.info("No results.")
            else:
                st.dataframe(df.head(100))
                if "LATITUDE" in df.columns and "LONGITUDE" in df.columns:
                    fig_map = px.scatter_geo(
                        df, lat="LATITUDE", lon="LONGITUDE",
                        color="PLATFORM_NUMBER",
                        hover_name="PLATFORM_NUMBER",
                        title="🌍 Float Locations"
                    )
                    st.plotly_chart(fig_map, use_container_width=True)
                if {"PRES", "TEMP", "PSAL"}.issubset(df.columns):
                    
                    #temprature - pressure
                    try:
                        fig_ts = px.scatter(
                            df,
                            x="PRES",
                            y="TEMP",
                            color="PLATFORM_NUMBER",
                            title="🌡🧂 Temperature-Pressure (T-P) Diagram",
                            labels={"PRES": "Pressure (dbar)", "TEMP": "Temperature (°C)"},
                        )
                        st.plotly_chart(fig_ts, use_container_width=True)
                    except:
                        pass
                    col1, col2 = st.columns(2)
                    # 🌡 Temperature vs Depth
                    try:
                        with col1:
                            fig_temp = px.line(
                                df,
                                x="TEMP", y="PRES",
                                color="PLATFORM_NUMBER",
                                title="🌡 Temperature Profiles",
                                labels={"PRES": "Pressure (dbar)", "TEMP": "Temperature (°C)"}
                            )
                            fig_temp.update_yaxes(autorange="reversed")  # depth increases downward
                            st.plotly_chart(fig_temp, use_container_width=True)
                    except:
                        pass
                    # 🧂 Salinity vs Depth
                    try:
                        with col2:
                            fig_psal = px.line(
                                df,
                                x="PSAL", y="PRES",
                                color="PLATFORM_NUMBER",
                                title="🧂 Salinity Profiles",
                                labels={"PRES": "Pressure (dbar)", "PSAL": "Salinity"}
                            )
                            fig_psal.update_yaxes(autorange="reversed")
                            st.plotly_chart(fig_psal, use_container_width=True)
                    
                    except:
                        pass
                    # 🌡🧂 Temperature vs Salinity (T–S Diagram)
                    try:
                        fig_ts = px.scatter(
                            df,
                            x="PSAL",
                            y="TEMP",
                            color="PLATFORM_NUMBER",
                            title="🌡🧂 Temperature-Salinity (T-S) Diagram",
                            labels={"PSAL": "Salinity", "TEMP": "Temperature (°C)"},
                        )
                        st.plotly_chart(fig_ts, use_container_width=True)
                    except:
                        pass
                    
                    try:
                        fig_ts = px.box(
                            df,
                            y="TEMP",
                        )
                        st.plotly_chart(fig_ts, use_container_width=True)
                    except:
                        pass
                    # 🧂 Salinity over time
                    try:
                        fig_psal_time = px.line(
                            df,
                            x="PROFILE_DATE",
                            y="PSAL",
                            color="PLATFORM_NUMBER",
                            title="🧂 Salinity Variation Over Time",
                            labels={"PROFILE_DATE": "Date", "PSAL": "Salinity"},
                        )
                        st.plotly_chart(fig_psal_time, use_container_width=True)
                    except Exception:
                        pass

                    # 🌡 Temperature over time
                    try:
                        fig_temp_time = px.line(
                            df,
                            x="PROFILE_DATE",
                            y="TEMP",
                            color="PLATFORM_NUMBER",
                            title="🌡 Temperature Variation Over Time",
                            labels={"PROFILE_DATE": "Date", "TEMP": "Temperature (°C)"},
                        )
                        st.plotly_chart(fig_temp_time, use_container_width=True)
                    except Exception:
                        pass

                    # ⬇️ Pressure over time
                    try:
                        fig_pres_time = px.line(
                            df,
                            x="PROFILE_DATE",
                            y="PRES",
                            color="PLATFORM_NUMBER",
                            title="⬇️ Pressure Variation Over Time",
                            labels={"PROFILE_DATE": "Date", "PRES": "Pressure (dbar)"},
                        )
                        st.plotly_chart(fig_pres_time, use_container_width=True)
                    except Exception:
                        pass
                    
                elif "PSAL" in df.columns: 
                    try:
                        fig_psal_time = px.line(
                            df,
                            x="PROFILE_DATE",
                            y="PSAL",
                            color="PLATFORM_NUMBER",
                            title="🧂 Salinity Variation Over Time",
                            labels={"PROFILE_DATE": "Date", "PSAL": "Salinity"},
                        )
                        st.plotly_chart(fig_psal_time, use_container_width=True)
                    except:
                        pass

                elif "TEMP" in df.columns:
                    try:
                        fig_temp_time = px.line(
                            df,
                            x="PROFILE_DATE",
                            y="TEMP",
                            color="PLATFORM_NUMBER",
                            title="🌡 Temperature Variation Over Time",
                            labels={"PROFILE_DATE": "Date", "TEMP": "Temperature (°C)"},
                        )
                        st.plotly_chart(fig_temp_time, use_container_width=True)
                    except:
                        pass

                elif "PRES" in df.columns:
                    try:
                        fig_pres_time = px.line(
                            df,
                            x="PROFILE_DATE",
                            y="PRES",
                            color="PLATFORM_NUMBER",
                            title="⬇️ Pressure Variation Over Time",
                            labels={"PROFILE_DATE": "Date", "PRES": "Pressure (dbar)"},
                        )
                        st.plotly_chart(fig_pres_time, use_container_width=True)
                    except:
                        pass
                else:
                    st.warning("No PRES/TEMP/PSAL columns found in result.")
elif mode == "Dashboard":
    @st.cache_data
    def generate_demo_data():
        """Generates a sample DataFrame mimicking Argo float data."""
        num_floats = 5
        records_per_float = 100
        base_date = datetime.datetime(2023, 1, 1)
        
        data = []
        for i in range(num_floats):
            platform_number = 10000 + i
            for j in range(records_per_float):
                date = base_date + datetime.timedelta(days=j, hours=np.random.randint(0, 24))
                lat = np.random.uniform(30, 60)
                lon = np.random.uniform(-40, -10)
                
                # Simulate data with some noise and trends
                base_temp = 10 + np.sin(j / 50) * 5
                temp = base_temp + np.random.randn() * 0.5
                
                base_psal = 35 + np.cos(j / 50) * 0.5
                psal = base_psal + np.random.randn() * 0.1
                
                pres = j * 10 + np.random.uniform(-50, 50)
                
                data.append({
                    "PLATFORM_NUMBER": platform_number,
                    "JULD": date,
                    "PROFILE_DATE": date.date(),
                    "LATITUDE": lat,
                    "LONGITUDE": lon,
                    "CYCLE_NUMBER": j + 1,
                    "TEMP": temp,
                    "PSAL": psal,
                    "PRES": max(0, pres), # Ensure pressure is not negative
                    "N_LEVELS": np.random.randint(50, 150),
                    "DATA_MODE": np.random.choice(['R', 'A', 'D']),
                    "TEMP_QC": np.random.choice([1, 2, 3, 4], p=[0.8, 0.1, 0.05, 0.05]),
                    "PSAL_QC": np.random.choice([1, 2, 3, 4], p=[0.8, 0.1, 0.05, 0.05]),
                    "PRES_QC": np.random.choice([1, 2, 3, 4], p=[0.9, 0.05, 0.03, 0.02]),
                })
                
        df = pd.DataFrame(data)
        df["JULD"] = pd.to_datetime(df["JULD"])
        return df

    # --- Custom CSS for Styling ---
    # This CSS enhances the visual appeal of KPI cards and the overall dashboard.
    st.markdown("""
        <style>
        /* General body styling */
        .stApp {
            background-color: #0E1117;
        }
        /* Style for KPI cards */
        .kpi-card {
            background: rgba(40, 40, 40, 0.6);
            border-radius: 15px;
            padding: 15px;
            text-align: center;
            color: white;
            border: 1px solid #2a2a2a;
            backdrop-filter: blur(5px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease-in-out;
        }
        .kpi-card:hover {
            transform: translateY(-5px);
        }
        .kpi-title {
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 10px;
            color: #a0a0a0;
        }
        .kpi-value {
            font-size: 36px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)


    # --- Dashboard Main Function ---
    def run_dashboard():
        """Main function to render the dashboard."""
        st.title("🌊 Modern Argo Float Dashboard")
        st.markdown("An interactive and redesigned interface for exploring oceanographic data.")

        # --- Load Data ---
        df = load_full_data()
        df  = generate_demo_data()

        # --- Sidebar Filters ---
        st.sidebar.header("🔬 Filters & Controls")
        
        # Multi-select for floats
        all_floats = sorted(df["PLATFORM_NUMBER"].unique())
        selected_floats = st.sidebar.multiselect(
            "Select Floats:", options=all_floats, default=all_floats
        )
        
        # Date range filter
        min_date = df["JULD"].min().date()
        max_date = df["JULD"].max().date()
        date_range = st.sidebar.date_input(
            "Select Date Range:", value=[min_date, max_date], min_value=min_date, max_value=max_date
        )

        # --- Filter Data Based on Selections ---
        if not selected_floats:
            st.warning("Please select at least one float.")
            st.stop()
            
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        
        mask = (
            df["PLATFORM_NUMBER"].isin(selected_floats) &
            (df["JULD"] >= start_date) &
            (df["JULD"] <= end_date)
        )
        filtered_df = df[mask].copy()

        if filtered_df.empty:
            st.error("No data available for the selected filters. Please adjust your selection.")
            st.stop()
            
        # --- KPI Section ---
        # st.markdown("###  ключевые показатели эффективности")
        k1, k2, k3, k4, k5 = st.columns(5)

        # with k1:
        #     st.markdown(f"""
        #     <div class="kpi-card">
        #         <div class="kpi-title">🛰️ Total Selected Floats</div>
        #         <div class="kpi-value">{filtered_df['PLATFORM_NUMBER'].nunique()}</div>
        #     </div>""", unsafe_allow_html=True)

        # with k2:
        #     st.markdown(f"""
        #     <div class="kpi-card">
        #         <div class="kpi-title">📑 Total Profiles</div>
        #         <div class="kpi-value">{len(filtered_df)}</div>
        #     </div>""", unsafe_allow_html=True)
            
        # with k3:
        #     avg_temp = round(filtered_df["TEMP"].mean(), 2)
        #     st.markdown(f"""
        #     <div class="kpi-card">
        #         <div class="kpi-title">🌡️ Avg Temp (°C)</div>
        #         <div class="kpi-value">{avg_temp}</div>
        #     </div>""", unsafe_allow_html=True)

        # with k4:
        #     avg_psal = round(filtered_df["PSAL"].mean(), 2)
        #     st.markdown(f"""
        #     <div class="kpi-card">
        #         <div class="kpi-title">🧂 Avg Salinity (PSU)</div>
        #         <div class="kpi-value">{avg_psal}</div>
        #     </div>""", unsafe_allow_html=True)
        # with k5:
        #     avg_pres = round(filtered_df["PRES"].mean(), 2)
        #     st.markdown(f"""
        #     <div class="kpi-card">
        #         <div class="kpi-title">🧂 Avg Pressure (PRES)</div>
        #         <div class="kpi-value">{avg_psal}</div>
        #     </div>""", unsafe_allow_html=True)
        with k1:
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #005f73, #0a9396);
                            border-radius: 15px; padding: 20px; text-align: center; color: white;">
                    <div style="font-size:16px">🛰️ Total Floats</div>
                    <div style="font-size:32px; font-weight:bold">{filtered_df['PLATFORM_NUMBER'].nunique()}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with k2:
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #0077be, #00c2d1);
                            border-radius: 15px; padding: 20px; text-align: center; color: white;">
                    <div style="font-size:16px">📑 Total Profiles</div>
                    <div style="font-size:32px; font-weight:bold">{len(filtered_df)}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with k3:
            avg_temp = round(filtered_df["TEMP"].mean(), 2) if "TEMP" in filtered_df.columns else "n/a"
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #ff6b6b, #ff9f43);
                            border-radius: 15px; padding: 20px; text-align: center; color: white;">
                    <div style="font-size:16px">🌡️ Avg Temp (°C)</div>
                    <div style="font-size:32px; font-weight:bold">{avg_temp}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with k4:
            avg_psal = round(filtered_df["PSAL"].mean(), 2) if "PSAL" in filtered_df.columns else "n/a"
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #ffd166, #06d6a0);
                            border-radius: 15px; padding: 20px; text-align: center; color: #222;">
                    <div style="font-size:16px">🧂 Avg Salinity (PSU)</div>
                    <div style="font-size:32px; font-weight:bold">{avg_psal}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with k5:
            avg_pres = round(filtered_df["PRES"].mean(), 2) if "PRES" in filtered_df.columns else "n/a"
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #8338ec, #3a0ca3);
                            border-radius: 15px; padding: 20px; text-align: center; color: white;">
                    <div style="font-size:16px">⬇️ Avg Pressure (dbar)</div>
                    <div style="font-size:32px; font-weight:bold">{avg_pres}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown("<hr>", unsafe_allow_html=True)

        # --- Main Content with Tabs ---
        tab1, tab2, tab3, tab4 = st.tabs([
            "🌎 **Geospatial View**", 
            "📈 **Parameter Trends**", 
            "📊 **Distributions**", 
            "🔬 **T-S Diagram & QC**"
        ])

        # --- Tab 1: Geospatial View ---
        with tab1:
            st.subheader("Float Locations and Profile Timeline")
            col1, col2 = st.columns([0.6, 0.4]) # Give more space to the map
            with col1:
                fig_map = px.scatter_geo(
                    filtered_df.groupby('PLATFORM_NUMBER').last().reset_index(),
                    lat="LATITUDE", lon="LONGITUDE", color="PLATFORM_NUMBER",
                    hover_name="PLATFORM_NUMBER", title="Latest Float Locations",
                    projection="natural earth"  
                )
                st.plotly_chart(fig_map, use_container_width=True)
            with col2:
                fig_time = px.scatter(
                    filtered_df, x="JULD", y="PLATFORM_NUMBER", color="PLATFORM_NUMBER",
                    title="Profiles Over Time", template="plotly_dark",
                    labels={"JULD": "Date", "PLATFORM_NUMBER": "Float ID"}
                )
                st.plotly_chart(fig_time, use_container_width=True)

        # --- Tab 2: Parameter Trends ---
        with tab2:
            st.subheader("Parameter Trends Over Time")
            param_to_plot = st.selectbox("Select a parameter to view trends:", ["TEMP", "PSAL", "PRES"])

            col1, col2 = st.columns(2)
            with col1:
                # Overall daily average
                trend_df = filtered_df.groupby("PROFILE_DATE")[param_to_plot].mean().reset_index()
                fig_trend = px.line(
                    trend_df, x="PROFILE_DATE", y=param_to_plot,
                    markers=True, line_shape="spline", template="plotly_dark",
                    title=f"Overall Average {param_to_plot} Trend",
                    labels={"PROFILE_DATE": "Date", param_to_plot: f"{param_to_plot} Value"}
                )
                st.plotly_chart(fig_trend, use_container_width=True)

            with col2:
                # Per-float average
                profile_df = filtered_df.groupby(["PLATFORM_NUMBER", "PROFILE_DATE"])[param_to_plot].mean().reset_index()
                fig_time_param = px.line(
                    profile_df, x="PROFILE_DATE", y=param_to_plot, color="PLATFORM_NUMBER",
                    markers=True, template="plotly_dark",
                    title=f"Per-Float Average {param_to_plot} Trend",
                    labels={"PROFILE_DATE": "Date", param_to_plot: f"{param_to_plot} Value"}
                )
                st.plotly_chart(fig_time_param, use_container_width=True)
                
            st.subheader("Depth Profiles")
            col3, col4 = st.columns(2)
            with col3:
                fig_temp_depth = px.line(
                    filtered_df, x="TEMP", y="PRES", color="PLATFORM_NUMBER",
                    title="Temperature vs Depth", template="plotly_dark",
                    labels={"TEMP": "Temperature (°C)", "PRES": "Pressure (dbar)"}
                )
                fig_temp_depth.update_yaxes(autorange="reversed")
                st.plotly_chart(fig_temp_depth, use_container_width=True)
                
            with col4:
                fig_psal_depth = px.line(
                    filtered_df, x="PSAL", y="PRES", color="PLATFORM_NUMBER",
                    title="Salinity vs Depth", template="plotly_dark",
                    labels={"PSAL": "Salinity (PSU)", "PRES": "Pressure (dbar)"}
                )
                fig_psal_depth.update_yaxes(autorange="reversed")
                st.plotly_chart(fig_psal_depth, use_container_width=True)

        # --- Tab 3: Distributions ---
        with tab3:
            st.subheader("Distribution of Key Parameters")
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(px.histogram(filtered_df, x="TEMP", title="Temperature Distribution", template="plotly_dark"), use_container_width=True)
                st.plotly_chart(px.histogram(filtered_df, x="PRES", title="Pressure Distribution", template="plotly_dark"), use_container_width=True)
            with col2:
                st.plotly_chart(px.histogram(filtered_df, x="PSAL", title="Salinity Distribution", template="plotly_dark"), use_container_width=True)
                st.plotly_chart(px.histogram(filtered_df, x="N_LEVELS", title="N_LEVELS Distribution", template="plotly_dark"), use_container_width=True)
        
        # --- Tab 4: T-S Diagram & QC ---
        with tab4:
            st.subheader("T-S Diagram and Data Quality")
            col1, col2 = st.columns(2)
            with col1:
                # NEW: T-S Diagram - a very insightful plot for oceanography
                fig_ts = px.scatter(
                    filtered_df, x="PSAL", y="TEMP", color="PRES",
                    title="Temperature-Salinity (T-S) Diagram",
                    labels={"PSAL": "Salinity (PSU)", "TEMP": "Temperature (°C)", "PRES": "Pressure (dbar)"},
                    template="plotly_dark"
                )
                st.plotly_chart(fig_ts, use_container_width=True)
                
            with col2:
                # Data Mode and QC plots
                fig_mode = px.pie(
                    filtered_df, names="DATA_MODE", title="Data Mode Distribution (R/A/D)",
                    template="plotly_dark", hole=0.4
                )
                st.plotly_chart(fig_mode, use_container_width=True)
            
            # QC Flags combined in one plot for better comparison
            qc_cols = ["TEMP_QC", "PSAL_QC", "PRES_QC"]
            qc_df = filtered_df[qc_cols].melt(var_name='QC_Parameter', value_name='QC_Flag')
            fig_qc = px.histogram(
                qc_df, x="QC_Flag", color="QC_Parameter", barmode='group',
                title="Data Quality Control (QC) Flag Distribution", template="plotly_dark"
            )
            st.plotly_chart(fig_qc, use_container_width=True)

    # # --- Run the App ---
    # if __name__ == "__main__":
    run_dashboard()
