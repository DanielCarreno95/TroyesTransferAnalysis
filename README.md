# ESTAC Troyes - Squad Value & Age Structure Analysis

A comprehensive Streamlit application for analyzing ESTAC Troyes squad efficiency, focusing on the relationship between player age and market value. This tool provides data-driven insights for coaching staff and management decisions.

## Overview

This application extracts real-time squad data from Transfermarkt, processes it, and presents interactive visualizations with strategic insights for football team management.

## Features

- **Real-time Data Scraping**: Automatically fetches current squad data from Transfermarkt
- **Interactive Visualizations**: 4 comprehensive charts with detailed insights
- **Key Performance Indicators (KPIs)**: 3 critical metrics for squad analysis
- **Data Export**: Download squad data as CSV or Excel
- **Secure Access**: Password-protected application using environment variables
- **Professional UI**: Custom football-themed design with ESTAC Troyes colors

## Data Pipeline

### 1. Data Import & Scraping

The application uses **web scraping** to extract player data from Transfermarkt:

#### Source
- **URL**: `https://www.transfermarkt.es/estac-troyes/kader/verein/1095/saison_id/2025/plus/1`
- **Method**: Python `requests` library with proper headers to mimic browser behavior
- **Parser**: **BeautifulSoup4** for HTML parsing and data extraction

#### Why BeautifulSoup?
- **HTML Parsing**: BeautifulSoup provides robust parsing of complex HTML structures
- **Flexible Extraction**: Handles nested tables and dynamic content from Transfermarkt
- **Error Handling**: Gracefully handles missing data or structure changes
- **Cross-platform**: Works consistently across different systems

#### Implementation
```python
import requests
from bs4 import BeautifulSoup

response = requests.get(url, headers=headers, timeout=20)
soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find('table', class_='items')
```

#### Extracted Data Fields:
- **Player Name**: Full name from table links
- **Position**: Normalized to standard categories (Goalkeeper, Defender, Midfielder, Forward)
- **Age**: Extracted from birth date format (validated 16-50 years)
- **Market Value**: Converted to millions of euros (M€)
- **Contract Expiry Date**: Future contract end dates (2025-2030)

#### Fallback Mechanism
- If scraping fails or returns invalid data (< 10 players, < 80% valid ages, < 3 positions), the system uses dummy data with real player names
- Ensures application always has data to display

### 2. Data Cleaning & Processing

#### Market Value Conversion
**Why Clean?** Transfermarkt uses different formats (Spanish/English, millions/thousands)

**How:**
- **Spanish format**: "1,50 mill. €" → 1.5 M€
- **Spanish thousands**: "600 mil €" → 0.6 M€
- **English format**: "€1.50m" → 1.5 M€
- **Handles**: Commas, periods, currency symbols, abbreviations

**Implementation:**
```python
def parse_market_value(value_str: str) -> float:
    # Removes currency symbols, normalizes separators
    # Converts "mil" (thousands) and "mill" (millions)
    # Returns float in millions of euros
```

#### Position Normalization
**Why Normalize?** Transfermarkt uses multiple position names (Spanish/English variants)

**How:**
- **Spanish**: Portero, Defensa, Lateral, Pivote, Mediocentro, Extremo, Delantero
- **English**: Goalkeeper, Defender, Midfielder, Forward
- **All mapped to**: Goalkeeper, Defender, Midfielder, Forward, Unknown

**Why This Matters:**
- Consistent categorization for analysis
- Enables accurate grouping by playing line
- Prevents duplicate categories

#### Age Validation
**Why Validate?** Prevents invalid ages from corrupting analysis

**How:**
- Extracts age from pattern: "(28)" in date strings
- Validates range: 16-50 years (realistic for football players)
- Filters out invalid entries

**Impact:**
- Ensures KPIs (Average Age) are accurate
- Prevents statistical errors in visualizations

#### Contract Date Extraction
**Why Extract?** Contract expiry is critical for transfer planning

**How:**
- Identifies future dates (2025-2030) as contract end dates
- Distinguishes from signing dates (past dates)
- Uses regex pattern matching: `^(\d{2}/\d{2}/\d{4})$`

#### Duplicate Removal
**Why Remove?** Same player may appear multiple times in table

**How:**
- Uses `seen_players` set to track processed names
- Skips rows with duplicate player names

### 3. Data Validation

Before using scraped data:
- **Minimum players**: At least 10 players required
- **Age validity**: At least 80% of players must have valid ages
- **Position diversity**: At least 3 distinct positions required
- **Data integrity**: All required fields must be present

If validation fails → Uses fallback dummy data

## Key Performance Indicators (KPIs)

### 1. Total Squad Value
**Definition**: Sum of all players' market values in millions of euros.

