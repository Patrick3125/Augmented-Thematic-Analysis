import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

# Load Excel file
@st.cache_data
def load_data(file_path):
    df = pd.read_excel(file_path)
    return df

# Create the base figure
@st.cache_data
def create_base_figure():
    fig = go.Figure()
    fig.update_layout(
        title='Scatter Plot of x1 vs x2',
        xaxis_title='x1',
        yaxis_title='x2',
        width=800,
        height=600,
        clickmode='event+select',
        dragmode='select'
    )
    return fig

def get_point_color(selected):
    return 'blue' if selected else 'lightblue'

def filter_dataframe(df, filter_by):
    if filter_by == 'Selected':
        return df[df['Select'] == True]
    elif filter_by == 'Modified':
        return df[df['Modified'] == 'M']
    else:  # Default
        return df

# update figure colors without redrawing
def update_figure_colors(fig, selected_indices):
    colors = [get_point_color(i in selected_indices) for i in range(len(fig.data[0].x))]
    fig.data[0].marker.color = colors
    return fig

# Callback 
def on_datatable_change(edited_df):
    st.session_state.df['initial_code'] = edited_df['initial_code']
    st.session_state.datatable_initial_codes = edited_df['initial_code'].tolist()
    # Update modified flags
    st.session_state.modified_flags = [
        new != original
        for new, original in zip(st.session_state.datatable_initial_codes, st.session_state.original_initial_codes)
    ]
    # Save the changes to the Excel file
    st.session_state.df.to_excel("InitialcodeTsne.xlsx", index=False)

def gray_background_source(col):
    return ['background-color: #f0f0f0' for _ in col]

def center_align_modified(col):
    return ['text-align: center' for _ in col]
    

def show_main_page():
    st.title("Main Page")

    # Initialize session state
    if 'df' not in st.session_state:
        st.session_state.df = load_data("InitialcodeTsne.xlsx")
    if 'selected_indices' not in st.session_state:
        st.session_state.selected_indices = []
    if 'datatable_selections' not in st.session_state:
        st.session_state.datatable_selections = [False] * len(st.session_state.df)
    if 'datatable_initial_codes' not in st.session_state:
        st.session_state.datatable_initial_codes = st.session_state.df['initial_code'].tolist()
    if 'original_initial_codes' not in st.session_state:
        st.session_state.original_initial_codes = st.session_state.df['initial_code'].tolist()
    if 'modified_flags' not in st.session_state: st.session_state.modified_flags = [''] * len(st.session_state.df)
    if 'last_plotly_selection' not in st.session_state:
        st.session_state.last_plotly_selection = []
    if 'plot_selection_changed' not in st.session_state:
        st.session_state.plot_selection_changed = False
    if 'sort_column' not in st.session_state:
        st.session_state.sort_column = None
    if 'sort_direction' not in st.session_state:
        st.session_state.sort_direction = None

    base_fig = create_base_figure()

    # Add scatter points
    base_fig.add_trace(go.Scatter(
        x=st.session_state.df['x1'],
        y=st.session_state.df['x2'],
        mode='markers',
        marker=dict(
            size=10,
            color=[get_point_color(i in st.session_state.selected_indices) for i in range(len(st.session_state.df))],
        ),
        hovertemplate='initial_code: %{customdata}<extra></extra>',
        customdata=st.session_state.datatable_initial_codes
    ))

    # Use plotly_events to capture click and select events
    selected_points = plotly_events(base_fig, click_event=True, select_event=True, override_height=650, key="plot")

    # Update selection based on plot interaction
    if selected_points != st.session_state.last_plotly_selection:
        new_selected_indices = set(st.session_state.selected_indices)
        for point in selected_points:
            point_index = point.get('pointIndex')
            if point_index is not None:
                if point_index in new_selected_indices:
                    new_selected_indices.remove(point_index)
                else:
                    new_selected_indices.add(point_index)
        st.session_state.selected_indices = list(new_selected_indices)
        st.session_state.datatable_selections = [i in st.session_state.selected_indices for i in range(len(st.session_state.df))]
        st.session_state.last_plotly_selection = selected_points
        st.session_state.plot_selection_changed = True
        base_fig = update_figure_colors(base_fig, st.session_state.selected_indices)
        st.experimental_rerun()

    # Sorting dropdown
    filter_options = ['All', 'Selected', 'Modified']
    selected_filter = st.selectbox('Filter by:', filter_options, key='filter_selector')

    df_display = st.session_state.df.copy()
    df_display.insert(0, 'Select', st.session_state.datatable_selections)
    df_display.insert(1, 'Modified', ['       M' if flag else '' for flag in st.session_state.modified_flags])
    # Sort the DataFrame
    df_display_filtered = filter_dataframe(df_display, selected_filter)
    df_d_s = df_display_filtered.style.apply(gray_background_source, subset=['Source']).apply(center_align_modified, subset=['Modified'])

    # Display the DataFrame
    st.write("Loaded DataFrame:")
    edited_df = st.data_editor(
        df_d_s,
        hide_index=True,
        column_config={
            "Select": st.column_config.CheckboxColumn(default=False),
            "Modified": st.column_config.TextColumn(disabled=True),
            "initial_code": st.column_config.TextColumn(required=True),
        },
        disabled=["Source","x1", "x2", "Modified"],
        column_order=["Select", "Modified", "initial_code", "Source"],

        key="datatable"
    )
    

    # Update session state based on DataFrame changes
    if st.session_state.datatable is not None and not st.session_state.plot_selection_changed:
        # Map the sorted DataFrame back to the original order
        new_selections = df_display['Select'].values
        new_initial_codes = df_display['initial_code'].values
        
        for i, row in enumerate(edited_df.itertuples()):
            idx = df_display_filtered.index[i]
            new_selections[idx] = row.Select
            new_initial_codes[idx] = row.initial_code
        
        selections_changed = new_selections.tolist() != st.session_state.datatable_selections
        initial_codes_changed = new_initial_codes.tolist() != st.session_state.datatable_initial_codes

        if selections_changed or initial_codes_changed:
            if selections_changed:
                st.session_state.datatable_selections = new_selections.tolist()
                st.session_state.selected_indices = [i for i, selected in enumerate(new_selections) if selected]
                base_fig = update_figure_colors(base_fig, st.session_state.selected_indices)

            if initial_codes_changed:
                st.session_state.datatable_initial_codes = new_initial_codes.tolist()
                on_datatable_change(pd.DataFrame({'initial_code': new_initial_codes}))
                base_fig.data[0].customdata = st.session_state.datatable_initial_codes
                
                # Update modified flags
                st.session_state.modified_flags = [
                    '       M' if new != original else ''
                    for new, original in zip(new_initial_codes, st.session_state.original_initial_codes)]

            st.experimental_rerun()

    if st.session_state.plot_selection_changed:
        st.session_state.plot_selection_changed = False


