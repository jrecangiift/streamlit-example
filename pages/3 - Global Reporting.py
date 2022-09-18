import json
from mimetypes import common_types
from tkinter import Scrollbar
import streamlit as st
from common import GetPreviousMonth,CLIENT_REGIONAL_CONFIG, GetClientMapDataFrame

import pandas as pd
import draclient as dcl
import usageData as mud
import numpy as np
import altair as alt
from streamlit_ace import st_ace
from st_aggrid import AgGrid, GridUpdateMode, GridOptionsBuilder, JsCode, DataReturnMode
from PIL import Image

@st.experimental_memo
def LoadData(client, month, year):
    # st.write("LOAD DATA RUNNING")
    cl = dcl.DRAClient()    
    try:
        usage = cl.loadAggregateData(client, month, year)
        data = json.loads(usage)
        return data
    except:
        return {}



BACKGROUND_COLOR = 'blue'
COLOR = 'black'

st.markdown("""
        <style>
               .css-18e3th9 {
                    padding-top: 2rem;
                    padding-bottom: 10rem;
                    padding-left: 3rem;
                    padding-right: 3rem;
                }
               .css-1d391kg {
                    padding-top: 3.5rem;
                    padding-right: 1rem;
                    padding-bottom: 3.5rem;
                    padding-left: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)

st.markdown("""
<style>
div[data-testid="metric-container"] {
   background-color: rgb(240,242,246);
   border: 3px solid black;
   padding: 4% 4% 4% 10%;
   border-radius: 10px;
   color: rgb(100, 100, 119);
   overflow-wrap: break-word;
}

/* breakline for metric text         */
div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
   overflow-wrap: break-word;
   white-space: break-spaces;
   color: black;
}
</style>
"""
, unsafe_allow_html=True)


st.sidebar.markdown("# Global Reporting" )


df = GetClientMapDataFrame()

with st.sidebar:

    # with st.expander("Configure Report"):

    gb = GridOptionsBuilder.from_dataframe(df)
    # gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True, header_checkbox=True)
    # gb.configure_side_bar()
    # gb.configure_pagination(enabled=True)
    # gb.configure_auto_height(True)
    gb.configure_column("Region",rowGroup=True, hide=True)
    gb.configure_column("Country",rowGroup=True, hide=True)

    gridoptions = gb.build()


    response = AgGrid(
        df,
        gridOptions=gridoptions,
        height=500,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        fit_columns_on_grid_load=False,
        header_checkbox_selection_filtered_only=True,
        use_checkbox=True)


    

    col1, col2 = st.sidebar.columns(2)

    col1.selectbox("Year ",
                     [  '2022'],key="year_selected")

    col2.selectbox("Month",
                     ['4','5','6','7','8','9'],key="month_selected")

    gen= st.button("Generate Report")

if not gen:
    st.header("Configure Report's Scope")

if gen:
    clients_selected = []
    v = response['selected_rows']
    if v:
        dfs = pd.DataFrame(v)
        dfs = dfs.reset_index() 
        for index, row in dfs.iterrows():
            clients_selected.append(row["Client"])
    # st.write(clients_selected)

    st.title("Report Date: "+ st.session_state["month_selected"]+"/"+st.session_state["year_selected"])

    cl = dcl.DRAClient()  

    AllClientData = {}
    FailedLoad = []
    for client in clients_selected:
        data = LoadData(client,int(st.session_state["month_selected"]),int(st.session_state["year_selected"]))
        if data:
            AllClientData[client] = mud.MonthlyUsageData(data)
        else:
            FailedLoad.append(client)

    if len(FailedLoad)>0:
        st.error("Could not load clients: " + ','.join(FailedLoad))
    
    # st.write(AllClientData)


    clientsList = []
    PointsRedeemed =[]
    PointsAccrued =[]
    TotalPoints =[]
    TotalUsers = []
    TotalActiveUsers = []
    TakeRates = []
    NetRevPerMAU=[]
    MAUOverTU = []
    NetRevenues = []

    for client, d in AllClientData.items():
        clientsList.append(client)
        PointsAccrued.append(d.GetPointsAccruedInSTD_CCY())
        PointsRedeemed.append(d.GetPointsRedeemedInSTD_CCY())
        TotalPoints.append(d.GetTotalPointsAccruedInSTD_CCY())
        TotalUsers.append(d.GetTotalUsers())
        # TotalActiveUsers.append(d.GetTotalActiveUsers())




        NetRevenues.append(d.GetNetRevenue())

    data ={
        "Client":clientsList,
        "Points Accrued in #$":PointsAccrued,
        "Points Redeemed in #$": PointsRedeemed,
        "Net Revenues in #$": NetRevenues,
        "Total Points Value in #$":TotalPoints,
        "Total Users":TotalUsers,
        # "Total Active Users":TotalActiveUsers
    }

    global_df = pd.DataFrame(data)
    # st.dataframe(global_df)

    with st.expander("Expand Global Data"):

        gb = GridOptionsBuilder.from_dataframe(global_df)
        # gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
        
        gb.configure_side_bar()
        gridoptions = gb.build()
        AgGrid(
        global_df,
        gridOptions=gridoptions,
        height=600,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.NO_UPDATE,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        fit_columns_on_grid_load=True,
        header_checkbox_selection_filtered_only=True,
        use_checkbox=True)





    col1, col2, col3,col4 = st.columns(4)
 
    col1.metric("Net Revenues in #$", '{:,.0f}'.format(global_df["Net Revenues in #$"].sum()))
    col2.metric("Points Accrued in #$",'{:,.0f}'.format(global_df["Points Accrued in #$"].sum()))
    col3.metric("Points Redeemed in #$",'{:,.0f}'.format(global_df["Points Redeemed in #$"].sum()))
    col4.metric("Total Points Value in #$",'{:,.0f}'.format(global_df["Total Points Value in #$"].sum()))

   