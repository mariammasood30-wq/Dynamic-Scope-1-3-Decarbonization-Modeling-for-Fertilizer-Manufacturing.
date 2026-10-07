import streamlit as st
import forge_decarb as fd

st.set_page_config(page_title="Decarbonization Model", layout="wide")

st.title("Dynamic Scope 1-3 Decarbonization Modeling")
st.subheader("Fertilizer Manufacturing (Ammonia–Urea Complex)")

# Sidebar inputs for parameters
st.sidebar.header("Simulation Parameters")
capacity = st.sidebar.number_input("Ammonia Capacity (t/yr)", value=200000)
grid_decarb_rate = st.sidebar.slider("Grid Decarbonization Rate (%)", 0, 100, 50)

# Run button
if st.sidebar.button("Run Simulation"):
    st.write("Running decarbonization model...")
    
    # Example: Call your class/functions from forge_decarb.py
    # model = fd.DecarbonizationModel(capacity=capacity)
    # results = model.run()
    # st.dataframe(results)
    
    st.success("Simulation Complete!")