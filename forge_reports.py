"""Shared result exports and calculation walkthrough for FORGE interfaces."""
from io import BytesIO

from matplotlib.figure import Figure


GREEN = "#17796f"
DARK = "#18332f"
PALE = "#e8f4f1"
LIGHT = "#d9eee9"
GREY = "#40534f"


def build_results_exports(plant, h2, solar, heat_recovery):
    """Return a one-page PDF and matching JPEG for the selected scenario."""
    rows = plant.table(h2, solar, heat_recovery)
    levers = plant.levers(h2, solar, heat_recovery)
    streams = plant.streams(h2, solar, heat_recovery)
    feed = plant.feedstock(h2, heat_recovery)
    total = rows[9]
    p = plant.p

    figure = Figure(figsize=(11.7, 8.3), dpi=160, facecolor="white")
    figure.text(0.04, 0.955, "FORGE-2026 | Ammonia & Urea Decarbonization Results",
                fontsize=17, fontweight="bold", color=DARK)
    figure.text(
        0.04,
        0.91,
        f"Capacity {p.capacity:,.0f} t NH3/yr  |  Urea share {p.urea_share * 100:.1f}%  |  "
        f"Green H2 {h2 * 100:.1f}%  |  Heat recovery {heat_recovery * 100:.0f}%  |  "
        f"Solar {solar * 100:.1f}%",
        fontsize=9,
        color=GREY,
    )
    figure.text(
        0.04,
        0.865,
        f"Total emissions: {total[1]:,.0f} -> {total[2]:,.0f} t CO2/yr  "
        f"({total[3]:+,.0f} avoided)  |  NH3 sold {feed['nh3_sold']:,.0f} t/yr  |  "
        f"Urea {feed['urea']:,.0f} t/yr  |  CO2 in urea {streams['urea_credit']:,.0f} t/yr",
        fontsize=9,
        color=DARK,
    )

    emissions_axis = figure.add_axes([0.04, 0.20, 0.60, 0.62])
    emissions_axis.axis("off")
    emission_data = [
        [
            name,
            f"{baseline:,.0f}" if isinstance(baseline, (int, float)) else baseline,
            f"{scenario:,.0f}" if isinstance(scenario, (int, float)) else scenario,
            f"{avoided:,.0f}" if isinstance(avoided, (int, float)) else avoided,
            f"{percent:.1f}%" if isinstance(percent, (int, float)) else percent,
        ]
        for name, baseline, scenario, avoided, percent in rows
    ]
    emissions_axis.set_title("Scope 1-3 emissions (t CO2/yr)", loc="left", pad=8,
                             fontsize=11, fontweight="bold", color=DARK)
    emission_table = emissions_axis.table(
        cellText=emission_data,
        colLabels=["Source", "Without", "With", "Avoided", "%"],
        colWidths=[0.49, 0.14, 0.14, 0.14, 0.09],
        cellLoc="right",
        colLoc="center",
        bbox=[0, 0, 1, 0.94],
    )
    emission_table.auto_set_font_size(False)
    emission_table.set_fontsize(7.3)
    emission_table.scale(1, 1.24)
    for column in range(5):
        cell = emission_table[(0, column)]
        cell.set_facecolor(GREEN)
        cell.get_text().set_color("white")
        cell.get_text().set_fontweight("bold")
    for row_index, row in enumerate(rows, start=1):
        row_color = DARK if row[0] == "TOTAL" else LIGHT if row[0].startswith("Scope") else "white"
        for column in range(5):
            cell = emission_table[(row_index, column)]
            cell.set_facecolor(row_color)
            cell.get_text().set_color("white" if row[0] == "TOTAL" else DARK)
            if row[0] == "TOTAL" or row[0].startswith("Scope"):
                cell.get_text().set_fontweight("bold")
        emission_table[(row_index, 0)].get_text().set_ha("left")

    mac_axis = figure.add_axes([0.68, 0.50, 0.28, 0.31])
    mac_axis.axis("off")
    mac_data = [
        [name, f"{cost:,.0f}", f"{avoided:,.0f}", f"{max(avoided, 0) * cost / 1e6:,.1f}"]
        for name, avoided, cost in levers
    ]
    mac_axis.set_title("MAC assessment", loc="left", pad=8,
                       fontsize=11, fontweight="bold", color=DARK)
    mac_table = mac_axis.table(
        cellText=mac_data,
        colLabels=["Lever", "PKR/t", "Avoided t/yr", "Cost PKR M/yr"],
        colWidths=[0.38, 0.19, 0.20, 0.23],
        cellLoc="right",
        colLoc="center",
        bbox=[0, 0, 1, 0.90],
    )
    mac_table.auto_set_font_size(False)
    mac_table.set_fontsize(7.1)
    mac_table.scale(1, 1.5)
    for column in range(4):
        cell = mac_table[(0, column)]
        cell.set_facecolor(GREEN)
        cell.get_text().set_color("white")
        cell.get_text().set_fontweight("bold")
    for row_index in range(1, len(mac_data) + 1):
        for column in range(4):
            mac_table[(row_index, column)].set_facecolor(PALE if row_index % 2 else "white")
            mac_table[(row_index, column)].get_text().set_color(DARK)
        mac_table[(row_index, 0)].get_text().set_ha("left")

    figure.text(
        0.68,
        0.39,
        "MAC compares each lever independently with the no-lever baseline. "
        "Annual cost is shown only for positive abatement.",
        fontsize=8,
        color=GREY,
        wrap=True,
    )
    figure.text(
        0.04,
        0.105,
        "The stoichiometric reference row is not included in totals. Model factors and "
        "assumptions are editable in Basis & equations.",
        fontsize=8,
        color=GREY,
    )

    pdf_buffer = BytesIO()
    jpg_buffer = BytesIO()
    figure.savefig(pdf_buffer, format="pdf", bbox_inches="tight", facecolor="white")
    figure.savefig(jpg_buffer, format="jpg", dpi=160, bbox_inches="tight", facecolor="white")
    return pdf_buffer.getvalue(), jpg_buffer.getvalue()


