from datetime import datetime
import json
import streamlit as st
from common import GetPreviousMonth
# from streamlit import caching
import pandas as pd
import draclient as dcl
import usageData as mud
import numpy as np
import altair as alt
from streamlit_ace import st_ace
from st_aggrid import AgGrid, GridUpdateMode, GridOptionsBuilder, JsCode
from PIL import Image
import datetime
import plotly.express as px
import plotly.graph_objects as go

import numpy as np





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

st.sidebar.markdown("# Client Reporting" )

cl = dcl.DRAClient()  

@st.experimental_memo
def LoadData(client, month, year):
    # st.write("LOAD DATA RUNNING")
    usage = cl.loadAggregateData(client, month, year)
    data = json.loads(usage)
    return data


st.sidebar.selectbox("Client ",
                     ['BDI','BRI','BJB','BNI'],key="client_selected")
col1, col2 = st.sidebar.columns(2)

col1.selectbox("Year ",
                     [  '2022'],key="year_selected")

col2.selectbox("Month",
                     ['4','5','6','7','8','9'],key="month_selected")

# load = st.sidebar.button(label="Load", on_click=LoadData(st.session_state["client_selected"],st.session_state["month_selected"],st.session_state["year_selected"]))
st.sidebar.markdown("""---""")
if st.sidebar.button("Clear Cache"):
    # Clear values from *all* memoized functions:
    # i.e. clear values from both square and cube
    st.experimental_memo.clear()


momTab, trendsTab, tabExperimental = st.tabs(["Month On Month", "Trends", "Experimental"])

