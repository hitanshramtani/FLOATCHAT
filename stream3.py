# streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np 
import ast
import plotly.express as px
from rag_pipeline import main

st.set_page_config(page_title="FloatChat - RAG", layout="wide")

st.title("FloatChat — KVPBot+RAG (ARGO)")

query = st.text_input("Ask a question about ARGO profiles (e.g., 'Show me salinity profiles near the bay of bangal in Febuary 2025')")

if st.button("Run"):
    if not query.strip():
        st.error("Enter a question.")
    else:
        with st.spinner("Running retrieval + LLM → SQL → DB..."):
            try:
                df = main(query)
                # st.write("DEBUG sample row:", df.iloc[0].to_dict())

            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()
        st.success(f"Returned {len(df)} rows")
        if df.empty:
            st.info("No results.")
        else:
            st.dataframe(df.head(200))
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