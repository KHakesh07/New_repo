import streamlit as st
from streamlit_option_menu import option_menu
from app_pages.overview import overview_page
from app_pages.Login import simple_login
from app_pages.sidebar import render_sidebar  # Import the new sidebar component
from visualizations.OverallAnalysis import vis
from common import create_database
import requests
import random
import streamlit.components.v1 as components
st.set_page_config(layout="wide")

# Custom CSS for overall styling and animations
st.markdown("""
<style>
    .stApp {
        background-color: #1a1a1a;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #2b2b2b;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4e8cff !important;
    }
    
    /* Hero Section Styling */
    .hero-section {
        background-image: url('https://source.unsplash.com/1600x900/?nature,environment');
        background-size: cover;
        background-position: center;
        padding: 100px 20px;
        text-align: center;
        color: #ffffff;
        min-height: 80vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        overflow: hidden;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px #000;
        animation: fadeInDown 1s ease-in-out;
    }
    .hero-subtitle {
        font-size: 1.5rem;
        margin-top: 10px;
        animation: fadeInUp 1s ease-in-out;
    }
    .cta-button {
        margin-top: 30px;
        background-color: #4e8cff;
        color: #fff;
        padding: 15px 30px;
        border: none;
        border-radius: 8px;
        font-size: 1.2rem;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .cta-button:hover {
        background-color: #367bd8;
    }
    @keyframes fadeInDown {
      from { opacity: 0; transform: translateY(-20px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeInUp {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @media only screen and (max-width: 768px) {
        .hero-title { font-size: 2.5rem; }
        .hero-subtitle { font-size: 1.2rem; }
        .cta-button { padding: 10px 20px; font-size: 1rem; }
    }
    /* Container for the interactive widgets */
    .widget-container {
        background: rgba(0, 0, 0, 0.6);
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
try:
    create_database()
except Exception as e:
    st.error(f"Failed to initialize database: {e}")
    st.stop()

# ------------------------------
# Helper function to load Lottie animations
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# ------------------------------
# Render Particle.js Background Animation via an HTML component
def render_particle_background():
    particle_html = """
    <div id="particles-js" style="position:absolute; width:100%; height:100%; top:0; left:0; z-index:0;"></div>
    <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
    <script>
      particlesJS("particles-js", {
        "particles": {
          "number": { "value": 80 },
          "color": { "value": "#ffffff" },
          "shape": {
            "type": "circle"
          },
          "opacity": {
            "value": 0.5,
            "random": true
          },
          "size": {
            "value": 3,
            "random": true
          },
          "line_linked": {
            "enable": false
          },
          "move": {
            "enable": true,
            "speed": 1,
            "direction": "none",
            "random": true,
            "out_mode": "out"
          }
        },
        "interactivity": {
          "detect_on": "canvas",
          "events": {
            "onhover": {
              "enable": true,
              "mode": "repulse"
            },
            "onclick": {
              "enable": true,
              "mode": "push"
            }
          }
        }
      });
    </script>
    """
    # The particles background is added as an HTML component and set behind other elements.
    components.html(particle_html, height=0, width=0)

# ------------------------------
# Function to render the enhanced pre-login landing page
def render_landing_page():
    # Render particle animation in the background
    render_particle_background()

    # Hero section with interactive CTA
    st.markdown("""
        <div class="hero-section">
            <div class="hero-title">Welcome to the Carbon Emission Dashboard</div>
            <div class="hero-subtitle">Calculate, analyze, and reduce your event's carbon footprint</div>
            <button class="cta-button" id="login-btn">Login to Begin</button>
        </div>
        <script>
            const btn = window.parent.document.getElementById("login-btn");
            if(btn){
                btn.addEventListener("click", () => {
                    window.parent.document.querySelector('[data-testid="stSidebar"]').scrollIntoView({ behavior: 'smooth' });
                });
            }
        </script>
    """, unsafe_allow_html=True)
    
    # Short video loop demonstrating climate impact (alt text provided for accessibility)
    st.markdown("### Climate Impact Preview")
    st.components.v1.html("""
                          <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 8px;">
                          <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
                          src="https://www.youtube.com/embed/-gejkWj3K24?autoplay=0&mute=0&loop=0&controls=1" 
                          frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                          allowfullscreen title="Climate Change Impact Visualization"></iframe>
                          </div>
                          """, height=400) # Replace with your video URL
    # Accessibility note
    st.caption("Video: Understanding carbon emissions and climate change impacts")  
    
    # Sustainability-themed Lottie Animation (optional; ensure URL is lightweight)
    try:
        from streamlit_lottie import st_lottie
        lottie_url = "https://assets10.lottiefiles.com/packages/lf20_8u7tmfzq.json"  # Update as needed
        lottie_json = load_lottieurl(lottie_url)
        if lottie_json:
            st_lottie(lottie_json, height=300, key="lottie_carbon", speed=1)
    except Exception as e:
        st.write("Animation could not be loaded.")
    
    # Interactive widget: Emission Calculator Preview & "Did you know?" fact
    st.markdown('<div class="widget-container">', unsafe_allow_html=True)
    st.markdown("### Quick Carbon Footprint Estimator")
    st.markdown("Estimate your event's carbon emissions with the sliders below:")
    attendees = st.slider("Number of Attendees", min_value=50, max_value=1000, value=200, step=50)
    duration = st.slider("Event Duration (hours)", min_value=1, max_value=12, value=4, step=1)
    # Rough estimation formula (adjust as needed)
    estimate = attendees * duration * 0.05  
    st.metric(label="Estimated Emissions (tons CO₂)", value=f"{estimate:.2f}")
    
    # "Did you know?" fact that changes on each page load
    facts = [
        "Did you know? Transportation contributes about 14% of global greenhouse gas emissions.",
        "Did you know? Electricity and heat production are the largest contributors to global CO₂ emissions.",
        "Did you know? Sustainable practices can reduce your event’s carbon footprint by up to 30%.",
        "Did you know? Small changes in energy use can lead to big environmental benefits over time."
    ]
    fact = random.choice(facts)
    st.info(fact)
    
    # Global Emission Reduction Progress Bar (example value; update dynamically as needed)
    st.markdown("#### Global Emission Reduction Goal")
    progress = 65  # Example percentage value
    st.progress(progress)
    st.markdown(f"{progress}% of the global reduction target reached.")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------
# Function to handle login using your existing logic
def handle_authentication():
    user = simple_login()
    if not user:
        return False
    st.session_state.logged_in_user = user
    st.session_state.sidebar_page = "main"
    return True

# ------------------------------
# Main application flow
if "logged_in_user" in st.session_state:
    if "sidebar_page" not in st.session_state:
        st.session_state.sidebar_page = "main"
    render_sidebar(st.session_state.logged_in_user)
    if st.session_state.get("sidebar_page", "main") == "main":
        st.title("Emission Calculator and Analysis Dashboard")
        st.write("This dashboard is designed to calculate and analyze emissions for Scope 1, Scope 2, and Scope 3.")
        pages = {
            "Overview": overview_page,
            "Analysis": vis
        }
        selected = option_menu(
            menu_title="Emissions Calculators",
            menu_icon="cloud",
            options=list(pages.keys()),
            orientation="horizontal",
        )
        if selected in pages:
            with st.spinner(f"Loading {selected}..."):
                pages[selected]()
else:
    # Render the enhanced pre-login landing page with interactive elements
    render_landing_page()
    if handle_authentication():
        st.rerun()
    else:
        st.stop()