with momTab:


    udata ={}
    try:
        udata= LoadData(st.session_state["client_selected"],st.session_state["month_selected"],st.session_state["year_selected"])
    except:
        st.error("Data unavailable for the month")
        st.stop()

    prev = GetPreviousMonth(int(st.session_state["month_selected"]),int(st.session_state["year_selected"]))
    prev_udata = {}
    try:
        prev_udata=LoadData(st.session_state["client_selected"],str(prev[0]),str(prev[1]))
    except:
        st.warning("Could not load previous Month")


    # udata = st.session_state["usageJson"]
    d = mud.MonthlyUsageData(udata)
    prev_d = mud.MonthlyUsageData(prev_udata)
    st.title("" + d.GetClientId() + " - "+str(d.GetMonth()) + "/"+ str(d.GetYear()))
    # st.markdown("""---""")

    # with st.expander("Raw Monthly Client Data"):
    #     st.write(udata)




    ### ************************************* Model ********************************************** ###

    total_std = d.GetTotalPointsAccruedInSTD_CCY()
    acc_std = d.GetPointsAccruedInSTD_CCY()
    red_std = d.GetPointsRedeemedInSTD_CCY()
    total_users = d.GetTotalUsers()
    total_active = d.GetActiveCustomers()

    df_chan_acc = d.GetPointsAcrruedPerChannel()
    df_chan_acc = df_chan_acc.sort_values(by=["Accrual in ST$"], ascending=False)
    total_GMV = df_chan_acc["GMV in ST$"].sum()

    df_prod_acc = d.GetPointsAcrruedPerProduct()
    df_prod_acc = df_prod_acc.sort_values(by=["Accrual in ST$"], ascending=False)  



    revDF = d.GetAllRevenues()
    gross_rev = revDF["#$ Amount"].sum()
    net_rev = revDF["Net #$ Amount"].sum()
    


    # Account Key Metrics

    take_rate = d.GetTakeRate()
    net_rev_per_active = d.GetNetRevenuePerActiveUser()
    MAUOverTU = d.GetMAUOverTU()
 

    ### ******************************************************************************************** ###


    st.subheader(":sparkles:Dashboard")
   


    if len(prev_udata.keys())>0:

    
        p_total_std = prev_d.GetTotalPointsAccruedInSTD_CCY()
        p_acc_std = prev_d.GetPointsAccruedInSTD_CCY()
        p_red_std = prev_d.GetPointsRedeemedInSTD_CCY()
        p_total_users = prev_d.GetTotalUsers()
        p_total_active = prev_d.GetActiveCustomers()

        p_df_chan_acc = prev_d.GetPointsAcrruedPerChannel()
        p_total_GMV = p_df_chan_acc["GMV in ST$"].sum()

        p_revDF = prev_d.GetAllRevenues()
        p_gross_rev = p_revDF["#$ Amount"].sum()
        p_net_rev = p_revDF["Net #$ Amount"].sum()

        
        p_take_rate = prev_d.GetTakeRate()
        p_net_rev_per_active = prev_d.GetNetRevenuePerActiveUser()
        p_MAUOverTU = prev_d.GetMAUOverTU()

        st.markdown("##### :red_circle:Key Account Performance Indicators")


        col1, col2, col3,col4 = st.columns(4)
        delta_take_rate = (take_rate-p_take_rate)/p_take_rate
        col1.metric("Take Rate (basis points)",'{:.2f} bp'.format(take_rate*10000), '{:.2f}%'.format(100*delta_take_rate))
        delta_net_rev_per_active = (net_rev_per_active-p_net_rev_per_active)/p_net_rev_per_active
        col2.metric("Net Revenue Per MAU (#$)",'{:.5f}'.format(net_rev_per_active), '{:.2f}%'.format(100*delta_net_rev_per_active))
        delta_MAUOverTU = (MAUOverTU-p_MAUOverTU)/p_MAUOverTU
        col3.metric("MAU Over TU",'{:.1f}%'.format(100*MAUOverTU), '{:.2f}%'.format(100*delta_MAUOverTU))
        delta_net_revenues = (net_rev-p_net_rev)/(p_net_rev)
        col4.metric("Net Revenues (#$)" , "{:,.0f}".format((net_rev)), '{:.2f}%'.format(100*delta_net_revenues))

        st.markdown("##### :large_blue_circle:Key Account Metrics")

        col1, col2, col3 = st.columns(3)
        delta_total_points = (total_std-p_total_std)/p_total_std
        col1.metric("Total Points Value (#$)", "{:,.0f}".format((total_std)), '{:.2f}%'.format(100*delta_total_points))
        delta_total_users = (total_users-p_total_users)/p_total_users
        col2.metric("Total Users" , "{:,.0f}".format((total_users)), '{:.2f}%'.format(100*delta_total_users))
        delta_total_active = (total_active-p_total_active)/p_total_active
        col3.metric("Monthly Active Users (MAU)", "{:,.0f}".format((total_active)), '{:.2f}%'.format(100*delta_total_active))
        


        col1, col2, col3 = st.columns(3)
        delta_accrual = (acc_std-p_acc_std)/p_acc_std
        col1.metric("Points Accrued Value (#$)", "{:,.0f}".format((acc_std)), '{:.2f}%'.format(100*delta_accrual))
        delta_red = (red_std-p_red_std)/p_red_std
        col2.metric("Points Redeemed Value (#$)",  "{:,.0f}".format((red_std)), '{:.2f}%'.format(100*delta_red))
        delta_total_gmv = (total_GMV-p_total_GMV)/p_total_GMV
        col3.metric("GMV (#$)" , "{:,.0f}".format(total_GMV), '{:.2f}%'.format(100*delta_total_gmv))
        

    else:
        st.markdown("##### :red_circle:Key Account Performance Indicators")


        col1, col2, col3,col4 = st.columns(4)

        col1.metric("Take Rate (basis points)",'{:.2f} bp'.format(take_rate*10000))
  
        col2.metric("Net Revenue Per MAU (#$)",'{:.5f}'.format(net_rev_per_active))
    
        col3.metric("MAU Over TU",'{:.1f}%'.format(100*MAUOverTU))
   
        col4.metric("Net Revenues (#$)" , "{:,.0f}".format((net_rev)))

        st.markdown("##### :large_blue_circle:Key Account Metrics")

        col1, col2, col3 = st.columns(3)
   
        col1.metric("Total Points Value (#$)", "{:,.0f}".format((total_std)))

        col2.metric("Total Users" , "{:,.0f}".format((total_users)))
  
        col3.metric("Monthly Active Users (MAU)", "{:,.0f}".format((total_active)))
        


        col1, col2, col3 = st.columns(3)

        col1.metric("Points Accrued Value (#$)", "{:,.0f}".format((acc_std)))

        col2.metric("Points Redeemed Value (#$)",  "{:,.0f}".format((red_std)))
 
        col3.metric("GMV (#$)" , "{:,.0f}".format(total_GMV))
        

        # df = d.GetMetricsDataFrame()
        # AgGrid(df,fit_columns_on_grid_load=True,  reload_data=False,update_mode=GridUpdateMode.VALUE_CHANGED)
        # # st.write(df)

    st.markdown("""---""")
    st.subheader(":arrow_heading_up:Accruals")

    

    with st.expander("Channel Accrual"):
        gb = GridOptionsBuilder.from_dataframe(df_chan_acc)
        gb.configure_pagination(paginationPageSize=25, paginationAutoPageSize=False)
        gridOptions = gb.build()
        AgGrid(df_chan_acc, gridOptions=gridOptions,fit_columns_on_grid_load=True,  reload_data=False,update_mode=GridUpdateMode.VALUE_CHANGED)

        col1, col2 = st.columns(2)  

        # fig_b = go.Figure(data=go.Scatter(      
        #     x=df_chan_acc["Accrual in ST$"], y=df_chan_acc["GMV in ST$"],
        #     mode='markers',
        #     marker=dict(
        #     size=20,              
        #     colorscale='Viridis', # one of plotly colorscales    
        #     )
        # ))

       

        fig = px.bar(df_chan_acc[["Channel","Accrual in ST$",]], x="Channel", y="Accrual in ST$", color="Channel")
        col1.plotly_chart(fig)
        fig2 = px.scatter(df_chan_acc[["Channel","Accrual in ST$", "GMV in ST$","Nb Prod"]], x="Accrual in ST$", y="GMV in ST$", color="Channel", size="Nb Prod")
        col2.plotly_chart(fig2)


    with st.expander("Product Accrual"):
        gb = GridOptionsBuilder.from_dataframe(df_prod_acc)
        gb.configure_pagination(paginationPageSize=10, paginationAutoPageSize=False)
        gridOptions = gb.build()
        AgGrid(df_prod_acc, gridOptions=gridOptions,fit_columns_on_grid_load=True,  reload_data=False,update_mode=GridUpdateMode.VALUE_CHANGED)

        df_prod_acc["size"] = 20
        col1, col2 = st.columns(2)  
        fig = px.sunburst(df_prod_acc[["Product","Channel","Accrual in ST$"]], path=['Channel', 'Product'], values='Accrual in ST$',
                  color='Channel', hover_data=["Accrual in ST$"])
        col1.plotly_chart(fig)
        fig2 = px.scatter(df_prod_acc[["Channel","Product","Accrual in ST$", "GMV in ST$","size"]], x="Accrual in ST$", y="GMV in ST$", color="Channel", size="size")
        col2.plotly_chart(fig2)

      
    st.markdown("""---""")
    st.subheader("	:arrow_heading_down:Redemptions")

    df = d.GetRedemptionDataFrame()

    with st.expander("Points Redemptions"):


        gb = GridOptionsBuilder.from_dataframe(df)
        gridOptions = gb.build()

        gridOptions["columnDefs"]= [
            { "field": 'Points Redeemed' },
            { "field": "#$ Redeemed" },       
        ]
        gridOptions["defaultColDef"]={
            "flex": 1,
            },
        gridOptions["autoGroupColumnDef"]= {
            "headerName": 'Classification',
            "minWidth": 200,
            "cellRendererParams": {
            "suppressCount": True,
            },
        },
        gridOptions["treeData"]=True
        gridOptions["animateRows"]=True
        gridOptions["groupDefaultExpanded"]= -1
        gridOptions["getDataPath"]=JsCode(""" function(data){
            return data.Classification.split("/");
        }""").js_code

        r = AgGrid(
            df,
            gridOptions=gridOptions,
            height=500,
            allow_unsafe_jscode=True,
            enable_enterprise_modules=True,
            filter=True,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            theme="material",
            tree_data=True
        )

    with st.expander("Marketplace Redemptions"):
        st.write("TBD with Marketplace feed")


    st.markdown("""---""")
    st.subheader(":family:Point Value Analytics")

    with st.expander("Users / Points Tiering Data & Charts"):
        df = d.GetUnitSTDDistribution()
        col1, col2, = st.columns(2) 
        col1.write(df)
        # AgGrid(df)

        df["size"] = 10
        fig2 = px.scatter(df[["Points Value","Users","#$ Value of Points", "Avg #$ Per User","size"]], x="#$ Value of Points", y="Avg #$ Per User", color="Users", size="size")
        col2.plotly_chart(fig2)

    with st.expander("Redemption Campaigns Recommendations"):
        st.write("TODO")

    st.markdown("""---""")
    st.subheader("	:part_alternation_mark:Revenues")

    with st.expander("Invoice Revenues"):
       
        
     
        

        col1, col2, = st.columns(2) 
        col1.metric("Gross Revenues","#$ {:,.0f}".format(gross_rev))
        col2.metric("Net Revenues", "#$ {:,.0f}".format(net_rev))
       
        col1, col2, = st.columns(2) 
        col1.write(revDF)
        netRevDF = revDF[revDF["Net #$ Amount"]>0]
        fig = px.bar(netRevDF[["Label","Net #$ Amount"]], x="Label", y="Net #$ Amount", color="Label", title="Net #$ Revenues per Category")
        col2.plotly_chart(fig)

    with st.expander("Marketplace Revenues"):
        st.write("TODO when markups, margins and currency effects available")








