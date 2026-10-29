import time

import streamlit as st


_DISPLAY_SECONDS = 15
_LOADING_MESSAGES = (
    "Loading feedstock data...",
    "Initializing Scope 1-3 engine...",
    "Preparing MAC curve module...",
)


def show_splash():
    """Render a responsive, one-time introductory splash screen."""
    if st.session_state.get("splash_done"):
        return

    if "splash_started_at" not in st.session_state:
        st.session_state.splash_started_at = time.time()

    st.markdown(
        """
        <style>
        [data-testid="stHeader"], [data-testid="stToolbar"],
        [data-testid="stDecoration"], footer,
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #f4fbfa 0%, #eef9f7 100%) !important;
        }
        [data-testid="stMainBlockContainer"] {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 1.5rem !important;
        }
        .st-key-splash-card {
            width: min(920px, 92vw);
            margin: auto;
            padding: clamp(1.3rem, 3vw, 2.5rem);
            background: rgba(255,255,255,0.97);
            border: 1px solid #dfece9;
            border-radius: 24px;
            box-shadow: 0 22px 60px rgba(16, 77, 68, 0.12);
            text-align: center;
        }
        .splash-brand {
            margin: 0;
            color: #0f6d66;
            font: 800 clamp(2.3rem, 5vw, 4.2rem)/1.1 "Segoe UI", Arial, sans-serif;
            letter-spacing: 0.06em;
        }
        .splash-tagline {
            margin-top: 0.55rem;
            color: #214f4a;
            font-size: clamp(0.95rem, 2vw, 1.4rem);
            font-weight: 600;
        }
        .splash-meta {
            margin-top: 0.7rem;
            color: #1d706b;
            font-size: 0.9rem;
            font-weight: 700;
        }
        .splash-credit {
            margin-top: 0.4rem;
            color: #435f5d;
            font-size: 0.82rem;
        }
        .splash-divider {
            width: 92%;
            height: 1px;
            margin: 1.3rem auto;
            background: linear-gradient(90deg, transparent, #bfe2dc 20%, #57b6a9 55%, #bfe2dc 80%, transparent);
        }
        .splash-section {
            margin-top: 1rem;
            text-align: left;
        }
        .splash-section h3 {
            margin: 0 0 0.65rem;
            color: #124d48;
            font-size: 1.05rem;
            font-weight: 800;
            text-align: center;
        }
        .splash-feature-list {
            display: grid;
            gap: 0.4rem;
            margin: 0;
            padding: 0;
            color: #2f4f4b;
            font-size: 0.9rem;
            list-style: none;
            text-align: center;
        }
        .splash-feature-list li::before {
            content: "• ";
            color: #0f6d66;
            font-weight: 800;
        }
        .splash-steps {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 0.7rem;
        }
        .splash-step {
            flex: 1 1 170px;
            max-width: 220px;
            min-height: 105px;
            padding: 0.75rem;
            background: #f7fbfa;
            border: 1px solid #dfece9;
            border-radius: 14px;
            text-align: left;
        }
        .splash-step-number {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.6rem;
            height: 1.6rem;
            margin-bottom: 0.4rem;
            border-radius: 50%;
            background: #0f6d66;
            color: white;
            font-size: 0.8rem;
            font-weight: 700;
        }
        .splash-step p {
            margin: 0;
            color: #264a48;
            font-size: 0.8rem;
            line-height: 1.4;
        }
        .splash-progress-title {
            margin: 0.8rem 0 0.45rem;
            color: #155d57;
            font-size: 0.84rem;
            font-weight: 700;
        }
        .splash-loading {
            min-height: 1.2rem;
            margin-top: 0.2rem;
            color: #1e544e;
            font-size: 0.88rem;
            font-weight: 600;
            text-align: center;
        }
        .st-key-splash-card [data-testid="stProgress"] > div > div {
            background-color: #0f6d66;
        }
        .st-key-splash-card [data-testid="stButton"] button {
            min-height: 2.6rem;
            border-radius: 10px;
            font-weight: 700;
        }
        @media (max-width: 640px) {
            [data-testid="stMainBlockContainer"] { padding: 0.75rem !important; }
            .st-key-splash-card { padding: 1.1rem 0.85rem; border-radius: 18px; }
            .splash-steps { flex-direction: column; align-items: stretch; }
            .splash-step { max-width: none; min-height: auto; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    @st.fragment(run_every="1s")
    def render_splash():
        elapsed = time.time() - st.session_state.splash_started_at
        if elapsed >= _DISPLAY_SECONDS:
            st.session_state.splash_done = True
            st.rerun(scope="app")

        message_index = min(int(elapsed // 5), len(_LOADING_MESSAGES) - 1)
        progress = min(elapsed / _DISPLAY_SECONDS, 1.0)

        with st.container(key="splash-card"):
            st.markdown(
                """
                <h1 class="splash-brand">DecarbNH3</h1>
                <div class="splash-tagline">Ammonia &amp; Urea Decarbonization Modeller</div>
                <div class="splash-meta">v1.0</div>
                <div class="splash-credit">programmed by Mariam Masood, mariam.masood30@gmail.com</div>
                <div class="splash-divider"></div>
                <div class="splash-section">
                    <h3>What this app does</h3>
                    <ul class="splash-feature-list">
                        <li>Models Scope 1, 2 and 3 emissions of an ammonia-urea plant.</li>
                        <li>Tests three decarbonization levers: green hydrogen blending, heat recovery, and solar PV.</li>
                        <li>Shows results as a Scope 1-3 table, Scope diagram, MAC curve, and upgrading cost estimate.</li>
                        <li>Intended for engineers, students and researchers.</li>
                    </ul>
                </div>
                <div class="splash-section">
                    <h3>How to use</h3>
                    <div class="splash-steps">
                        <div class="splash-step"><div class="splash-step-number">1</div><p>Enter ammonia capacity (t NH3/yr) and urea share (%) in the left panel.</p></div>
                        <div class="splash-step"><div class="splash-step-number">2</div><p>Set the levers: green hydrogen blending, heat recovery, and solar PV.</p></div>
                        <div class="splash-step"><div class="splash-step-number">3</div><p>Click "Run model".</p></div>
                        <div class="splash-step"><div class="splash-step-number">4</div><p>Explore the tabs: Feedstock, Scope 1-3 table, Scope diagram, MAC curve, Upgrading cost, Basis &amp; equations. Use Results and Methodology in the left panel for a summary and assumptions.</p></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                "<div class='splash-progress-title'>Initializing app</div>",
                unsafe_allow_html=True,
            )
            st.progress(progress)
            st.markdown(
                f"<div class='splash-loading'>{_LOADING_MESSAGES[message_index]}</div>",
                unsafe_allow_html=True,
            )
            skip_col, enter_col = st.columns(2)
            with skip_col:
                skip = st.button("Skip intro", key="skip_intro_button", use_container_width=True)
            with enter_col:
                enter = st.button("Enter app", key="enter_app_button", type="primary", use_container_width=True)

        if skip or enter:
            st.session_state.splash_done = True
            st.rerun(scope="app")

    render_splash()