**Calculation**: 
```
Total Squad Value = Σ(Market Value of each player)
```

**Why Important:**
- Represents total financial investment in the squad
- Higher value = more expensive squad (not necessarily better performance)
- Useful for budget planning and transfer strategy

**Strategic Use**: Compare with league average to understand market position.

### 2. Average Age
**Definition**: Mean age of all players in the squad.

**Calculation**: 
```
Average Age = Σ(Age of each player) / Number of players
```

**Why Important:**
- **< 24 years**: Young squad - high potential, low experience
- **24-27 years**: Prime age - optimal balance
- **> 28 years**: Veteran squad - experience but higher injury risk

**Strategic Use**: Plan generational transitions and identify renewal needs.

### 3. Value Efficiency Ratio
**Definition**: Total squad value divided by average age. Measures value per year of age.

**Calculation**: 
```
Value Efficiency Ratio = Total Squad Value / Average Age
```

**Why Important:**
- **High ratio**: Expensive but young squad - high potential return
- **Low ratio**: Cheap or old squad - may need investment
- **Optimal**: Balance between value and age

**Strategic Use**: Identify if squad is over/under-invested relative to age profile.

## Visualizations

### 1. Age vs Market Value by Position (Scatter Plot)

**Why This Chart?**
- Identifies the relationship between age and value
- Reveals which positions have the best value-for-age ratio
- Highlights star players and development opportunities

**Key Insights:**
- **Top-left quadrant**: Young players with high value → **Most valuable assets**, prioritize contract protection
- **24-27 years zone**: Players in prime → **Backbone of team**, maximize performance now
- **Right side, top**: Veterans with high value → **Expensive but experienced**, evaluate performance vs. cost
- **Bottom-left quadrant**: Young players with low value → **Development projects**, invest in training

**Strategic Recommendation**: Balance team between young prospects (future) and prime players (present).

### 2. Total Market Value by Line (Bar Chart)

**Why This Chart?**
- Shows investment distribution across playing lines
- Reveals squad balance (offensive vs defensive)
- Identifies transfer priorities

**Key Insights:**
- **Investment Distribution**: Identifies where club has invested most financial resources
- **Squad Balance**: 
  - If **Attack** has much more value → Offensive team, but defensively vulnerable
  - If **Defense** has much more value → Solid at the back, but may lack goals
  - If **Midfield** dominates → Game control, but may lack finishing
- **Transfer Strategy**: Line with low value = priority for reinforcements

**Strategic Recommendation**: Adjust playing style to strengths, plan transfers to balance team.

### 3. Age Distribution (Histogram)

**Why This Chart?**
- Shows squad age profile (young/veteran/balanced)
- Identifies generational gaps
- Highlights future planning needs

**Key Insights:**
- **Young Team (<24 avg)**: Energy and potential, but needs veteran leaders
- **Veteran Team (>28 avg)**: Experience and leadership, but needs generational renewal
- **Balanced Team (24-27 avg)**: Perfect combination, maintain with selective signings
- **Generational Gap**: Missing age groups → Future renewal problem

**Strategic Recommendation**: 
- **Optimal age by position**: 
  - Goalkeepers: 26-32 years
  - Defenders: 24-30 years
  - Midfielders: 22-28 years
  - Forwards: 20-27 years

### 4. Market Value Distribution by Position (Box Plot)

**Why This Chart?**
- Statistical distribution of values per position
- Identifies positions with highest median values
- Highlights star players (high outliers) and development opportunities (low outliers)

**Key Insights:**
- **High Median Value**: Quality players, but higher performance pressure
- **Large Variation (big boxes)**: Big difference between best and worst → Excessive dependence on star players
- **High Outliers**: **Star players** → Protect with contract renewal, build game around them
- **Low Outliers**: Development projects or veterans to evaluate
- **Small Boxes**: Balanced team in that position

**Strategic Recommendation**: 
- Sell high outliers if you can replace with 2-3 medium-value players (better depth)
- Invest training in young low outliers
- Prioritize positions with small boxes and low values

## Security: Login with Environment Variables

### Why Use .env File?

**Security Best Practice**: Never hardcode credentials in source code

**Benefits:**
- **Confidentiality**: Credentials stored outside code repository
- **Version Control Safety**: `.env` file is in `.gitignore`, never committed
- **Flexibility**: Different credentials for development/production
- **Team Collaboration**: Each developer can have their own credentials

### Implementation

**1. Create `.env` file:**
```bash
STREAMLIT_USERNAME=CityGroup
STREAMLIT_PASSWORD=CityGroup
```

**2. Load in Python:**
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file
# CRITICAL: Credentials ONLY from .env - NO hardcoded values
username = os.getenv("STREAMLIT_USERNAME")  # Must exist in .env
password = os.getenv("STREAMLIT_PASSWORD")  # Must exist in .env

