import base64
import logging
import mimetypes
import time
from pathlib import Path

import streamlit as st


_DISPLAY_SECONDS = 10
_STATUS_MESSAGES = (
    "Loading feedstock data...",
    "Initializing Scope 1-3 engine...",
    "Preparing MAC curve module...",
)
_ASSET_NAMES = (
    "bg_plant.jpg",
    "shot_mac.png",
    "shot_scope_diagram.png",
    "shot_scope_table.png",
)
_LOGGER = logging.getLogger(__name__)


@st.cache_data(show_spinner=False)
def _load_splash_assets(
    asset_directory: str,
    asset_manifest: tuple[tuple[str, int, int], ...],
) -> dict[str, str]:
    """Load and cache image data URIs for the splash screen."""
    assets: dict[str, str] = {}
    root = Path(asset_directory)

    for name, _, _ in asset_manifest:
        image_path = root / name
        if not image_path.is_file():
            _LOGGER.warning("Splash artwork is missing: %s", image_path)
            continue

        mime_type = mimetypes.guess_type(image_path.name)[0]
        if mime_type is None or not mime_type.startswith("image/"):
            raise ValueError(f"Unsupported splash image type: {image_path}")

        encoded_image = base64.b64encode(image_path.read_bytes()).decode("ascii")
        assets[name] = f"data:{mime_type};base64,{encoded_image}"

    return assets


