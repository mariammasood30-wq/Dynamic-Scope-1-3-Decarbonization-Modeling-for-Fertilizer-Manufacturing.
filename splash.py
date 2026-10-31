import base64
import logging
import mimetypes
from pathlib import Path

import streamlit as st


_ASSET_NAMES = (
    "splash_cover.png",
    "bg_plant.jpg",
    "bg_plant_clean.jpg",
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
    """Show a two-screen, one-time DecarbNH3 welcome flow."""
    if st.session_state.get("splash_done"):
        return

    if "splash_screen" not in st.session_state:
        st.session_state.splash_screen = 1

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
    cover_image = assets.get("splash_cover.png")
    if cover_image is None:
        raise FileNotFoundError(
            f"Required splash cover image is missing: {asset_directory / 'splash_cover.png'}"
        )
    background_image = assets.get("bg_plant_clean.jpg") or assets.get("bg_plant.jpg")
    background_layer = (
        f"linear-gradient(135deg, rgba(12, 112, 103, 0.78), "
        f"rgba(4, 62, 57, 0.48)), url('{background_image}')"
        if background_image
        else "linear-gradient(135deg, #0e796c 0%, #06373a 100%)"
    )

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
    .splash-cover {
        position: fixed;
        inset: 0;
        z-index: 0;
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        object-position: center;
    }
    .splash-content {
        position: relative;
        z-index: 3;
        width: min(1180px, 92vw);
        margin: 0 auto;
        text-align: center;
    }
    .splash-content-two {
        width: min(760px, 88vw);
        max-height: calc(100vh - 8rem);
        overflow-y: auto;
        padding: 0.5rem 1rem 1rem;
    }
    .splash-title {
        margin: 0;
        color: #f5fbfa;
        font: 700 clamp(2.7rem, 3vw, 5.1rem)/0.96 "Segoe UI", Arial, sans-serif;
        letter-spacing: -0.055em;
        text-shadow: 0 8px 24px rgba(0, 0, 0, 0.14);
    }
    .splash-tagline {
        margin: 0;
        color: #ecfdf7;
        font-size: clamp(0.78rem, 1vw, 1.08rem);
        font-weight: 600;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }
    .splash-credit {
        margin: 0;
        color: rgba(241, 252, 248, 0.88);
        font-size: 0.82rem;
        font-weight: 500;
        letter-spacing: 0.04em;
    }
    .splash-section-title {
        margin: 1.4rem 0 0.5rem;
        color: #dffaf5;
        font-size: 1.2rem;
        font-weight: 700;
    }
    .splash-feature-list, .splash-steps-list {
        max-width: 680px;
        margin: 0.45rem auto 0;
        padding-left: 1.5rem;
        color: #f4fbfa;
        font-size: clamp(1rem, 1.4vw, 1.15rem);
        line-height: 1.55;
        text-align: left;
    }
    .splash-feature-list li, .splash-steps-list li {
        margin: 0.35rem 0;
    }
    .st-key-splash-controls {
        position: fixed;
        bottom: 2rem;
        left: 50%;
        z-index: 5;
        width: min(360px, 86vw);
        padding: 0.4rem 0.8rem 0;
        transform: translateX(-50%);
        text-align: center;
    }
    .st-key-splash-controls-cover {
        position: fixed;
        right: 1.5rem;
        bottom: 1.5rem;
        z-index: 5;
        width: min(210px, 42vw);
        padding: 0.4rem 0.8rem 0;
        text-align: center;
    }
    .st-key-splash-controls [data-testid="stVerticalBlock"],
    .st-key-splash-controls-cover [data-testid="stVerticalBlock"] {
        gap: 0.35rem;
    }
    .st-key-splash-controls [data-testid="stButton"] button,
    .st-key-splash-controls-cover [data-testid="stButton"] button {
        min-height: 3.2rem;
        border: 1px solid rgba(138, 235, 215, 0.95);
        border-radius: 12px;
        background: linear-gradient(180deg, #1d8a78 0%, #136f62 100%);
        color: #fff;
        font-size: 1.08rem;
        font-weight: 800;
        box-shadow: 0 8px 18px rgba(8, 61, 56, 0.22);
        transition: background 160ms ease, transform 160ms ease;
    }
    .st-key-splash-controls [data-testid="stButton"] button:hover,
    .st-key-splash-controls-cover [data-testid="stButton"] button:hover {
        border-color: rgba(190, 255, 244, 1);
        background: linear-gradient(180deg, #1f9b84 0%, #147a66 100%);
        color: #fff;
        transform: translateY(-1px);
    }
    @keyframes splash-fade-in {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @media (max-width: 899px) {
        .splash-content { width: min(700px, 92vw); }
        .splash-content-two { width: min(700px, 92vw); }
        .st-key-splash-controls { bottom: 1.2rem; }
    }
    @media (max-width: 600px) {
        [data-testid="stMainBlockContainer"] { padding: 0.5rem !important; }
        .st-key-splash-screen { padding: 1rem; }
        .splash-content { width: 100%; }
        .splash-title { font-size: clamp(2.6rem, 13vw, 3.4rem); }
        .splash-content-two { width: 100%; padding: 0.25rem 0.5rem 0.75rem; }
        .splash-section-title { margin-top: 1rem; }
        .splash-feature-list, .splash-steps-list { font-size: 0.92rem; }
        .st-key-splash-controls { bottom: 0.6rem; width: 94vw; }
        .st-key-splash-controls-cover {
            right: 0.5rem;
            bottom: 0.5rem;
            width: min(180px, 48vw);
        }
    }
    </style>
    """.replace("__BACKGROUND__", background_layer),
        unsafe_allow_html=True,
    )

    screen = st.session_state.splash_screen
    with st.container(key="splash-screen", border=False):
        if screen == 1:
            st.markdown(
                f"""
                <img class="splash-cover" src="{cover_image}" alt="DecarbNH3 industrial ammonia plant cover">
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <main class="splash-content splash-content-two">
                    <h1 class="splash-title">What this app does</h1>
                    <ul class="splash-feature-list">
                        <li>Models ammonia-plant emissions across Scopes 1, 2 and 3.</li>
                        <li>Compares green hydrogen, waste-heat recovery and solar PV options.</li>
                        <li>Estimates feedstock, electricity, water needs and abatement costs.</li>
                    </ul>
                    <h2 class="splash-section-title">How to use it</h2>
                    <ol class="splash-steps-list">
                        <li>Enter plant capacity and urea share in the input panel.</li>
                        <li>Adjust the hydrogen, heat-recovery and solar controls.</li>
                        <li>Explore the result tabs and export your results if needed.</li>
                    </ol>
                </main>
                """,
                unsafe_allow_html=True,
            )

    controls_key = "splash-controls-cover" if screen == 1 else "splash-controls"
    with st.container(key=controls_key, border=False):
        if screen == 1:
            if st.button(
                "Continue",
                key="continue_splash_button",
                type="primary",
                width="stretch",
            ):
                st.session_state.splash_screen = 2
                st.rerun()
        else:
            back_col, launch_col = st.columns(2, gap="small")
            if back_col.button("Back", key="back_splash_button", width="stretch"):
                st.session_state.splash_screen = 1
                st.rerun()
            if launch_col.button(
                "Launch DecarbNH3",
                key="launch_decarbnh3_button",
                type="primary",
                width="stretch",
            ):
                st.session_state.splash_done = True
                st.rerun()
