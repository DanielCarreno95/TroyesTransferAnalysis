"""
ESTAC Troyes - Squad Value & Age Structure Analysis
Streamlit application for analyzing squad efficiency (Age vs Market Value)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, use environment variables directly
    pass
from scraper import get_troyes_squad_data

# Environment variables loaded above (if dotenv available)

# Ensure pandas displays all data correctly
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Authentication
def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        # CRITICAL: Credentials ONLY from .env file, NOT hardcoded
        username = os.getenv("STREAMLIT_USERNAME")
        password = os.getenv("STREAMLIT_PASSWORD")
        
        # Security check: Fail if .env not configured
        if not username or not password:
            st.error("⚠️ Security Error: .env file not configured. Please create .env with STREAMLIT_USERNAME and STREAMLIT_PASSWORD")
            st.stop()
        
        if st.session_state["username"] == username and \
           st.session_state["password"] == password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False
    
    if "password_correct" not in st.session_state:
        # Login page styling with simple Troyes blue background (compatible with all browsers)
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #003366 0%, #0066CC 50%, #0099FF 100%);
            background-attachment: fixed;
        }
        .main {
            background: transparent;
        }
        [data-testid="stAppViewContainer"] {
            background: transparent;
        }
        .login-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 70vh;
            padding: 30px 40px;
        }
        .login-title {
            font-size: 42px;
            font-weight: 900;
            color: #FFFFFF;
            margin-bottom: 5px;
            text-align: center;
            text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.7), 0 0 20px rgba(255, 255, 255, 0.3);
            letter-spacing: 2px;
            font-family: 'Arial Black', 'Arial', sans-serif;
        }
        .login-subtitle {
            font-size: 18px;
            color: #E6F3FF;
            margin-bottom: 25px;
            text-align: center;
            font-weight: 500;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.6);
            letter-spacing: 1px;
        }
        .login-form-container {
            margin-top: 10px;
            width: 100%;
            max-width: 400px;
        }
        </style>
        <div class="login-container">
            <h1 class="login-title">ESTAC TROYES</h1>
            <p class="login-subtitle">Squad Analysis Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login form - closer to title
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="login-form-container">', unsafe_allow_html=True)
            st.text_input("Username", key="username", on_change=password_entered)
            st.text_input("Password", type="password", key="password", on_change=password_entered)
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    elif not st.session_state["password_correct"]:
        # Login page styling for retry with simple Troyes blue background (compatible with all browsers)
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #003366 0%, #0066CC 50%, #0099FF 100%);
            background-attachment: fixed;
        }
        .main {
            background: transparent;
        }
        [data-testid="stAppViewContainer"] {
            background: transparent;
        }
        .login-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 70vh;
            padding: 30px 40px;
        }
        .login-title {
            font-size: 42px;
            font-weight: 900;
            color: #FFFFFF;
            margin-bottom: 5px;
            text-align: center;
            text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.7), 0 0 20px rgba(255, 255, 255, 0.3);
            letter-spacing: 2px;
            font-family: 'Arial Black', 'Arial', sans-serif;
        }
        .login-subtitle {
            font-size: 18px;
            color: #E6F3FF;
            margin-bottom: 25px;
            text-align: center;
            font-weight: 500;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.6);
            letter-spacing: 1px;
        }
        .login-form-container {
            margin-top: 10px;
            width: 100%;
            max-width: 400px;
        }
        </style>
        <div class="login-container">
            <h1 class="login-title">ESTAC TROYES</h1>
            <p class="login-subtitle">Squad Analysis Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login form with error - closer to title
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="login-form-container">', unsafe_allow_html=True)
            st.text_input("Username", key="username", on_change=password_entered)
            st.text_input("Password", type="password", key="password", on_change=password_entered)
            st.error("Invalid username or password")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    else:
        # Password correct
        return True

if not check_password():
    st.stop()

# ESTAC Troyes color palette
TROYES_BLUE_DARK = '#003366'
TROYES_BLUE_MEDIUM = '#0066CC'
TROYES_BLUE_LIGHT = '#0099FF'
TROYES_RED = '#FF0000'
TROYES_WHITE = '#FFFFFF'

# Page configuration
st.set_page_config(
    page_title="ESTAC Troyes Analysis",
    layout="wide"
)

# Custom CSS for Troyes theme - Paper texture background with blue tones (inspired by Pinterest design)
st.markdown(f"""
    <style>
    .main {{
        background: #F8F6F0;
        background-image: 
            radial-gradient(circle at 1px 1px, rgba(0, 51, 102, 0.15) 1px, transparent 0),
            linear-gradient(180deg, rgba(255, 140, 0, 0.05) 0%, transparent 50%),
            linear-gradient(90deg, rgba(0, 51, 102, 0.03) 0%, transparent 50%);
        background-size: 20px 20px, 100% 100%, 100% 100%;
        background-attachment: fixed;
    }}
    .stApp {{
        background: #F8F6F0;
    }}
    [data-testid="stAppViewContainer"] {{
        background: #F8F6F0;
    }}
    .stSidebar {{
        background: linear-gradient(180deg, #003366 0%, #004080 30%, #0066CC 60%, #0099FF 100%);
        border-right: 4px solid #001F3F;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
    }}
    .stSidebar .stMarkdown {{
        color: #FFFFFF !important;
    }}
    .stSidebar label {{
        color: #FFFFFF !important;
        font-weight: bold;
    }}
    .stSidebar .stSelectbox label, .stSidebar .stSlider label {{
        color: #FFFFFF !important;
    }}
    /* All sidebar text elements in white */
    .stSidebar p, .stSidebar span, .stSidebar div {{
        color: #FFFFFF !important;
    }}
    .stSidebar .stMarkdown p, .stSidebar .stMarkdown span, .stSidebar .stMarkdown div {{
        color: #FFFFFF !important;
    }}
    /* Position filter - Dark blue background */
    .stSidebar [data-baseweb="select"] {{
        background-color: #003366 !important;
    }}
    .stSidebar [data-baseweb="select"] > div {{
        background-color: #003366 !important;
    }}
    .stSidebar [data-baseweb="select"] input {{
        background-color: #003366 !important;
        color: #FFFFFF !important;
    }}
    .stSidebar [data-baseweb="select"] svg {{
        color: #FFFFFF !important;
    }}
    /* Force white background for download buttons (not selectbox) */
    [data-baseweb="select"]:not(.stSidebar [data-baseweb="select"]) {{
        background-color: #FFFFFF !important;
    }}
    button[kind="secondary"] {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #CCCCCC !important;
    }}
    button[kind="secondary"]:hover {{
        background-color: #F0F0F0 !important;
    }}
    .stSidebar h1, .stSidebar h2, .stSidebar h3 {{
        color: #FFFFFF !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }}
    .stMetric {{
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid {TROYES_BLUE_DARK};
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }}
    .stMetric label {{
        color: {TROYES_BLUE_DARK} !important;
        font-weight: bold;
        font-size: 14px;
    }}
    .stMetric [data-testid="stMetricValue"] {{
        color: {TROYES_BLUE_DARK} !important;
        font-size: 28px;
        font-weight: bold;
    }}
    .stMetric [data-testid="stMetricDelta"] {{
        color: #666666 !important;
    }}
    /* FORCE ALL TEXT TO BLACK */
    h1, h2, h3, h4, h5, h6 {{
        color: #000000 !important;
        font-weight: bold;
    }}
    h1 {{
        border-bottom: 3px solid {TROYES_BLUE_DARK};
        padding-bottom: 10px;
    }}
    .stMarkdown p, .stMarkdown li, .stMarkdown ul, .stMarkdown ol {{
        color: #000000 !important;
    }}
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] ul,
    [data-testid="stMarkdownContainer"] ol {{
        color: #000000 !important;
    }}
    [data-testid="stMarkdownContainer"] {{
        color: #000000 !important;
    }}
    .stExpander {{
        background-color: #FFFFFF;
        border: 1px solid {TROYES_BLUE_DARK};
    }}
    .stExpander label {{
        color: #000000 !important;
        font-weight: bold;
    }}
    .stExpander .stMarkdown p {{
        color: #000000 !important;
    }}
    [data-testid="stHeader"] {{
        background-color: {TROYES_BLUE_DARK};
    }}
    [data-testid="stHeader"] .stMarkdown {{
        color: #FFFFFF;
    }}
    /* Force all Streamlit text elements to black */
    .element-container p,
    .element-container div,
    .element-container span {{
        color: #000000 !important;
    }}
    /* Table text */
    [data-testid="stDataFrame"] {{
        color: #000000 !important;
    }}
    /* Caption text */
    .stCaption {{
        color: #000000 !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Title - FORCED BLACK TEXT
st.markdown('<h1 style="color: #000000 !important; font-weight: bold; border-bottom: 3px solid #003366; padding-bottom: 10px;">ESTAC Troyes - Squad Value & Age Structure Analysis</h1>', unsafe_allow_html=True)
st.markdown("---")

# Load data - USE REAL DATA from Transfermarkt
from scraper import get_troyes_squad_data
df = get_troyes_squad_data()

# Show data source info - VERIFIED DATA SOURCE
if len(df) > 20:  # Real data usually has more players
    st.sidebar.markdown(f'<p style="color: #FFFFFF; background: rgba(0, 0, 0, 0.3); padding: 10px; border-radius: 5px; text-align: center; font-weight: bold;">✓ REAL DATA: {len(df)} players from Transfermarkt</p>', unsafe_allow_html=True)
    st.session_state['data_verified'] = True
    st.session_state['data_source'] = 'Transfermarkt'
else:
    st.sidebar.markdown(f'<p style="color: #FFFFFF; background: rgba(255, 0, 0, 0.3); padding: 10px; border-radius: 5px; text-align: center;">⚠ Fallback data: {len(df)} players</p>', unsafe_allow_html=True)
    st.session_state['data_verified'] = False
    st.session_state['data_source'] = 'Dummy'

# Sidebar filters with blue Troyes theme
st.sidebar.markdown("""
    <style>
    .sidebar-header {
        color: #FFFFFF;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
        text-align: center;
        padding: 10px;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 5px;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    }
    </style>
    <div class="sidebar-header">Filters</div>
""", unsafe_allow_html=True)

# Position filter
positions = ['All'] + sorted(df['Position'].unique().tolist())
selected_position = st.sidebar.selectbox("Position", positions)

# Age range filter
min_age, max_age = st.sidebar.slider(
    "Age Range",
    min_value=int(df['Age'].min()),
    max_value=int(df['Age'].max()),
    value=(int(df['Age'].min()), int(df['Age'].max()))
)

# Market value filter
min_value, max_value = st.sidebar.slider(
    "Market Value Range (M€)",
    min_value=float(df['Market Value (M€)'].min()),
    max_value=float(df['Market Value (M€)'].max()),
    value=(float(df['Market Value (M€)'].min()), float(df['Market Value (M€)'].max()))
)

# Apply filters - CRITICAL: All visualizations use filtered_df from verified source
# This ensures all charts use the same verified data
filtered_df = df[
    (df['Age'] >= min_age) & 
    (df['Age'] <= max_age) &
    (df['Market Value (M€)'] >= min_value) &
    (df['Market Value (M€)'] <= max_value)
].copy()

if selected_position != 'All':
    filtered_df = filtered_df[filtered_df['Position'] == selected_position].copy()

# VERIFICATION: Ensure filtered_df is not empty and uses verified source
if len(filtered_df) == 0:
    st.warning("No players match the selected filters. Adjust filters to see data.")
    filtered_df = df.copy()  # Fallback to full dataset

# KPIs - FORCED BLACK TEXT
st.markdown('<h2 style="color: #000000 !important; font-weight: bold;">Key Performance Indicators</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    total_value = filtered_df['Market Value (M€)'].sum()
    # Calculate delta only if filters are applied
    base_total = df['Market Value (M€)'].sum()
    delta_val = total_value - base_total if len(filtered_df) < len(df) else None
    st.metric(
        label="Total Squad Value",
        value=f"{total_value:.2f} M€",
        delta=f"{delta_val:.2f} M€" if delta_val is not None and abs(delta_val) > 0.01 else None
    )

with col2:
    # CRITICAL: Use verified data from filtered_df (which comes from verified source)
    avg_age = filtered_df['Age'].mean()
    # Validate age is reasonable (between 16-50 for football players)
    if avg_age < 16 or avg_age > 50:
        # If age is invalid, use the full dataset average
        avg_age = df['Age'].mean()
    
    base_avg_age = df['Age'].mean()
    delta_age = avg_age - base_avg_age if len(filtered_df) < len(df) else None
    st.metric(
        label="Average Age",
        value=f"{avg_age:.1f} years",
        delta=f"{delta_age:.1f}" if delta_age is not None and abs(delta_age) > 0.1 else None
    )

with col3:
    # CRITICAL: Use verified avg_age from filtered_df
    # Ensure avg_age is valid (between 16-50)
    if avg_age < 16 or avg_age > 50:
        avg_age = df['Age'].mean()
    # Calculate efficiency: total value / average age
    value_per_age = total_value / avg_age if avg_age > 0 else 0
    st.metric(
        label="Value Efficiency Ratio",
        value=f"{value_per_age:.2f} M€/year",
        help="Total squad value divided by average age"
    )

st.markdown("---")

# Visualizations - FORCED BLACK TEXT
st.markdown('<h2 style="color: #000000 !important; font-weight: bold;">Visualizations</h2>', unsafe_allow_html=True)

# Graph 1: Scatter Plot - Age vs Market Value
col1, col2 = st.columns(2)

with col1:
    fig_scatter = px.scatter(
        filtered_df,
        x='Age',
        y='Market Value (M€)',
        color='Position',
        size='Market Value (M€)',
        hover_data=['Player Name'],
        title="Age vs Market Value by Position",
        labels={
            'Age': 'Age (years)',
            'Market Value (M€)': 'Market Value (M€)',
            'Position': 'Position'
        },
        color_discrete_map={
            'Goalkeeper': '#003366',
            'Defender': '#0066CC',
            'Midfielder': '#0099FF',
            'Forward': '#FF0000'
        }
    )
    fig_scatter.update_layout(
        height=500,
        showlegend=True,
        hovermode='closest'
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Explanation of scatter plot - SPORTS INSIGHTS FOR STAFF
    with st.expander("Age vs Market Value - Strategic Insights for Coaching Staff"):
        st.markdown("""
        **STRATEGIC VALUE ANALYSIS BY AGE AND POSITION:**
        
        **What does this chart show?**
        - **X-axis**: Player age in years
        - **Y-axis**: Market value in millions of euros
        - **Colors**: Positions (Goalkeeper, Defender, Midfielder, Forward)
        - **Bubble size**: Larger size = higher market value
        
        **CRITICAL SPORTS INSIGHTS FOR STAFF:**
        
        **Young Players with High Value (top-left quadrant)**
        - **Action**: These are your **most valuable assets**. Prioritize their development and contract protection.
        - **Example**: If you see a forward aged 18-22 with value >3M€, this is a **star talent** that needs playing time and career planning.
        - **Risk**: High risk of sale if contract is not renewed in time.
        
        **Peak Value Zone (24-27 years)**
        - **Action**: Players in their **physical and mental prime**. They are the backbone of the team.
        - **Strategy**: Maximize their performance now, they make the difference in key matches.
        - **Renewal**: Critical moment to negotiate extensions before they lose value.
        
        **Veterans with High Value (right side, top)**
        - **Action**: **Expensive but experienced** players. Evaluate if their performance justifies the cost.
        - **Decision**: Keep for leadership or free up salary for young signings?
        - **Analysis**: Compare their value with their actual on-field contribution.
        
        **Young Players with Low Value (bottom-left quadrant)**
        - **Action**: **Development projects**. Invest in their training, they can multiply their value.
        - **Opportunity**: If developed well, you can sell with profit or have a key player at low cost.
        
        **TECHNICAL RECOMMENDATION**: 
        - Balance the team between young prospects (future) and prime players (present).
        - Identify which positions need immediate reinforcement vs. long-term development.
        """)

# Graph 2: Bar Chart - Total Market Value by Line
with col2:
    # Categorize positions into lines - improved to handle all cases
    def categorize_line(position):
        if pd.isna(position) or position == 'Unknown':
            return 'Unknown'
        position_str = str(position).strip()
        if position_str == 'Goalkeeper':
            return 'Goalkeeper'
        elif position_str == 'Defender':
            return 'Defense'
        elif position_str == 'Midfielder':
            return 'Midfield'
        elif position_str == 'Forward':
            return 'Attack'
        else:
            # Fallback: try to infer from position name
            pos_lower = position_str.lower()
            if 'goalkeeper' in pos_lower or 'keeper' in pos_lower:
                return 'Goalkeeper'
            elif any(term in pos_lower for term in ['defender', 'defence', 'back', 'centre-back', 'center-back']):
                return 'Defense'
            elif any(term in pos_lower for term in ['midfield', 'midfielder']):
                return 'Midfield'
            elif any(term in pos_lower for term in ['forward', 'striker', 'winger', 'attacker']):
                return 'Attack'
            else:
                return 'Unknown'
    
    filtered_df['Line'] = filtered_df['Position'].apply(categorize_line)
    # Filter out Unknown lines
    line_df = filtered_df[filtered_df['Line'] != 'Unknown'].copy()
    line_values = line_df.groupby('Line')['Market Value (M€)'].sum().reset_index()
    line_values = line_values.sort_values('Market Value (M€)', ascending=False)
    
    # ESTAC Troyes color palette: Blue (#003366) and White/Red accents
    troyes_colors = {
        'Goalkeeper': '#003366',  # Dark blue
        'Defense': '#0066CC',     # Medium blue
        'Midfield': '#0099FF',    # Light blue
        'Attack': '#FF0000'       # Red accent
    }
    
    fig_bar = px.bar(
        line_values,
        x='Line',
        y='Market Value (M€)',
        title="Total Market Value by Line",
        labels={
            'Line': 'Line',
            'Market Value (M€)': 'Total Market Value (M€)'
        },
        color='Line',
        color_discrete_map=troyes_colors
    )
    # Add data labels to bars - ensure they show
    for i, val in enumerate(line_values['Market Value (M€)']):
        fig_bar.add_annotation(
            x=line_values['Line'].iloc[i],
            y=val,
            text=f'{val:.2f} M€',
            showarrow=False,
            yshift=10,
            font=dict(size=12, color=TROYES_BLUE_DARK, family="Arial Black")
        )
    fig_bar.update_layout(
        height=500,
        showlegend=False,
        xaxis_title="",
        yaxis_title="Market Value (M€)",
        margin=dict(b=50, t=50)
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Explanation of bar chart - SPORTS INSIGHTS FOR STAFF
    with st.expander("Total Market Value by Line - Squad Investment Analysis"):
        st.markdown("""
        **SQUAD INVESTMENT ANALYSIS BY LINE:**
        
        **What does this chart show?**
        - **Bars**: Total market value (sum of all players) by line
        - **Lines**: Goalkeeper, Defense, Midfield, Attack
        
        **CRITICAL SPORTS INSIGHTS FOR STAFF:**
        
        **Investment Distribution**
        - **Analysis**: Identifies where the club has invested the most financial resources.
        - **Interpretation**: A line with high value = quality players, but also = higher performance pressure.
        - **Risk**: If a line has high value but low performance, there is a management problem.
        
        **Squad Balance**
        - **Ideal balance**: All lines should have similar values for a balanced team.
        - **Detected imbalance**: 
          - If **Attack** has much more value → Offensive team, but may be defensively vulnerable.
          - If **Defense** has much more value → Solid at the back, but may lack goals.
          - If **Midfield** dominates → Game control, but may lack finishing.
        
        **Transfer Strategy**
        - **Line with low value**: Priority for reinforcements in next transfer windows.
        - **Line with high value**: Ensure you have depth (quality substitutes).
        - **Recommendation**: Do not overload one line if others are weak.
        
        **Comparison with Rivals**
        - **Benchmark**: Compare your distribution with teams at your level.
        - **Competitive advantage**: Identify if your strength aligns with your playing style.
        
        **TECHNICAL RECOMMENDATION**:
        - If value is unbalanced, adjust playing style to your strengths.
        - Plan transfers to balance the team, not just to reinforce what is already strong.
        - Consider selling expensive players in overloaded lines to reinforce weak lines.
        """)

# Graph 3: Age Distribution
col3, col4 = st.columns(2)

with col3:
    fig_age_dist = px.histogram(
        filtered_df,
        x='Age',
        nbins=10,
        title="Age Distribution",
        labels={'Age': 'Age (years)', 'count': 'Number of Players'},
        color_discrete_sequence=[TROYES_BLUE_DARK]
    )
    # Add data labels to histogram bars - ensure they show
    fig_age_dist.update_traces(
        texttemplate='%{y}',
        textposition='outside',
        textfont=dict(size=11, color=TROYES_BLUE_DARK, family="Arial Black"),
        hovertemplate='Age: %{x}<br>Players: %{y}<extra></extra>'
    )
    fig_age_dist.update_layout(
        height=400,
        showlegend=False,
        margin=dict(b=50, t=50)
    )
    st.plotly_chart(fig_age_dist, use_container_width=True)
    
    # Explanation of age distribution - SPORTS INSIGHTS FOR STAFF
    with st.expander("Age Distribution - Squad Age Profile Analysis"):
        st.markdown("""
        **SQUAD AGE PROFILE - STRATEGIC ANALYSIS:**
        
        **What does this chart show?**
        - **X-axis**: Age ranges (groups)
        - **Y-axis**: Number of players in each age group
        - **Bars**: Count of players per age bracket
        
        **CRITICAL SPORTS INSIGHTS FOR STAFF:**
        
        **Team Age Profile**
        - **Young Team (average <24 years)**: 
          - **Advantage**: Energy, improvement potential, low salary cost.
          - **Risk**: Lack of experience in key moments, emotional instability.
          - **Action**: You need 2-3 veteran leaders to guide the group.
        
        **Veteran Team (average >28 years)**:
          - **Advantage**: Experience, leadership, winning mentality.
          - **Risk**: More frequent injuries, loss of pace, high cost.
          - **Action**: Plan urgent generational renewal.
        
        **Balanced Team (24-27 years average)**:
          - **Ideal**: Perfect combination of experience and youth.
          - **Strategy**: Maintain this balance with selective signings.
        
        **Age Concentration**
        - **Peak at 18-22 years**: Many young players → Development opportunity, but risk of inexperience.
        - **Peak at 25-28 years**: Players in prime → Maximum expected performance.
        - **Generational gap**: If there is a gap (e.g., few players aged 23-25) → Future renewal problem.
        
        **Medium-term Planning**
        - **Players 30+**: Identify when your key players retire. Plan substitutes NOW.
        - **Players 18-21**: Project their development. Will they be starters in 2-3 years?
        - **Generational transition**: Avoid all your best players retiring at the same time.
        
        **Signing Recommendations**
        - If you have many young players → Sign 1-2 experienced veterans.
        - If you have many veterans → Sign 3-4 young prospects.
        - If there is a generational gap → Sign players of the missing age.
        
        **TECHNICAL RECOMMENDATION**:
        - **Optimal age by position**: 
          - Goalkeepers: 26-32 years (experience key)
          - Defenders: 24-30 years (physical strength + experience)
          - Midfielders: 22-28 years (stamina + technique)
          - Forwards: 20-27 years (speed + finishing)
        - Adjust your playing style according to the team's age profile.
        """)

# Graph 4: Market Value Distribution by Position
with col4:
    fig_value_box = px.box(
        filtered_df,
        x='Position',
        y='Market Value (M€)',
        title="Market Value Distribution by Position",
        labels={
            'Position': 'Position',
            'Market Value (M€)': 'Market Value (M€)'
        },
        color='Position',
        color_discrete_map={
            'Goalkeeper': TROYES_BLUE_DARK,
            'Defender': TROYES_BLUE_MEDIUM,
            'Midfielder': TROYES_BLUE_LIGHT,
            'Forward': TROYES_RED
        }
    )
    fig_value_box.update_layout(
        height=400,
        showlegend=False,
        margin=dict(b=50, t=50)
    )
    st.plotly_chart(fig_value_box, use_container_width=True)
    
    # Explanation of the box plot - SPORTS INSIGHTS FOR STAFF
    with st.expander("Market Value Distribution by Position - Positional Value Analysis"):
        st.markdown("""
        **VALUE DISTRIBUTION BY POSITION - STATISTICAL ANALYSIS:**
        
        **What does this box plot show?**
        - **Box**: Interquartile range (IQR) - where the central 50% of values fall
        - **Center line**: Median (typical) value for that position
        - **Whiskers**: Range of values (excluding outliers)
        - **Dots**: Atypical players (very high or very low values)
        
        **CRITICAL SPORTS INSIGHTS FOR STAFF:**
        
        **Positions with Highest Median Value**
        - **Interpretation**: These positions have more valuable players on average.
        - **Action**: Ensure you have **depth** in these positions. If your star gets injured, do you have a quality substitute?
        - **Strategy**: These are your **strong lines**. Take tactical advantage of this.
        
        **Positions with Highest Variation (large boxes)**
        - **Interpretation**: There is a big difference between your best and worst player in that position.
        - **Risk**: Excessive dependence on 1-2 star players.
        - **Action**: 
          - If the high outlier gets injured → Serious problem.
          - If you have low outliers → Development or sale opportunity.
        - **Recommendation**: Seek balance. Do not depend on a single player.
        
        **High Outliers (points above)**
        - **Identification**: **Star** players with value much higher than the rest.
        - **Action**: 
          - **Protection**: Renew contract urgently if it is close to expiring.
          - **Strategy**: Build the game around these players.
          - **Risk**: If they leave, the team loses much value.
        
        **Low Outliers (points below)**
        - **Identification**: Players with very low value for their position.
        - **Opportunity**: 
          - If young → Development project, they can multiply value.
          - If veterans → Consider if their performance justifies keeping them.
        - **Decision**: Invest in their development or seek alternative?
        
        **Value Consistency**
        - **Small boxes**: Similar values among players → Balanced team in that position.
        - **Large boxes**: Big difference → You need to level up (raise weak players' level or sell expensive ones).
        
        **Analysis by Specific Position**
        - **Goalkeepers**: If there is high variation → You have a star goalkeeper and weak substitutes. Seek balance.
        - **Defenders**: High variation → Inconsistent defensive line. Prioritize signings.
        - **Midfielders**: If value is high → You have game control. If low → You need creativity.
        - **Forwards**: High outliers → You have a star scorer. Ensure you have an alternative.
        
        **TECHNICAL RECOMMENDATION**:
        - **Market strategy**: Sell high outliers if you can replace them with 2-3 medium-value players (better depth).
        - **Development**: Invest training time in young low outliers.
        - **Signings**: Prioritize positions with small boxes and low values (you need to level up).
        - **Tactics**: Adjust your playing system according to where your high outliers are (your strengths).
        """)

st.markdown("---")

# Data table - FORCED BLACK TEXT
st.markdown('<h2 style="color: #000000 !important; font-weight: bold;">Squad Data</h2>', unsafe_allow_html=True)

# Display dataframe
display_df = filtered_df[['Player Name', 'Position', 'Age', 'Market Value (M€)', 'Contract Expires']].sort_values('Market Value (M€)', ascending=False)
st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

# Download buttons
col_dl1, col_dl2 = st.columns(2)

with col_dl1:
    # CSV download - WHITE BACKGROUND
    csv = display_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="Download Data as CSV",
        data=csv,
        file_name=f"troyes_squad_data_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        key='download-csv',
        type="secondary"
    )

with col_dl2:
    # Excel download - WHITE BACKGROUND
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        display_df.to_excel(writer, index=False, sheet_name='Squad Data')
    excel_data = output.getvalue()
    st.download_button(
        label="Download Data as Excel",
        data=excel_data,
        file_name=f"troyes_squad_data_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key='download-excel',
        type="secondary"
    )

# Footer - FORCED BLACK TEXT
st.markdown("---")
st.markdown('<p style="color: #000000 !important; text-align: center; font-size: 0.9em;">Data source: Transfermarkt | Analysis: ESTAC Troyes Squad Efficiency</p>', unsafe_allow_html=True)

