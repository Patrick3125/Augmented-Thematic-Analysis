import streamlit as st
import pandas as pd

def show_modified_page():
    st.title("Modified Entries")

    if 'df' not in st.session_state or 'modified_flags' not in st.session_state:
        st.warning("No data available. Please visit the Main Page first.")
        return

    modified_df = st.session_state.df[st.session_state.modified_flags].copy()
    modified_df.insert(0, 'Modified', [True] * len(modified_df))

    st.write("Modified Entries:")
    st.dataframe(
        modified_df,
        hide_index=True,
        column_config={
            "Modified": st.column_config.CheckboxColumn(default=True, disabled=True),
            "initial_code": st.column_config.TextColumn(required=True),
            "x1": st.column_config.NumberColumn(disabled=True),
            "x2": st.column_config.NumberColumn(disabled=True)
        }
    )

    st.write(f"Number of modified entries: {len(modified_df)}")