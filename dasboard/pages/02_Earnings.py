import streamlit as st
import pandas as pd

import plotly.graph_objects as go
import plotly.express as px

from st_aggrid import GridOptionsBuilder, AgGrid, ColumnsAutoSizeMode
from st_aggrid.shared import JsCode

from sqlalchemy import create_engine
from sqlalchemy.sql import text

# End of imports ----------------------------------------------------

# Margins for graphs
MARGIN = dict(l=0,r=10,b=10,t=25)

# JsCode to highlight cells when surprise < 0
cellsytle_jscode = JsCode(
    """
        function(params) {
            if (params.data.Surprise < 0) {
                return {
                    'color': 'white',
                    'backgroundColor': '#A93226'
                }
            }
        };
    """
)

def categorize_number(number):
    if number < 0:
        return "Negative"
    elif number == 0:
        return "Expected"
    else:
        return "Positive"

def get_data(): 
    engine = st.session_state.engine

    with engine.connect() as conn:
        df_annual = pd.read_sql('SELECT * FROM annual_earnings WHERE Ticker=(:tk)',
                         params=dict(tk=st.session_state.ticker),
                         con=conn, parse_dates=["Fiscal Date"])
        df_quarterly = pd.read_sql('SELECT * FROM quarterly_earnings WHERE Ticker=(:tk)',
                         params=dict(tk=st.session_state.ticker),
                         con=conn, parse_dates={"Fiscal Date", "Reported Date"})

    # Drop the ticker column
    df_annual = df_annual.drop("Ticker", axis=1)
    df_quarterly = df_quarterly.drop("Ticker", axis=1)

    # Round to 2 decimal places
    df_quarterly["Surprise Percent"] = df_quarterly["Surprise Percent"].round(2)

    # Categorise surprises into three groups
    df_quarterly["Category"] = df_quarterly["Surprise Percent"].apply(categorize_number)

    return (df_annual, df_quarterly)

def annual_page(ticker, df):
    # Need to save this ticker again or it looses it"s value
    st.session_state.ticker = ticker
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
    gb.configure_column(
        field="Fiscal Date",
        valueFormatter="value != undefined ? new Date(value).toLocaleString('en-AU', {dateStyle:'medium'}): ''"
    )
    gb.configure_column(
        field="Reported EPS",
        type=["numericColumn"]
    )
    gridOptions = gb.build()
    col1, col2 = st.columns([1, 2])
    with col1:
        AgGrid(df, gridOptions=gridOptions, theme="balham")
    with col2:
        fig = px.scatter(df, x="Fiscal Date", y="Reported EPS")
        fig.update_traces(marker_size=10, marker=dict(color='#A93226'))
        fig.update_layout(xaxis_title=None, legend_title=None, yaxis_title=None)
        
        st.plotly_chart(fig, theme='streamlit', use_container_width=True)

def quarterly_page(ticker, df):
    # Need to save this ticker again or it looses it's value
    st.session_state.ticker = ticker

    gb = GridOptionsBuilder()
    # Pagination is set to 10 rows per page
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
    # Apply the jscode to display the row in red for negative EPS
    gb.configure_default_column(cellStyle=cellsytle_jscode)

    gb.configure_column(
        field="Fiscal Date",
        valueFormatter="value != undefined ? new Date(value).toLocaleString('en-AU', {dateStyle:'medium'}): ''",
        width=125
    )
    gb.configure_column(
        field="Reported Date",
        valueFormatter="value != undefined ? new Date(value).toLocaleString('en-AU', {dateStyle:'medium'}): ''",
        width=145
    )
    gb.configure_column(
        field="Reported EPS",
        type=["numericColumn"],
        width=120
    )
    gb.configure_column(
        field="Estimated EPS",
        type=["numericColumn"],
        width=145
    )
    gb.configure_column(
        field="Surprise",
        type=["numericColumn"],
        width=115
    )
    gb.configure_column(
        field="Surprise Percent",
        valueFormatter="value + '%'",
        width=147
    )
    gridOptions = gb.build()

    col1, col2 = st.columns([1.5, 1])
    with col1:
        AgGrid(df, gridOptions=gridOptions, theme="balham", 
            # columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
            allow_unsafe_jscode=True)
    with col2:
        st.write("")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Fiscal Date"], y=df["Reported EPS"],
        name="Reported EPS",
        marker_color="#A93226"
    ))

    fig.add_trace(go.Scatter(
        x=df["Fiscal Date"], y=df["Estimated EPS"],
        name="Estimated EPS",
        marker_color="#F5B7B1"
    ))

    # Set options common to all traces with fig.update_traces
    fig.update_traces(mode="markers", marker_line_width=2, marker_size=10)
    fig.update_layout(title="Reported/Estimated EPS", margin=MARGIN, legend=dict(orientation="h"))
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    # Normlaize suprise column as it contains negative values
    # norm = ((df['Surprise'] - df['Surprise'].min()) / (df['Surprise'].max() - df['Surprise'].min())) * 100

    fig = px.scatter(df, x="Fiscal Date", y="Reported EPS", color="Category",
                     color_discrete_map = {'Negative': "#A93226", 'Expected': "#7FB3D5", 'Positive': "#1E8449"})
    fig.update_traces(marker_size=10)
    fig.update_layout(title="Reported EPS (Categorized)", xaxis_title=None, legend_title=None, yaxis_title=None,
                      margin=MARGIN, legend=dict(orientation="h"))
    st.plotly_chart(fig, theme='streamlit', use_container_width=True)

def sidebar_page():
    # Sidebar selection
    selected_range = st.sidebar.selectbox(
        "Select Period", options=["Annual", "Quarterly"]
    )
    # Updated the subheader with the selection
    st.text("{} Earnings".format(selected_range))
    if selected_range == "Annual":
        annual_page(st.session_state.ticker, df_annual)
    else:
        quarterly_page(st.session_state.ticker, df_quarterly)

st.subheader(st.session_state.page_subheader)
st.divider()

# Get annual and quarterly earnings data
df_annual, df_quarterly = get_data()
sidebar_page()