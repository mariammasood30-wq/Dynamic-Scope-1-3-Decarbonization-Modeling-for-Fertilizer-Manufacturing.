from dataclasses import fields

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from forge_decarb import Params, Plant


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
    .stApp {{ background-color: #f2f6f5; }}
    [data-testid="stHeader"] {{ background: transparent; }}
    [data-testid="stMainBlockContainer"] {{
        max-width: 1600px; padding-top: .7rem; padding-bottom: .5rem;
    }}
    [data-testid="stSidebar"] {{
        background: #f2f6f5; min-width: 300px; max-width: 300px;
    }}
    [data-testid="stSidebar"] > div:first-child {{ padding-top: .65rem; }}
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
        gap: .45rem;
    }}
    [data-baseweb="tab-list"] {{
        gap: .25rem; justify-content: center; border-bottom: 0; padding-bottom: .5rem;
    }}
    [data-baseweb="tab"] {{
        color: {DARK}; font-weight: 700; border-radius: 8px; height: 2.1rem;
        padding: 0 .65rem;
    }}
    [aria-selected="true"][data-baseweb="tab"] {{
        background: #d9eee9; color: {DARK};
    }}
    [data-baseweb="tab-panel"] {{
        background: white; border: 1px solid #dce7e4; border-radius: 0 10px 10px 10px;
        padding: .75rem .85rem; min-height: 68vh;
    }}
    [data-testid="stTabs"] > div:first-child {{
        overflow-x: auto; flex-wrap: nowrap;
    }}
    [data-testid="stSidebar"] label p {{
        color: {DARK}; font-weight: 650; font-size: .84rem;
    }}
    [data-testid="stCaptionContainer"] p {{
        color: {GREY}; font-size: .72rem; line-height: 1.3;
    }}
    div[data-testid="stDataFrame"] {{
        border: 1px solid #dce7e4; border-radius: 6px; overflow: hidden;
    }}
    div[data-testid="stAlert"] {{
        border: 0; background: {PALE}; color: {DARK}; border-radius: 9px;
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
if st.sidebar.button("Reset model", use_container_width=True):
    st.session_state.basis_values = DEFAULTS.copy()
    for group_name, basis_rows in BASIS_GROUPS:
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
    st.rerun()

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
h2_pct = st.sidebar.slider(
    "Green hydrogen blending (%)",
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

st.sidebar.caption(
    f"Plant only: {plant_load_kwh_day:,.0f} kWh/day (fixed)\n\n"
    f"Plant + electrolyzer: {combined_load_kwh_day:,.0f} kWh/day"
)
h2_t, ro_water = plant_for_controls.h2_water(h2_pct / 100)
h2_mwh, h2_kwh_day = plant_for_controls.h2_electricity(h2_pct / 100)
st.sidebar.caption(
    f"Green H2: {h2_t:,.0f} t/yr  |  RO water: {ro_water:,.0f} m³/yr\n\n"
    f"Electrolysis electricity: {h2_mwh:,.0f} MWh/yr ({h2_kwh_day:,.0f} kWh/day)"
)
heat_pct = st.sidebar.slider(
    "Heat recovery (combustion) (%)",
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
solar_kwh_day = st.sidebar.slider(
    "Solar PV (kWh/day)",
    min_value=0.0,
    max_value=solar_slider_max,
    step=max(solar_slider_max / 100, 1.0),
    key="solar_input",
    help="Daily solar generation offsets electricity demand. Solar is daylight-only and capped by the no-battery maximum.",
)
st.sidebar.caption(
    f"Solar available in daylight only (~{params_for_controls.daylight_hours:g} h/day); "
    f"slider capped at {solar_max_kwh_day:,.0f} kWh/day "
    "(maximum deliverable plant + electrolyzer load without battery storage)."
)
st.sidebar.button("Run model", type="primary", use_container_width=True)

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
    st.dataframe(
        feed_style,
        hide_index=True,
        use_container_width=True,
    )
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
    st.dataframe(
        pd.DataFrame(table_rows),
        hide_index=True,
        use_container_width=True,
        column_config={
            "Without (t CO2/yr)": st.column_config.NumberColumn(format="localized"),
            "With (t CO2/yr)": st.column_config.NumberColumn(format="localized"),
            "Avoided (t CO2/yr)": st.column_config.NumberColumn(format="localized"),
            "% avoided": st.column_config.NumberColumn(format="%.1f%%"),
        },
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

st.divider()
st.info(plant.recommend(h2, solar, heat))
st.caption(
    f"Plant-only electricity: {plant.total_electricity_kwh_day():,.0f} kWh/day. "
    f"Plant + electrolyzer: {combined_load_kwh_day:,.0f} kWh/day. "
    "Model factors marked as assumptions are placeholders; replace them with "
    "site-specific or literature-backed values."
)