def methodology_sections():
    """Return the ordered formula guide, grouped by the model's calculation stages."""
    return [
        (
            "1. Plant emissions (Scope 1 and Scope 3)",
            [
                ("Gross SMR process CO2", "Capacity x SMR process CO2 factor x (1 - green H2 share)."),
                ("CO2 used in urea", "Minimum of (capacity x urea share x 44/34) and gross SMR process CO2. This caps the credit at the CO2 actually available."),
                ("Net SMR process CO2", "Gross SMR process CO2 - CO2 used in urea."),
                ("Gas combustion CO2 after interventions", "Capacity x combustion factor x (1 - green H2 share x combustion-tied-to-H2 share) x (1 - heat-recovery share)."),
                ("Supply-chain CO2 (Scope 3)", "Capacity x logistics CO2 factor. This is unchanged by the modeled levers."),
            ],
        ),
        (
            "2. Electricity emissions (Scope 2)",
            [
                ("Plant electricity demand", "Capacity x plant electricity use (MWh/t) x 1,000 / 365 = kWh/day."),
                ("Green H2 demand", "Capacity x H2 demand factor x green H2 blend share = tonnes H2/year."),
                ("Electrolyzer electricity", "H2 (t/year) x 1,000 kg/t x electrolyzer use (kWh/kg) / 1,000 = MWh/year; convert to kWh/day by multiplying by 1,000 / 365."),
                ("Day/night grid electricity", "The model splits both loads by daylight hours / 24. Solar offsets daytime demand only, shared between plant and electrolyzer in proportion to each daytime load. Nighttime demand remains grid-powered."),
                ("Scope 2 CO2 for each load", "Remaining grid electricity (kWh/day) x 365 / 1,000 x grid emissions factor (t CO2/MWh). Plant power and electrolyzer power are calculated separately."),
            ],
        ),
        (
            "3. Total emissions and table percentages",
            [
                ("Scope 1 total", "Combustion CO2 + net SMR process CO2."),
                ("Scope 2 total", "Plant electricity CO2 + electrolyzer electricity CO2."),
                ("Total emissions", "Scope 1 total + Scope 2 total + Scope 3 CO2."),
                ("Avoided emissions", "Without-intervention value - with-interventions value. A negative result means emissions increased."),
                ("% avoided", "(Without - with) / without x 100. If the without value is zero, the model reports 0%."),
                ("Stoichiometric reference", "Capacity x stoichiometric process factor; the same green H2 fraction is applied. This is a reference row and is not included in the total."),
            ],
        ),
        (
            "4. Feedstock and product balances",
            [
                ("Natural gas feed and fuel", "Corresponding gross SMR process CO2 or combustion CO2 / CO2 released per tonne of methane."),
                ("Process water", "Capacity x process-water factor x (1 - green H2 share)."),
                ("RO water", "Green H2 (tonnes/year) x 1,000 kg/tonne x RO water factor (kg/kg) / 1,000 kg/m3."),
                ("Nitrogen", "Ammonia capacity x nitrogen factor."),
                ("Ammonia sent to urea", "CO2 used in urea x 34/44. Urea output = CO2 used x 60/44; ammonia sold = capacity - ammonia sent to urea."),
                ("Electricity use", "Annual plant electricity + annual electrolyzer electricity."),
            ],
        ),
        (
            "5. Solar and electrolyzer sizing",
            [
                ("Solar-eligible combined load", "Plant kWh/day + electrolyzer kWh/day. Achievable solar share is the lower of the selected share and the daylight cap."),
                ("Solar energy target", "Combined daily load x achievable solar share."),
                ("PV system size", "Solar energy target / (effective daylight hours x system performance ratio) = kWp."),
                ("Panel count", "PV system size (kWp) x 1,000 / panel rating (W)."),
                ("Land and installed cost", "Land = system size (MW) x acres/MW. Cost = system size (kW) x installed PKR/W."),
                ("Electrolyzer size and cost", "Electrolyzer kWh/day / operating hours/day = kW. Installed cost = kW x installed PKR/kW."),
            ],
        ),
        (
            "6. Abatement cost and recommendation",
            [
                ("Lever-specific avoided CO2", "For each lever, compare total emissions at its selected setting alone against the no-intervention baseline."),
                ("MAC cost", "Each lever's configured PKR per tonne of CO2 avoided; the chart orders levers by this unit cost. Costs are basis assumptions, not dynamically calculated capital costs."),
                ("Annual lever cost on cards", "Positive tonnes avoided x PKR per tonne / 1,000,000 = PKR million/year. No annual cost is shown when a lever does not avoid CO2."),
                ("Recommendation", "Compares total modeled emissions, ranks active levers by unit cost and tonnes avoided, and warns if a lever used on its own increases emissions."),
            ],
        ),
        (
            "Important assumptions",
            [
                ("Model boundary", "These are simplified, editable model calculations. Basis values marked as assumptions should be replaced with plant-specific data before using results for decisions."),
                ("Solar and green H2", "Solar is capped by the daylight share and is allocated to both power loads during daylight; green H2 electrolyzer demand outside solar supply remains grid emissions."),
                ("Urea and reference rows", "CO2 used to make urea is treated as a process-emissions credit. The stoichiometric process row is a comparison only and is excluded from totals."),
            ],
        ),
    ]