def dateFunc(s):
    toks = s.split("/")
    date = datetime.datetime(int(toks[1]),int(toks[0]),1)
    return date


with trendsTab:

    st.title(st.session_state["client_selected"] + " - Up To "+ st.session_state["month_selected"]+"/"+st.session_state["year_selected"])
    cl.updateUsageAndAggregateExecutionStatus()
    aggregate = cl.df_aggregate
    ds= (aggregate.loc[st.session_state["client_selected"]])
    ds = ds.dropna()


    with st.expander("Available Months"):
        st.write(ds)
    # st.write(aggregate.loc[st.session_state["client_selected"]])
    dateList = (ds.keys().tolist())
    dateList.sort(key=dateFunc)


  
    AllDataDic = {}
    upToDate = datetime.datetime(int(st.session_state["year_selected"]),int(st.session_state["month_selected"]),1)
    for date in dateList:
       
        toks = date.split("/")
        month = int(toks[0])
        year = int(toks[1])
        dateT = datetime.datetime(int(toks[1]),int(toks[0]),1)

        if dateT <= upToDate:
            data = LoadData(st.session_state["client_selected"], month,year)
            AllDataDic[date] = mud.MonthlyUsageData(data)

    # st.write(AllDataDic)

    
    st.subheader(":sparkles:Dashboard")

    RedAndAccDF =[]
    TotalPoints =[]
    TotalUsers = []
    TakeRates = []
    NetRevPerMAU=[]
    MAUOverTU = []
    NetRevenues = []


    for d in AllDataDic.keys():
        date = dateFunc(d)
        ud = AllDataDic[d]
        RedAndAccDF.append({"Date":pd.to_datetime(date).strftime('%B-%Y'), "#$ Value":ud.GetPointsAccruedInSTD_CCY(),"Type":"Accrual"})
        RedAndAccDF.append({"Date":pd.to_datetime(date).strftime('%B-%Y'), "#$ Value":ud.GetPointsRedeemedInSTD_CCY(),"Type":"Redemption"})
        TotalPoints.append({"Date":pd.to_datetime(date).strftime('%B-%Y'), "Total Points in #$":ud.GetTotalPointsAccruedInSTD_CCY()})
        TotalUsers.append({"Date":pd.to_datetime(date).strftime('%B-%Y'), "Total Users":ud.GetTotalUsers()})
        TakeRates.append({"Date":pd.to_datetime(date).strftime('%B-%Y'), "Take Rate in bp":10000*ud.GetTakeRate()})
        NetRevPerMAU.append({"Date":pd.to_datetime(date).strftime('%B-%Y'), "Net Revenue Per MAU":ud.GetNetRevenuePerActiveUser()})
        MAUOverTU.append({"Date":pd.to_datetime(date).strftime('%B-%Y'), "MAU Over TU %":100*ud.GetMAUOverTU()})
        NetRevenues.append({"Date":pd.to_datetime(date).strftime('%B-%Y'), "Net Revenues (#$)":ud.GetNetRevenue()})

    dfar = pd.DataFrame(RedAndAccDF)
    dfp = pd.DataFrame(TotalPoints)
    dfu = pd.DataFrame(TotalUsers)
    df_take_rate = pd.DataFrame(TakeRates)
    df_netrevperMAU = pd.DataFrame(NetRevPerMAU)
    df_MAU_over_TU = pd.DataFrame(MAUOverTU)
    df_netRevenues = pd.DataFrame(NetRevenues)
  
    figar = px.line(dfar, x="Date", y="#$ Value", color='Type', markers=True, title="Monthly Accruals & Redemptions in #$" ,width=500, height=400)
    figp = px.line(dfp, x="Date", y="Total Points in #$",  title="Total Points #$", width=500, height=400)
    figu= px.line(dfu, x="Date", y="Total Users", markers=True, title="Total Users", width=500, height=400)
    fig_takeRate = px.line(df_take_rate, x="Date", y="Take Rate in bp", markers=True, title="Take Rate in BP", width=700, height=400)
    fig_netrevperMAU = px.line(df_netrevperMAU, x="Date", y="Net Revenue Per MAU", markers=True, title="Net Revenue Per MAU", width=700, height=400)
    fig_MAU_over_TU = px.line(df_MAU_over_TU, x="Date", y="MAU Over TU %", markers=True, title="MAU Over TU %", width=700, height=400)
    fig_net_revenues = px.line(df_netRevenues, x="Date", y="Net Revenues (#$)", markers=True, title="Net Revenues (#$)", width=700, height=400)

    st.markdown("##### :red_circle:Key Account Performance Indicators")

    col1, col2 = st.columns(2)  
    col1.plotly_chart(fig_takeRate)
    col2.plotly_chart(fig_netrevperMAU)
    col1,col2 = st.columns(2)
    col1.plotly_chart(fig_MAU_over_TU)
    col2.plotly_chart(fig_net_revenues)

    st.markdown("##### :large_blue_circle:Key Account Metrics")


    
    col1, col2,col3 = st.columns(3)  
    col1.plotly_chart(figar)
    col2.plotly_chart(figp)
    col3.plotly_chart(figu)
   

    st.subheader(":sparkles:Channel Accruals Over Time")

    AllChanAcc = pd.DataFrame()
    for d in AllDataDic.keys():
        date = dateFunc(d)
        ud = AllDataDic[d]
        chan_acc = ud.GetPointsAcrruedPerChannel()
        chan_acc["Date"] = pd.to_datetime(date).strftime('%B-%Y')
        
        
        AllChanAcc= pd.concat([AllChanAcc,chan_acc])


    col1, col2 = st.columns(2)
    col1.write(AllChanAcc)

    fig2 = px.scatter(AllChanAcc[["Channel","Accrual in ST$", "GMV in ST$","Nb Prod","Date"]], x="Accrual in ST$", y="GMV in ST$",animation_frame="Date", color="Channel", size="Nb Prod")
    col2.plotly_chart(fig2)


with tabExperimental:
    st.write("TODO")