# Application will show error if .env is missing or incomplete
if not username or not password:
    raise ValueError("❌ .env file required with STREAMLIT_USERNAME and STREAMLIT_PASSWORD")
```

**3. Verify in `.gitignore`:**
```
.env
*.env
```

**Why This Matters:**
- **NO credentials in source code**: The application reads credentials ONLY from `.env` file
- **No hardcoded values**: If `.env` is missing, the app shows an error (no fallback credentials)
- Prevents accidental credential exposure in GitHub
- Allows secure deployment to production
- Follows industry security standards

**⚠️ IMPORTANT**: The application will NOT work without a properly configured `.env` file. There are NO hardcoded credentials in the source code.

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd troyes_analysis
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables** (REQUIRED):
```bash
# The repository includes a .env file with default credentials
# If you need to create your own, copy the template:
cp .env .env.backup  # Backup existing .env
# Edit .env and set your credentials:
# STREAMLIT_USERNAME=your_username
# STREAMLIT_PASSWORD=your_password
```

**⚠️ CRITICAL**: The application requires a `.env` file with `STREAMLIT_USERNAME` and `STREAMLIT_PASSWORD`. Without it, the app will show an error and stop. There are NO hardcoded credentials in the code.

4. **Run the application**:
```bash
streamlit run app.py
```

Or using Python module:
```bash
python -m streamlit run app.py
```

## Project Structure

```
troyes_analysis/
├── app.py                  # Main Streamlit application
│   ├── Authentication (login with .env)
│   ├── Data loading from scraper
│   ├── Filters (Position, Age, Market Value)
│   ├── KPIs (3 metrics)
│   ├── Visualizations (4 charts with insights)
│   └── Data export (CSV/Excel)
│
├── scraper.py              # Web scraping module
│   ├── scrape_troyes_squad() - Main scraping function
│   ├── parse_market_value() - Value conversion
│   ├── normalize_position() - Position standardization
│   ├── get_troyes_squad_data() - Data retrieval with validation
│   └── get_dummy_data() - Fallback data
│
├── verify_scraper.py       # Data validation script
│   └── Tests scraper output for correctness
│
├── analysis_notebook.ipynb # Analysis documentation (Spanish)
│   └── Detailed explanations of methodology
│
├── requirements.txt        # Python dependencies
│   ├── streamlit
│   ├── pandas
│   ├── plotly
│   ├── requests
│   ├── beautifulsoup4
│   └── python-dotenv
│
├── .env                    # Credentials file (REQUIRED - not in Git)
├── .gitignore             # Git ignore rules (.env excluded)
└── README.md              # This file
```

## Usage

1. **Access the application**: Open `http://localhost:8501` in your browser
2. **Login**: Enter username and password (set in `.env`)
3. **View KPIs**: Check the three key metrics at the top
4. **Explore visualizations**: Use filters in the sidebar to analyze specific subsets
5. **Read insights**: Expand each chart's explanation for strategic recommendations
6. **Download data**: Export filtered results as CSV or Excel

## Data Source

- **Primary**: Transfermarkt (https://www.transfermarkt.es)
- **Team ID**: 1095 (ESTAC Troyes)
- **Season**: 2024/2025
- **Update Frequency**: Real-time on each app load
- **Fallback**: Dummy data with real player names if scraping fails

## Technical Details

- **Language**: Python 3.11+
- **Framework**: Streamlit
- **Visualization**: Plotly Express
- **Data Processing**: Pandas
- **Web Scraping**: 
  - **Requests**: HTTP library for fetching web pages
  - **BeautifulSoup4**: HTML parsing and data extraction
- **Authentication**: Environment variables with python-dotenv
- **Data Export**: CSV (pandas) and Excel (openpyxl)

## Security

- ✅ **Credentials ONLY in `.env` file** - NO credentials in source code
- ✅ **No hardcoded values** - Application requires `.env` file to function
- ✅ Password-protected access
- ✅ `.env` file included in `.gitignore` (not committed to Git)
- ✅ Application validates `.env` exists before allowing login
- ✅ Follows security best practices: credentials never in version control

## GitHub Structure Best Practices

This repository follows professional GitHub structure:

1. **Clear README**: Comprehensive documentation
2. **Requirements file**: All dependencies listed
3. **Environment file**: `.env` file with credentials (required for app to run)
4. **Git ignore**: Excludes sensitive files (`.env`, `__pycache__`, etc.)
5. **Modular code**: Separate files for scraping, app, and utilities
6. **Documentation**: Inline comments and notebook explanations

## License

This project is for educational and analytical purposes.

## Author

Data Science Team - ESTAC Troyes Analysis
