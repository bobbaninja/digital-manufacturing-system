import streamlit as st
# import pandas as pd
# import sqlite3
# import plotly.express as px

# # Connect to database
# conn = sqlite3.connect("../sql/manufacturing.db")
# df = pd.read_sql("SELECT * FROM validated_data", conn)
# conn.close()

st.title("Manufacturing Data Dashboard")

# # Summary stats
# st.header("Summary Statistics")
# st.write(f"Total Events: {len(df)}")
# st.write(f"Out of Spec: {df['out_of_spec'].sum()}")
# st.write(f"Max Consecutive Failures: {df['consecutive_failures'].max()}")

# # Out of spec over time
# st.header("Out of Spec Over Time")
# fig1 = px.scatter(df, x="event_time", y="measured_value", color="out_of_spec", title="Measured Values Over Time")
# st.plotly_chart(fig1)

# # Consecutive failures by serial
# st.header("Consecutive Failures by Serial Number")
# fig2 = px.bar(df.groupby("serial_number")["consecutive_failures"].max().reset_index(), x="serial_number", y="consecutive_failures", title="Max Consecutive Failures per Serial")
# st.plotly_chart(fig2)

# # Process step performance
# st.header("Process Step Performance")
# fig3 = px.bar(df.groupby("process_step")["out_of_spec"].mean().reset_index(), x="process_step", y="out_of_spec", title="Out of Spec Rate by Process Step")
# st.plotly_chart(fig3)