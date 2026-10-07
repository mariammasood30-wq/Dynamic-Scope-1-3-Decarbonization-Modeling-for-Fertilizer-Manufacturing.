import pandas as pd
import streamlit as st

import forge_decarb as fd


st.set_page_config(page_title="Decarbonization Model", layout="wide")

st.title("Dynamic Scope 1-3 Decarbonization Modeling")
st.subheader("Fertilizer Manufacturing (Ammonia-Urea Complex)")
st.caption(
    "Explore annual emissions for an ammonia-urea plant. Model factors marked "
    "as assumptions are placeholders and should be replaced with site-specific data."
)

st.sidebar.header("Simulation Parameters")
capacity = st.sidebar.number_input(
    "Ammonia capacity (t/yr)", min_value=1, value=200_000, step=10_000
)
grid_decarb_rate = st.sidebar.slider(
    "Grid decarbonization (%)", min_value=0, max_value=100, value=15
)
hydrogen_blend = st.sidebar.slider(
    "Green hydrogen blend (%)", min_value=0, max_value=100, value=0
)
solar_share = st.sidebar.slider(
    "Solar electricity share (%)", min_value=0, max_value=55, value=0
)
heat_recovery = st.sidebar.slider(
    "Heat recovery (%)", min_value=0, max_value=100, value=0
)

default_grid_factor = fd.Params().grid_ef
params = fd.Params(
    capacity=float(capacity),
    grid_ef=default_grid_factor * (1 - grid_decarb_rate / 100),
)
plant = fd.Plant(params)
h2 = hydrogen_blend / 100
solar = solar_share / 100
heat = heat_recovery / 100

rows = plant.table(h2, solar, heat)
emissions = pd.DataFrame(
    [
        {
            "Emission source": label,
            "Without selected levers (t CO2/yr)": baseline,
            "With selected levers (t CO2/yr)": scenario,
            "Avoided (t CO2/yr)": avoided,
            "Avoided (%)": percent,
        }
        for label, baseline, scenario, avoided, percent in rows
        if not label.startswith("Ref:")
    ]
)
total = next(row for row in rows if row[0] == "TOTAL")

baseline_col, scenario_col, avoided_col = st.columns(3)
baseline_col.metric("Baseline emissions", f"{total[1]:,.0f} t CO2/yr")
scenario_col.metric("With selected levers", f"{total[2]:,.0f} t CO2/yr")
avoided_col.metric(
    "Emissions avoided",
    f"{total[3]:,.0f} t CO2/yr",
    delta=f"{total[4]:.1f}%",
)

st.subheader("Emissions by source")
st.dataframe(
    emissions,
    hide_index=True,
    use_container_width=True,
    column_config={
        "Without selected levers (t CO2/yr)": st.column_config.NumberColumn(
            format="localized"
        ),
        "With selected levers (t CO2/yr)": st.column_config.NumberColumn(
            format="localized"
        ),
        "Avoided (t CO2/yr)": st.column_config.NumberColumn(format="localized"),
        "Avoided (%)": st.column_config.NumberColumn(format="%.1f%%"),
    },
)

streams_before = plant.streams()
streams_after = plant.streams(h2, solar, heat)
scope_emissions = pd.DataFrame(
    {
        "Without selected levers": [
            streams_before["combustion"] + streams_before["smr"],
            streams_before["scope2_plant"] + streams_before["scope2_electrolyzer"],
            streams_before["scope3"],
        ],
        "With selected levers": [
            streams_after["combustion"] + streams_after["smr"],
            streams_after["scope2_plant"] + streams_after["scope2_electrolyzer"],
            streams_after["scope3"],
        ],
    },
    index=["Scope 1", "Scope 2", "Scope 3"],
)
st.subheader("Scope comparison")
st.bar_chart(scope_emissions)

if h2 > 0 or solar > 0 or heat > 0:
    st.subheader("Model recommendation")
    st.info(plant.recommend(h2, solar, heat))

with st.expander("Resource and equipment estimates"):
    green_h2_t, ro_water_m3 = plant.h2_water(h2)
    solar_data = plant.solar_sizing(h2, solar)
    first, second, third = st.columns(3)
    first.metric("Green hydrogen", f"{green_h2_t:,.0f} t/yr")
    second.metric("RO water for hydrogen", f"{ro_water_m3:,.0f} m³/yr")
    third.metric("Electrolyzer size", f"{plant.electrolyzer_size_kw(h2):,.0f} kW")
    st.write(
        f"Solar system: **{solar_data['system_kwp']:,.0f} kWp**, "
        f"approximately **{solar_data['panels']:,.0f} panels** over "
        f"**{solar_data['land_acres']:,.1f} acres**. "
        f"Estimated installed cost: **PKR {solar_data['cost_pkr']:,.0f}**."
    )
    if solar_data["capped"]:
        st.warning(
            f"The requested solar share is limited to {params.daylight_cap:.0%} "
            "by the model's daylight-only assumption."
        )

st.caption(
    f"Effective grid emissions factor: {params.grid_ef:.3f} t CO2/MWh. "
    "Changing an input updates the results automatically."
)