def show_splash():
    """Show an animated, one-time DecarbNH3 welcome screen."""
    if st.session_state.get("splash_done"):
        return

    if "splash_started_at_v2" not in st.session_state:
        st.session_state.splash_started_at_v2 = time.time()

    asset_directory = Path(__file__).parent / "assets"
    asset_manifest = tuple(
        (
            name,
            (asset_directory / name).stat().st_mtime_ns,
            (asset_directory / name).stat().st_size,
        )
        if (asset_directory / name).is_file()
        else (name, 0, 0)
        for name in _ASSET_NAMES
    )
    assets = _load_splash_assets(str(asset_directory), asset_manifest)
    background_image = assets.get("bg_plant.jpg")
    background_layer = (
        f"linear-gradient(135deg, rgba(15, 92, 82, 0.78), "
        f"rgba(7, 48, 53, 0.84)), url('{background_image}')"
        if background_image
        else "linear-gradient(135deg, #0f5c52 0%, #073035 100%)"
    )

    screenshots = []
    screenshot_specs = (
        ("shot_mac.png", "MAC curve preview", "splash-shot splash-shot-mac"),
        (
            "shot_scope_diagram.png",
            "Scope emissions diagram preview",
            "splash-shot splash-shot-diagram",
        ),
        (
            "shot_scope_table.png",
            "Scope emissions table preview",
            "splash-shot splash-shot-table",
        ),
    )
    for name, alt_text, classes in screenshot_specs:
        if name in assets:
            screenshots.append(
                f'<img class="{classes}" src="{assets[name]}" alt="{alt_text}">'
            )
    screenshot_markup = "\n".join(screenshots)
    missing_assets = [name for name in _ASSET_NAMES if name not in assets]

    st.markdown(
        """
    <style>
    [data-testid="stHeader"], [data-testid="stToolbar"],
    [data-testid="stDecoration"], footer, [data-testid="stSidebar"],
    [data-testid="stStatusWidget"] {
        display: none !important;
    }
    [data-testid="stAppViewContainer"] {
        background: __BACKGROUND__ center center / cover no-repeat fixed !important;
        color: #fff;
        font-family: Inter, "Segoe UI", Arial, sans-serif !important;
    }
    html, body, .stApp, [data-testid="stAppViewContainer"],
    section[data-testid="stMain"] {
        height: 100vh;
        max-height: 100vh;
        overflow: hidden !important;
    }
    [data-testid="stMainBlockContainer"] {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        max-width: none;
        min-height: 100vh;
        padding: 1.25rem !important;
    }
    .st-key-splash-screen {
        position: fixed;
        inset: 0;
        z-index: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        box-sizing: border-box;
        width: 100vw;
        height: 100vh;
        padding: 2rem;
        overflow: hidden;
        animation: splash-fade-in 900ms ease-out both;
    }
    .splash-content {
        position: relative;
        z-index: 3;
        width: min(760px, 84vw);
        margin: 0 auto;
        text-align: center;
    }
    .splash-title {
        margin: 0;
        color: #fff;
        font: 800 clamp(3rem, 6vw, 4rem)/1.05 Inter, "Segoe UI", Arial, sans-serif;
        letter-spacing: -0.035em;
        text-shadow: 0 2px 20px rgba(0, 0, 0, 0.16);
    }
    .splash-tagline {
        margin: 0.7rem 0 0;
        color: #a9e3da;
        font-size: clamp(1.05rem, 2vw, 1.35rem);
        font-weight: 600;
        letter-spacing: 0.015em;
    }
    .splash-description {
        max-width: 700px;
        margin: 1.3rem auto 0;
        color: #f2fbf9;
        font-size: clamp(1rem, 1.4vw, 1.08rem);
        line-height: 1.55;
        text-wrap: balance;
    }
    .splash-chips, .splash-steps {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-wrap: wrap;
        gap: 0.65rem;
    }
    .splash-chips {
        margin-top: 1.5rem;
    }
    .splash-chip {
        padding: 0.48rem 0.9rem;
        color: #e8faf6;
        background: rgba(235, 255, 250, 0.12);
        border: 1px solid rgba(210, 250, 241, 0.55);
        border-radius: 999px;
        font-size: 0.92rem;
        font-weight: 600;
        letter-spacing: 0.01em;
        backdrop-filter: blur(8px);
    }
    .splash-steps {
        margin-top: 1.65rem;
        gap: 0.45rem;
    }
    .splash-step {
        padding: 0.58rem 0.86rem;
        color: #f7fffd;
        background: rgba(3, 42, 43, 0.34);
        border: 1px solid rgba(202, 241, 233, 0.3);
        border-radius: 9px;
        font-size: 0.9rem;
        font-weight: 600;
        white-space: nowrap;
    }
    .splash-arrow {
        color: #b2e8de;
        font-size: 1.1rem;
        font-weight: 700;
    }
    .splash-footer {
        position: absolute;
        right: 1rem;
        bottom: 1rem;
        left: 1rem;
        z-index: 4;
        color: rgba(239, 251, 248, 0.86);
        font-size: 0.875rem;
        text-align: center;
    }
    .splash-shot {
        position: absolute;
        z-index: 2;
        display: block;
        width: clamp(150px, 18vw, 260px);
        height: auto;
        padding: 7px;
        background: #fff;
        border: 1px solid rgba(255, 255, 255, 0.92);
        border-radius: 12px;
        box-shadow: 0 18px 46px rgba(0, 20, 23, 0.34);
        animation: splash-float 6s ease-in-out infinite;
    }
    .splash-shot-mac {
        top: 24%;
        left: 5.5%;
        transform: rotate(-4deg);
    }
    .splash-shot-diagram {
        top: 51%;
        left: 9%;
        transform: rotate(3deg);
        animation-delay: -2s;
    }
    .splash-shot-table {
        top: 36%;
        right: 6%;
        transform: rotate(-3deg);
        animation-delay: -1s;
    }
    .st-key-splash-controls {
        position: fixed;
        bottom: 3.1rem;
        left: 50%;
        z-index: 5;
        width: min(480px, 86vw);
        padding: 0.6rem 0.8rem 0;
        transform: translateX(-50%);
        text-align: center;
    }
    .st-key-splash-controls [data-testid="stVerticalBlock"] {
        gap: 0.35rem;
    }
    .st-key-splash-controls [data-testid="stProgress"] {
        padding: 0;
    }
    .st-key-splash-controls [data-testid="stProgress"] > div > div {
        background: #43c4ad;
    }
    .st-key-splash-controls [data-testid="stButton"] button {
        min-height: 3.1rem;
        border: 1px solid #6be0ca;
        border-radius: 12px;
        background: #1b7a6b;
        color: #fff;
        font-size: 1rem;
        font-weight: 750;
        transition: background 160ms ease, transform 160ms ease;
    }
    .st-key-splash-controls [data-testid="stButton"] button:hover {
        border-color: #9af0df;
        background: #21927f;
        color: #fff;
        transform: translateY(-1px);
    }
    .st-key-splash-controls .st-key-skip-splash-button button {
        min-height: 2.5rem;
        border: 0;
        background: transparent;
        color: #e9f8f5;
        font-size: 0.9rem;
        font-weight: 600;
        text-decoration: underline;
        text-underline-offset: 3px;
    }
    .splash-status {
        min-height: 1.25rem;
        margin: 0;
        color: rgba(242, 251, 249, 0.92);
        font-size: 0.9rem;
        font-weight: 600;
        text-align: center;
    }
    @keyframes splash-fade-in {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes splash-float {
        0%, 100% { margin-top: 0; }
        50% { margin-top: -12px; }
    }
    @media (max-width: 899px) {
        .splash-shot { display: none !important; }
        .splash-content { width: min(700px, 92vw); }
        .st-key-splash-controls { bottom: 2.8rem; }
    }
    @media (max-width: 600px) {
        [data-testid="stMainBlockContainer"] { padding: 0.5rem !important; }
        .st-key-splash-screen { padding: 1rem; }
        .splash-content { width: 100%; }
        .splash-title { font-size: clamp(2.6rem, 13vw, 3.4rem); }
        .splash-description { margin-top: 0.9rem; font-size: 1rem; }
        .splash-chips { margin-top: 1rem; gap: 0.45rem; }
        .splash-chip { padding: 0.42rem 0.68rem; font-size: 0.875rem; }
        .splash-steps { margin-top: 1rem; gap: 0.4rem; }
        .splash-step { padding: 0.45rem 0.58rem; font-size: 0.875rem; }
        .splash-footer { bottom: 0.5rem; font-size: 0.875rem; }
        .st-key-splash-controls { bottom: 2.3rem; width: 92vw; }
    }
    </style>
    """.replace("__BACKGROUND__", background_layer),
        unsafe_allow_html=True,
    )

    @st.fragment(run_every="1s")
    def render_splash():
        elapsed = time.time() - st.session_state.splash_started_at_v2
        if elapsed >= _DISPLAY_SECONDS:
            st.session_state.splash_done = True
            st.rerun(scope="app")

        progress = min(elapsed / _DISPLAY_SECONDS, 1.0)
        if missing_assets:
            status = "Add the requested images to assets\\ to enable the full splash artwork."
        else:
            status = _STATUS_MESSAGES[
                min(int(elapsed // (_DISPLAY_SECONDS / len(_STATUS_MESSAGES))), len(_STATUS_MESSAGES) - 1)
            ]

        with st.container(key="splash-screen", border=False):
            st.markdown(
                f"""
                {screenshot_markup}
                <main class="splash-content">
                    <h1 class="splash-title">DecarbNH3</h1>
                    <p class="splash-tagline">Ammonia &amp; Urea Decarbonization Modeller</p>
                    <p class="splash-description">Model Scope 1-3 emissions and compare green hydrogen, heat recovery and solar PV for ammonia and urea plants.</p>
                    <div class="splash-chips">
                        <span class="splash-chip">Green H2</span>
                        <span class="splash-chip">Heat recovery</span>
                        <span class="splash-chip">Solar PV</span>
                    </div>
                    <div class="splash-steps">
                        <span class="splash-step">1&nbsp; Enter capacity</span>
                        <span class="splash-arrow" aria-hidden="true">→</span>
                        <span class="splash-step">2&nbsp; Set levers</span>
                        <span class="splash-arrow" aria-hidden="true">→</span>
                        <span class="splash-step">3&nbsp; Run model</span>
                        <span class="splash-arrow" aria-hidden="true">→</span>
                        <span class="splash-step">4&nbsp; Explore tabs</span>
                    </div>
                </main>
                <div class="splash-footer">v1.0 - Created by Mariam Masood, Dept. of Chemical Engineering, UET Lahore</div>
                """,
                unsafe_allow_html=True,
            )

        with st.container(key="splash-controls", border=False):
            st.markdown(f"<p class='splash-status'>{status}</p>", unsafe_allow_html=True)
            st.progress(progress)
            launch_col, skip_col = st.columns([3, 1], vertical_alignment="center")
            with launch_col:
                launch = st.button(
                    "Launch DecarbNH3",
                    key="launch_decarbnh3_button",
                    type="primary",
                    width="stretch",
                )
            with skip_col:
                skip = st.button(
                    "Skip",
                    key="skip_splash_button",
                    width="stretch",
                )

        if launch or skip:
            st.session_state.splash_done = True
            st.rerun(scope="app")

    render_splash()
