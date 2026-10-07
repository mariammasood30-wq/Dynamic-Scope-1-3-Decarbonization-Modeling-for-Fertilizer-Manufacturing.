from dataclasses import fields

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from forge_decarb import Params, Plant

plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial", "DejaVu Sans"]
plt.rcParams["font.family"] = "sans-serif"

st.set_page_config(
    page_title="FORGE-2026 | Ammonia & Urea Decarbonization Simulator",
    page_icon="🌱",
    layout="wide",
)

GREEN = "#17796f"
DARK = "#18332f"
PALE = "#e8f4f1"
GREY = "#40534f"
ORANGE = "#b9582a"

st.markdown(
    f"""
    <style>
    html, body, [class*="st-"], [data-testid="stAppViewContainer"] {{
        font-family: "Segoe UI", Arial, sans-serif !important;
    }}
    .stApp {{ background: #f2f6f5; }}
    [data-testid="stHeader"], [data-testid="stToolbar"], footer,
    [data-testid="stDecoration"], [data-testid="stStatusWidget"] {{
        display: none !important;
    }}
    [data-testid="stMainBlockContainer"] {{
        max-width: none; padding: 35px 9px 10px;
    }}
    section[data-testid="stMain"] {{
        flex: 0 1 951px; width: 951px; max-width: 951px;
    }}
    [data-testid="stSidebar"] {{
        background: #f2f6f5; min-width: 310px; max-width: 310px;
        border: 0;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        padding: 35px 8px 12px;
    }}
    [data-testid="stSidebarHeader"] {{
        display: none !important;
    }}
    [data-testid="stSidebarUserContent"] {{
        box-sizing: border-box; position: relative; top: 16px; left: 10px;
        width: calc(100% + 4px); min-height: calc(100vh - 73px);
        padding: 12px 12px 10px; background: white;
        border: 1px solid #dce7e4; border-radius: 14px;
    }}
    [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] {{
        gap: .32rem;
    }}
    [data-testid="stSidebar"] h2 {{
        color: {DARK}; font: 700 16px "Segoe UI", Arial, sans-serif;
        margin: 0 0 7px;
    }}
    [data-testid="stSidebar"] label p {{
        color: {DARK}; font: 700 12px "Segoe UI", Arial, sans-serif;
        margin-bottom: .15rem;
    }}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
        color: {GREY}; font: 400 10px/1.3 "Segoe UI", Arial, sans-serif;
        margin-bottom: .18rem;
    }}
    [data-testid="stSidebar"] input {{
        font: 400 12px "Segoe UI", Arial, sans-serif;
        border: 1px solid #dce7e4; border-radius: 5px;
    }}
    [data-testid="stNumberInput"] button {{
        display: none !important;
    }}
    [data-testid="stSidebar"] [data-testid="stSliderTickBar"],
    [data-testid="stSidebar"] [data-testid="stSliderThumbValue"] {{
        display: none !important;
    }}
    [data-testid="stSidebar"] [data-testid="stSlider"] {{
        margin-bottom: -.2rem;
    }}
    [data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {{
        background-color: {GREEN}; border-color: {GREEN};
    }}
    [data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stSliderTrack"] > div {{
        background-color: {GREEN};
    }}
    [data-testid="stSidebar"] button {{
        font: 700 12px "Segoe UI", Arial, sans-serif;
        border-radius: 8px;
    }}
    [data-testid="stTabs"] {{
        background: white; border: 1px solid #dce7e4; border-radius: 14px;
        padding: 10px; min-height: calc(100vh - 73px);
    }}
    [data-testid="stTabs"] [role="tablist"] {{
        gap: 2px; justify-content: center; border-bottom: 0;
        padding: 0 0 8px; min-height: 38px;
    }}
    [data-testid="stTab"] {{
        box-sizing: border-box; height: 30px; padding: 0 9px;
        color: {DARK}; background: white; border: 0; border-radius: 7px;
        font: 700 13px "Segoe UI", Arial, sans-serif;
    }}
    [data-testid="stTab"][aria-selected="true"] {{
        color: {DARK} !important; background: #d9eee9 !important;
        box-shadow: none !important;
    }}
    [data-testid="stTabs"] [role="tablist"]::after,
    [data-testid="stTabs"] [role="tablist"]::before {{
        display: none !important; content: none !important;
    }}
    [data-testid="stTab"] .react-aria-SelectionIndicator {{
        display: none !important;
    }}
    [data-testid="stTab"] p {{
        font: 700 13px "Segoe UI", Arial, sans-serif;
        margin: 0;
    }}
    [data-testid="stTabPanel"] {{
        background: #fff; border: 0; border-radius: 8px; padding: 8px 6px;
    }}
    [data-testid="stTabPanel"] h3 {{
        color: {DARK}; font: 700 16px "Segoe UI", Arial, sans-serif;
        margin: 0 0 .55rem;
    }}
    [data-testid="stTabPanel"] h4 {{
        color: {DARK}; font: 700 14px "Segoe UI", Arial, sans-serif;
    }}
    [data-testid="stTabPanel"] p {{
        font-family: "Segoe UI", Arial, sans-serif;
    }}
    .app-credit {{
        color: {GREY}; text-align: center; font: 400 9px "Segoe UI", Arial, sans-serif;
        padding-top: 9px;
    }}
    [data-testid="stCaptionContainer"] p {{
        color: {GREY}; font: 400 10px/1.35 "Segoe UI", Arial, sans-serif;
    }}
    [data-testid="stDataFrame"], [data-testid="stTable"] {{
        font: 400 12px "Segoe UI", Arial, sans-serif;
        border: 0; border-radius: 4px; overflow: hidden;
    }}
    div[data-testid="stAlert"] {{
        border: 0; background: {PALE}; color: {DARK}; border-radius: 9px;
        font: 700 11px "Segoe UI", Arial, sans-serif;
    }}
    [data-testid="stMetric"] label, [data-testid="stMetricValue"] {{
        font-family: "Segoe UI", Arial, sans-serif !important;
    }}
    @media (max-width: 1280px) {{
        section[data-testid="stMain"] {{
            flex: 1 1 auto; width: auto; max-width: none;
        }}
    }}
    @media (max-width: 900px) {{
        [data-testid="stSidebar"] {{ min-width: 260px; max-width: 260px; }}
        [data-testid="stMainBlockContainer"] {{ padding: 12px 8px 8px; }}
        [data-testid="stSidebar"] > div:first-child {{ padding-top: 12px; }}
        [data-testid="stSidebarUserContent"] {{
            top: 0; left: 0; width: 100%; min-height: calc(100vh - 24px);
        }}
        [data-testid="stTabs"] {{ min-height: calc(100vh - 36px); }}
        [data-testid="stTab"] {{ padding: 0 5px; font-size: 11px; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

DEFAULTS = {item.name: item.default for item in fields(Params)}

BASIS_GROUPS = [
    (
        "1. Plant and process (Scope 1)",
        [
            ("capacity", "Ammonia capacity", "t NH3/yr",
             "Yearly ammonia output. Set on the Model inputs panel."),
            ("urea_share", "Urea share of NH3", "fraction 0-1",
             "Part of ammonia turned into urea; urea locks up CO2. Set on the Model inputs panel."),
            ("process_ef", "SMR process CO2 factor", "t CO2 / t NH3",
             "CO2 released by the steam-methane-reforming reaction."),
            ("combustion_ef", "Gas combustion CO2 factor", "t CO2 / t NH3",
             "CO2 from burning natural gas in reformers and boilers."),
            ("stoich_process_ef", "Stoichiometric CO2 factor", "t CO2 / t NH3",
             "Ideal textbook value, used only for the reference row."),
            ("combustion_h2_share", "Combustion tied to H2 production", "fraction 0-1",
             "How much combustion CO2 falls when green H2 replaces SMR H2."),
        ],
    ),
    (
        "2. Electricity and supply chain (Scope 2 and 3)",
        [
            ("power_mwh", "Plant electricity use", "MWh / t NH3",
             "Grid power the existing plant needs per tonne of ammonia."),
            ("grid_ef", "Grid emissions factor", "t CO2 / MWh",
             "CO2 released per MWh of grid electricity."),
            ("logistics_ef", "Logistics CO2 factor", "t CO2 / t NH3",
             "CO2 from shipping one tonne of ammonia."),
        ],
    ),
    (
        "3. Green hydrogen and electrolyzer",
        [
            ("h2_demand_ef", "H2 needed per t NH3", "t H2 / t NH3",
             "From the reaction 3H2 + N2 -> 2NH3 (6/34)."),
            ("ro_water_ef", "RO water per kg H2", "kg water / kg H2",
             "Water for electrolysis, including reverse-osmosis reject losses."),
            ("electrolysis_kwh_per_kg", "Electrolyzer energy use", "kWh / kg H2",
             "Electricity required to make 1 kg of green hydrogen."),
            ("electrolyzer_operating_hours", "Electrolyzer running hours", "hours/day",
             "Sets the continuous electrolyzer power rating needed for annual H2 production."),
            ("electrolyzer_cost_per_kw", "Electrolyzer installed cost", "PKR / kW",
             "Estimated turnkey electrolyzer price per kW."),
        ],
    ),
    (
        "4. Abatement costs (MAC ranking)",
        [
            ("h2_cost", "Green H2 blending", "PKR / t CO2 avoided",
             "Cost of avoiding one tonne of CO2 with green hydrogen."),
            ("solar_cost", "Solar PV", "PKR / t CO2 avoided",
             "Cost of avoiding one tonne of CO2 with solar panels."),
            ("heat_recovery_cost", "Waste-heat recovery", "PKR / t CO2 avoided",
             "Cost of avoiding one tonne of CO2 by recovering flue-gas heat."),
        ],
    ),
    (
        "5. Solar PV sizing (no battery, daylight only)",
        [
            ("daylight_cap", "Max solar share without storage", "fraction 0-1",
             "Highest round-the-clock load share solar can cover without batteries."),
            ("daylight_hours", "Effective daylight hours", "hours/day",
             "Hours per day the panels produce usable power."),
            ("performance_ratio", "System performance ratio", "fraction 0-1",
             "Accounts for heat, wiring, inverter and dust losses."),
            ("panel_watt", "Panel rating", "W per panel", "Power rating of one solar panel."),
            ("cost_per_watt_pkr", "Installed solar cost", "PKR / W",
             "Turnkey installed cost per watt of solar."),
            ("land_acres_per_mw", "Land needed", "acres / MW",
             "Land area used per MW of solar installed."),
        ],
    ),
    (
        "6. Feedstock and water",
        [
            ("ch4_co2_ratio", "CO2 per tonne of natural gas", "t CO2 / t CH4",
             "CO2 released per tonne of methane reformed or burned."),
            ("process_water_ef", "Process water per t NH3", "t water / t NH3",
             "Water used in reforming and shift reactions."),
            ("n2_ef", "Nitrogen per t NH3", "t N2 / t NH3",
             "Nitrogen requirement from N2 + 3H2 -> 2NH3."),
        ],
    ),
]

FEED_ROWS = [
    ("RAW MATERIALS IN", None, None, None),
    ("Natural gas - reforming feedstock", "t/yr", "ch4_feed", False),
    ("Natural gas - fuel (furnaces, boilers)", "t/yr", "ch4_fuel", False),
    ("Natural gas - total", "t/yr", "ch4_total", True),
    ("Process water (reforming / shift)", "t/yr", "water_process", False),
    ("RO water for electrolysis", "m3/yr", "water_ro", False),
    ("Nitrogen (N2, from air)", "t/yr", "n2", False),
    ("Green hydrogen (electrolysis)", "t/yr", "h2_green", False),
    ("Electricity (plant + electrolyzer)", "MWh/yr", "elec_mwh", True),
    ("PRODUCTS OUT", None, None, None),
    ("Ammonia produced", "t/yr", "nh3_made", False),
    ("of which used to make urea", "t/yr", "nh3_to_urea", False),
    ("Ammonia sold as NH3", "t/yr", "nh3_sold", True),
    ("Urea produced", "t/yr", "urea", True),
    ("CO2 locked into urea", "t/yr", "co2_in_urea", False),
]


if "basis_values" not in st.session_state:
    st.session_state.basis_values = DEFAULTS.copy()
for key, value in (
    ("capacity_input", int(DEFAULTS["capacity"])),
    ("urea_input", int(DEFAULTS["urea_share"] * 100)),
    ("h2_input", 0.0),
    ("heat_input", 0),
    ("solar_input", 0.0),
):
    if key not in st.session_state:
        st.session_state[key] = value

st.sidebar.header("Model inputs")

def reset_model():
    st.session_state.basis_values = DEFAULTS.copy()
    for _, basis_rows in BASIS_GROUPS:
        for key, _, _, _ in basis_rows:
            if key not in ("capacity", "urea_share"):
                st.session_state[f"basis_{key}"] = DEFAULTS[key]
    for key, value in (
        ("capacity_input", int(DEFAULTS["capacity"])),
        ("urea_input", int(DEFAULTS["urea_share"] * 100)),
        ("h2_input", 0.0),
        ("heat_input", 0.0),
        ("solar_input", 0.0),
    ):
        st.session_state[key] = value

capacity = st.sidebar.number_input(
    "Ammonia capacity (t NH3/yr)",
    min_value=1,
    step=10_000,
    key="capacity_input",
    help="Annual ammonia output; used as the plant production basis.",
)
urea_pct = st.sidebar.number_input(
    "Urea share of NH3 (%)  (0 = gross CO2)",
    min_value=0,
    max_value=100,
    step=1,
    key="urea_input",
    help="Share of ammonia converted to urea. The CO2 in urea is deducted from net process emissions.",
)
h2_current = float(st.session_state.h2_input)
h2_pct = st.sidebar.slider(
    f"Green hydrogen blending: {h2_current:.1f} %",
    min_value=0.0,
    max_value=10.0,
    step=0.1,
    key="h2_input",
    help="Green hydrogen replaces fossil hydrogen made by SMR. The desktop model limits this lever to 10%.",
)
params_for_controls = Params(
    **{
        **st.session_state.basis_values,
        "capacity": float(capacity),
        "urea_share": urea_pct / 100,
    }
)
plant_for_controls = Plant(params_for_controls)
plant_load_kwh_day = plant_for_controls.total_electricity_kwh_day()
_, electrolyzer_kwh_day = plant_for_controls.h2_electricity(h2_pct / 100)
combined_load_kwh_day = plant_load_kwh_day + electrolyzer_kwh_day
solar_max_kwh_day = params_for_controls.daylight_cap * combined_load_kwh_day
solar_slider_max = float(max(solar_max_kwh_day, 1))
if st.session_state.solar_input > solar_slider_max:
    st.session_state.solar_input = solar_slider_max

h2_t, ro_water = plant_for_controls.h2_water(h2_pct / 100)
h2_mwh, h2_kwh_day = plant_for_controls.h2_electricity(h2_pct / 100)
st.sidebar.caption(
    f"Green H2: {h2_t:,.0f} t/yr  |  RO water: {ro_water:,.0f} m³/yr\n\n"
    f"Electrolysis electricity: {h2_mwh:,.0f} MWh/yr ({h2_kwh_day:,.0f} kWh/day)"
)
heat_current = int(st.session_state.heat_input)
heat_pct = st.sidebar.slider(
    f"Heat recovery (combustion): {heat_current} %",
    min_value=0,
    max_value=90,
    step=1,
    key="heat_input",
    help="Waste-heat recovery reduces the natural gas burned for process heat; modelled as a Scope 1a lever.",
)
streams_base_for_controls = plant_for_controls.streams()
streams_current_for_controls = plant_for_controls.streams(
    h2_pct / 100, 0, heat_pct / 100
)
st.sidebar.caption(
    f"Combustion CO2: {streams_base_for_controls['combustion']:,.0f} -> "
    f"{streams_current_for_controls['combustion']:,.0f} t/yr "
    f"({streams_base_for_controls['combustion'] - streams_current_for_controls['combustion']:,.0f} avoided)"
)
st.sidebar.markdown(
    f"**Plant only:** {plant_load_kwh_day:,.0f} kWh/day (fixed)  \n"
    f"**Plant + electrolyzer:** {combined_load_kwh_day:,.0f} kWh/day"
)
solar_current = float(st.session_state.solar_input)
solar_kwh_day = st.sidebar.slider(
    f"Solar PV: {solar_current:,.0f} kWh/day",
    min_value=0.0,
    max_value=solar_slider_max,
    step=max(solar_slider_max / 100, 1.0),
    key="solar_input",
    help="Daily solar generation offsets electricity demand. Solar is daylight-only and capped by the no-battery maximum.",
)
st.sidebar.caption(
    f"Solar available in daylight only (~{params_for_controls.daylight_hours:g} h); "
    "slider capped at the max deliverable (plant + electrolyzer) without battery storage."
)
run_col, reset_col = st.sidebar.columns(2, gap="small")
run_col.button("Run model", type="primary", use_container_width=True)
reset_col.button("Reset", on_click=reset_model, use_container_width=True)
st.sidebar.markdown(
    "<div class='app-credit'>Created by Mariam Masood · mariam.masood30@gmail.com</div>",
    unsafe_allow_html=True,
)

params = Params(
    **{
        **st.session_state.basis_values,
        "capacity": float(capacity),
        "urea_share": urea_pct / 100,
    }
)
plant = Plant(params)
h2 = h2_pct / 100
heat = heat_pct / 100
combined_load_kwh_day = (
    plant.total_electricity_kwh_day() + plant.h2_electricity(h2)[1]
)
solar_kwh_day = min(float(solar_kwh_day), params.daylight_cap * combined_load_kwh_day)
solar = solar_kwh_day / combined_load_kwh_day if combined_load_kwh_day else 0.0

streams_before = plant.streams()
streams_after = plant.streams(h2, solar, heat)
rows = plant.table(h2, solar, heat)
h2_t, ro_water = plant.h2_water(h2)
h2_mwh, h2_kwh_day = plant.h2_electricity(h2)
electrolyzer_kw = plant.electrolyzer_size_kw(h2)
electrolyzer_cost = plant.electrolyzer_cost(h2)
solar_data = plant.solar_sizing(h2, solar)

tab_feed, tab_table, tab_scope, tab_mac, tab_upgrade, tab_basis = st.tabs(
    [
        "Feedstock",
        "Scope 1-3 table",
        "Scope diagram",
        "MAC curve",
        "Upgrading cost",
        "Basis & equations",
    ]
)

with tab_feed:
    st.subheader("Raw material in / product out")
    feed_before = plant.feedstock()
    feed_after = plant.feedstock(h2, heat)
    feed_rows = []
    for label, unit, key, bold in FEED_ROWS:
        if key is None:
            feed_rows.append({"Raw material in / product out": label, "Without": "", "With": "", "Change": ""})
            continue
        before_value, after_value = feed_before[key], feed_after[key]
        pct_change = (
            100 * (after_value - before_value) / before_value
            if before_value
            else None
        )
        feed_rows.append(
            {
                "Raw material in / product out": f"{label} ({unit})",
                "Without": before_value,
                "With": after_value,
                "Change": (
                    f"{pct_change:+.1f}%"
                    if pct_change is not None
                    else ("new" if after_value else "-")
                ),
            }
        )
    feed_frame = pd.DataFrame(feed_rows)

    def style_feed_row(row):
        label = row["Raw material in / product out"]
        if label in ("RAW MATERIALS IN", "PRODUCTS OUT"):
            return ["background-color: #d9eee9; color: #18332f; font-weight: bold"] * len(row)
        if label.startswith(
            (
                "Natural gas - total",
                "Electricity (plant + electrolyzer)",
                "Ammonia sold as NH3",
                "Urea produced",
            )
        ):
            return ["background-color: #e8f4f1; color: #18332f; font-weight: bold"] * len(row)
        return [""] * len(row)

    feed_style = (
        feed_frame.style
        .apply(style_feed_row, axis=1)
        .format(
            {
                "Without": lambda value: f"{value:,.0f}" if isinstance(value, (int, float)) else value,
                "With": lambda value: f"{value:,.0f}" if isinstance(value, (int, float)) else value,
            },
            na_rep="",
        )
        .set_table_styles(
            [
                {
                    "selector": "th",
                    "props": [
                        ("background-color", GREEN),
                        ("color", "white"),
                        ("font-weight", "bold"),
                        ("text-align", "center"),
                    ],
                },
                {"selector": "td", "props": [("padding", ".35rem .5rem")]},
            ]
        )
    )
    st.table(feed_style)
    st.caption(
        "Natural gas is back-calculated from model CO2 numbers, assuming pure methane "
        "(gas = CO2 / 2.743). Green H2 lowers reforming gas, furnace gas and process "
        "water, but adds RO water and electricity. Factors are editable in Basis & equations."
    )

with tab_table:
    st.subheader("CO2 emissions")
    table_rows = [
        {
            "Source": label,
            "Without (t CO2/yr)": baseline,
            "With (t CO2/yr)": scenario,
            "Avoided (t CO2/yr)": avoided,
            "% avoided": percent,
        }
        for label, baseline, scenario, avoided, percent in rows
    ]
    table_rows.extend(
        [
            {
                "Source": "Green H2 required (t/yr)",
                "Without (t CO2/yr)": None,
                "With (t CO2/yr)": h2_t,
                "Avoided (t CO2/yr)": None,
                "% avoided": None,
            },
            {
                "Source": "RO water required (m3/yr)",
                "Without (t CO2/yr)": None,
                "With (t CO2/yr)": ro_water,
                "Avoided (t CO2/yr)": None,
                "% avoided": None,
            },
            {
                "Source": "Electrolysis electricity required (MWh/yr)",
                "Without (t CO2/yr)": None,
                "With (t CO2/yr)": h2_mwh,
                "Avoided (t CO2/yr)": None,
                "% avoided": None,
            },
        ]
    )
    emissions_frame = pd.DataFrame(table_rows)

    def style_emission_row(row):
        source = row["Source"]
        if source == "TOTAL":
            return ["background-color: #18332f; color: white; font-weight: bold"] * len(row)
        if source.startswith(("Scope 1b - ", "Scope 1 total", "Scope 2 total",
                              "Green H2", "RO water", "Electrolysis")):
            return ["background-color: #e8f4f1; color: #18332f; font-weight: bold"] * len(row)
        if source.startswith("Ref:"):
            return ["color: #40534f; font-style: italic"] * len(row)
        return [""] * len(row)

    emissions_style = (
        emissions_frame.style
        .apply(style_emission_row, axis=1)
        .format(
            {
                "Without (t CO2/yr)": lambda value: f"{value:,.0f}" if pd.notna(value) else "-",
                "With (t CO2/yr)": lambda value: f"{value:,.0f}" if pd.notna(value) else "-",
                "Avoided (t CO2/yr)": lambda value: f"{value:,.0f}" if pd.notna(value) else "-",
                "% avoided": lambda value: f"{value:.1f} %" if pd.notna(value) else "-",
            },
            na_rep="-",
        )
        .set_table_styles(
            [
                {
                    "selector": "th",
                    "props": [
                        ("background-color", GREEN),
                        ("color", "white"),
                        ("font-weight", "bold"),
                        ("text-align", "center"),
                    ],
                },
                {"selector": "td", "props": [("padding", ".32rem .45rem")]},
            ]
        )
    )
    st.table(
        emissions_style,
    )
    st.caption("The reference stoichiometric row is for comparison and is not included in totals.")

with tab_scope:
    st.subheader("CO2 emissions by scope")
    scope_source_data = [
        ("Scope 1", "SMR process", streams_before["smr"], streams_after["smr"]),
        ("Scope 1", "Combustion", streams_before["combustion"], streams_after["combustion"]),
        ("Scope 2", "Plant power", streams_before["scope2_plant"], streams_after["scope2_plant"]),
        (
            "Scope 2",
            "Electrolyzer",
            streams_before["scope2_electrolyzer"],
            streams_after["scope2_electrolyzer"],
        ),
        ("Scope 3", "Supply chain", streams_before["scope3"], streams_after["scope3"]),
    ]
    figure, axis = plt.subplots(figsize=(11, 5), facecolor="white")
    axis.set_facecolor("white")
    grouped_sources = [
        ("Scope 1", [scope_source_data[0], scope_source_data[1]]),
        ("Scope 2", [scope_source_data[2], scope_source_data[3]]),
        ("Scope 3", [scope_source_data[4]]),
    ]
    x_positions = []
    source_labels = []
    scope_ranges = []
    x = 0.0
    for scope_name, sources in grouped_sources:
        scope_start = x
        for _, source, before, after in sources:
            x_positions.append(x)
            source_labels.append(source)
            x += 1.0
        scope_ranges.append((scope_name, scope_start, x - 1.0))
        x += 0.8

    before_values = [item[2] for item in scope_source_data]
    after_values = [item[3] for item in scope_source_data]
    bar_width = 0.34
    before_bars = axis.bar(
        [position - bar_width / 2 for position in x_positions],
        before_values,
        width=bar_width,
        color="#b8ddd5",
        edgecolor=DARK,
        label="Before intervention",
        zorder=3,
    )
    after_bars = axis.bar(
        [position + bar_width / 2 for position in x_positions],
        after_values,
        width=bar_width,
        color=GREEN,
        edgecolor=DARK,
        label="After intervention",
        zorder=3,
    )
    maximum = max(before_values + after_values) or 1
    for bars in (before_bars, after_bars):
        for bar in bars:
            axis.annotate(
                f"{bar.get_height():,.0f}",
                (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
                color=DARK,
            )
    axis.set_xticks(x_positions, source_labels)
    axis.tick_params(axis="x", labelsize=9)
    axis.set_ylim(-maximum * 0.2, maximum * 1.32)
    axis.set_ylabel("t CO2/yr")
    axis.grid(axis="y", color="#dce7e4", linewidth=0.8, zorder=0)
    axis.set_axisbelow(True)
    for side in ("top", "right", "left"):
        axis.spines[side].set_visible(False)
    axis.spines["bottom"].set_color("#dce7e4")
    for scope_name, left, right in scope_ranges:
        before_total = sum(item[2] for item in scope_source_data if item[0] == scope_name)
        after_total = sum(item[3] for item in scope_source_data if item[0] == scope_name)
        pct = (after_total - before_total) / before_total * 100 if before_total else 0.0
        center = (left + right) / 2
        axis.plot([left - .35, left - .35, right + .35, right + .35],
                  [-maximum * .07, -maximum * .1, -maximum * .1, -maximum * .07],
                  color=DARK, linewidth=1.5, clip_on=False)
        axis.text(
            center,
            maximum * 1.2,
            f"{before_total:,.0f} -> {after_total:,.0f}\n"
            f"t CO2/yr ({pct:+.1f}%)",
            ha="center",
            va="top",
            fontsize=9,
            fontweight="bold",
            color=GREEN if pct <= 0 else ORANGE,
        )
        axis.text(center, -maximum * .15, scope_name, ha="center", va="top",
                  fontsize=10, fontweight="bold", color=DARK)
    axis.legend(frameon=False, loc="upper left", ncol=2)
    figure.tight_layout()
    st.pyplot(figure, use_container_width=True)
    plt.close(figure)
    scope_totals = []
    for scope in ("Scope 1", "Scope 2", "Scope 3"):
        before = sum(item[2] for item in scope_source_data if item[0] == scope)
        after = sum(item[3] for item in scope_source_data if item[0] == scope)
        pct = (after - before) / before * 100 if before else 0.0
        scope_totals.append(
            {"Scope": scope, "Before (t CO2/yr)": before, "After (t CO2/yr)": after, "Change": f"{pct:+.1f}%"}
        )
    st.dataframe(pd.DataFrame(scope_totals), hide_index=True, use_container_width=True)
    st.caption(
        f"Selected levers: green H2 {h2 * 100:.1f}%, heat recovery {heat * 100:.0f}%, "
        f"solar {solar * 100:.1f}% of combined electricity demand."
    )

with tab_mac:
    st.subheader("Marginal abatement cost (MAC)")
    levers = plant.levers(h2, solar, heat)
    mac_frame = pd.DataFrame(
        [
            {
                "Lever": name,
                "Abatement cost (PKR/t CO2)": cost,
                "CO2 avoided (t/yr)": avoided,
                "Annual cost (PKR million/yr)": max(avoided, 0) * cost / 1_000_000,
            }
            for name, avoided, cost in levers
        ]
    )
    chart_column, cards_column = st.columns([3, 2], gap="medium")
    with chart_column:
        figure, axis = plt.subplots(figsize=(7, 4.6), facecolor="white")
        axis.set_facecolor("white")
        ordered = mac_frame.sort_values("Abatement cost (PKR/t CO2)", ascending=False)
        bars = axis.barh(
            ordered["Lever"],
            ordered["Abatement cost (PKR/t CO2)"],
            color=GREEN,
            edgecolor="white",
            height=0.55,
        )
        maximum_cost = max(ordered["Abatement cost (PKR/t CO2)"].max(), 1)
        for bar in bars:
            axis.text(
                bar.get_width() + maximum_cost * .02,
                bar.get_y() + bar.get_height() / 2,
                f"{bar.get_width():,.0f}",
                va="center",
                fontsize=9,
                fontweight="bold",
                color=DARK,
            )
        axis.set_xlim(0, maximum_cost * 1.3)
        axis.set_title("Abatement cost (PKR / t CO2 avoided)", fontweight="bold", color=DARK)
        axis.grid(axis="x", color="#dce7e4", linewidth=0.8)
        axis.set_axisbelow(True)
        for side in ("top", "right"):
            axis.spines[side].set_visible(False)
        axis.spines["left"].set_visible(False)
        axis.spines["bottom"].set_color("#dce7e4")
        figure.tight_layout()
        st.pyplot(figure, use_container_width=True)
        plt.close(figure)
    with cards_column:
        lever_cards = (
            ("Solar PV", "Scope 2a"),
            ("Heat recovery", "Scope 1a"),
            ("Green H2 blending", "Scope 1a + 1b + 2b"),
        )
        for lever_name, scope_name in lever_cards:
            avoided, cost = next(
                (amount, price)
                for name, amount, price in levers
                if name == lever_name
            )
            annual_cost_text = (
                f"Annual cost: PKR {avoided * cost / 1e6:,.1f} million/yr"
                if avoided > 0
                else "Annual cost: - (no CO2 saved)"
            )
            with st.container(border=True):
                st.markdown(f"**{lever_name} avoided ({scope_name})**")
                st.metric("CO2 avoided", f"{avoided:+,.0f} t CO2/yr")
                st.caption(annual_cost_text)
    st.caption("*Green H2's listed cost assumes clean electrolyzer power.")

with tab_upgrade:
    st.subheader("Solar cost")
    st.info(
        f"Combined electricity need (plant + electrolyzer) is "
        f"{solar_data['total_kwh_day']:,.0f} kWh/day. Selected solar generation is "
        f"{solar_data['need_kwh_day']:,.0f} kWh/day (~{solar_data['achievable'] * 100:.0f}% "
        f"of demand). Without battery storage, daylight-only solar can cover at most "
        f"~{params.daylight_cap * 100:.0f}% of the round-the-clock load "
        f"(about {solar_data['total_kwh_day'] * params.daylight_cap:,.0f} kWh/day)."
    )
    solar_metrics = st.columns(4)
    solar_metrics[0].metric("System size needed", f"{solar_data['system_kwp']:,.0f} kWp")
    solar_metrics[1].metric(
        f"Number of panels ({params.panel_watt:g} W each)",
        f"{solar_data['panels']:,.0f}",
    )
    solar_metrics[2].metric("Land required", f"{solar_data['land_acres']:,.1f} acres")
    solar_metrics[3].metric(
        "Estimated installed cost",
        f"PKR {solar_data['cost_pkr'] / 1_000_000:,.1f} million",
    )
    st.caption(
        f"Assumptions: {params.daylight_hours:g} effective daylight hours/day, "
        f"{params.performance_ratio * 100:.0f}% performance ratio, "
        f"PKR {params.cost_per_watt_pkr:g}/W installed, {params.panel_watt:g} W panels, "
        f"{params.land_acres_per_mw:g} acres/MW, no battery."
    )
    st.subheader("Green H2")
    h2_metrics = st.columns(2)
    h2_metrics[0].metric("Electrolyzer size needed", f"{electrolyzer_kw:,.0f} kW")
    h2_metrics[1].metric(
        "Estimated installed cost",
        f"PKR {electrolyzer_cost / 1_000_000:,.1f} million",
    )
    st.caption(
        f"Assumptions: electrolyzer runs {params.electrolyzer_operating_hours:g} h/day "
        f"and uses {params.electrolysis_kwh_per_kg:g} kWh/kg H2. It draws grid power "
        "whenever solar is unavailable. Electrolyzer cost is "
        f"PKR {params.electrolyzer_cost_per_kw:,.0f}/kW."
    )

with tab_basis:
    st.subheader("Basis factors (editable)")
    st.markdown("**0.88 CH₄ + 1.24 H₂O + 1.26 air → 2 NH₃ + 0.88 CO₂**")
    st.caption(
        "Edit the model assumptions below and select Apply basis. Ammonia capacity "
        "and urea share are controlled in the Model inputs panel."
    )
    with st.form("basis_form"):
        edited_basis = st.session_state.basis_values.copy()
        for group_name, basis_rows in BASIS_GROUPS:
            st.markdown(f"#### {group_name}")
            for key, label, unit, note in basis_rows:
                if key in ("capacity", "urea_share"):
                    st.write(f"**{label}** ({unit}): set in Model inputs")
                    st.caption(note)
                    continue
                current_value = float(st.session_state.basis_values[key])
                edited_basis[key] = st.number_input(
                    f"{label} ({unit})",
                    value=current_value,
                    key=f"basis_{key}",
                    help=note,
                    format="%.8g",
                )
        apply_basis = st.form_submit_button("Apply basis", type="primary")
    if apply_basis:
        edited_basis["capacity"] = DEFAULTS["capacity"]
        edited_basis["urea_share"] = DEFAULTS["urea_share"]
        st.session_state.basis_values = edited_basis
        st.rerun()

st.info(plant.recommend(h2, solar, heat))
