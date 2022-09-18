from turtle import onclick
import streamlit as st
import draclient as dcl

client = dcl.DRAClient()

def refreshPipelineState():
    client.updateUsageAndAggregateExecutionStatus()
    st.session_state.pipe_refresh = True
    
    st.session_state["usage_pipeline"]=client.df_usage
    st.session_state["aggregate_pipeline"]=client.df_aggregate




st.sidebar.markdown("# Control Panel ")
st.sidebar.button("Refresh Executed Pipelines", on_click=refreshPipelineState)


st.sidebar.markdown("# Pipeline Runs")
st.sidebar.button("Run Usage Pipeline", on_click=refreshPipelineState)
st.sidebar.button("Run AggregatePipeline", on_click=refreshPipelineState)


st.markdown("# Data Pipeline Monitoring")




if 'pipe_refresh' not in st.session_state:
    st.session_state['pipe_refresh'] = False

has_freshed_once = False







if st.session_state.pipe_refresh:
    st.write(st.session_state["usage_pipeline"])
    st.write( st.session_state["aggregate_pipeline"])

st.write(st.session_state['pipe_refresh'])