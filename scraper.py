"""
ESTAC Troyes Squad Data Scraper
Extracts player data from Transfermarkt with fallback to dummy data
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from typing import Dict, List, Optional

def normalize_position(raw_position: str) -> str:
    """
    Normalizes Transfermarkt position names to standard categories
    Handles both English and Spanish position names
    """
    if not raw_position or raw_position == 'Unknown':
        return 'Unknown'
    
    raw_pos_lower = raw_position.lower()
    
    # Goalkeeper (Spanish: Portero)
    if any(term in raw_pos_lower for term in ['goalkeeper', 'portero', 'torwart', 'guardameta']):
        return 'Goalkeeper'
    
    # Defenders (Spanish: Defensa, Lateral)
    elif any(term in raw_pos_lower for term in ['defender', 'defence', 'defensa', 'defensa central',
                                                 'centre-back', 'center-back', 'central',
                                                 'left-back', 'right-back', 'lateral izquierdo', 
                                                 'lateral derecho', 'lateral', 'defensive', 
                                                 'verteidiger', 'pivote']):
        return 'Defender'
    
    # Midfielders (Spanish: Mediocentro, Pivote)
    elif any(term in raw_pos_lower for term in ['midfield', 'midfielder', 'mediocentro',
                                                 'central midfield', 'defensive midfield', 
                                                 'attacking midfield', 'mediocentro ofensivo',
                                                 'mediocentro defensivo', 'mittelfeld']):
        return 'Midfielder'
    
    # Forwards/Attackers (Spanish: Delantero, Extremo)
    elif any(term in raw_pos_lower for term in ['forward', 'striker', 'winger', 'attacker',
                                                 'delantero', 'extremo', 'delantero centro',
                                                 'extremo izquierdo', 'extremo derecho',
                                                 'centre-forward', 'center-forward', 'left winger', 
                                                 'right winger', 'sturm', 'angriff']):
        return 'Forward'
    
    else:
        return 'Unknown'

def parse_market_value(value_str: str) -> float:
    """
    Converts market value string (e.g., '€1.50m', '€500k', '1,50 mill. €', '600 mil €') to float in millions
    Handles both English and Spanish formats
    """
    if pd.isna(value_str) or value_str == '-' or value_str == '':
        return 0.0
    
    value_str = str(value_str).strip()
    
    # Handle Spanish format: "1,50 mill. €" or "600 mil €"
    # Replace comma with dot for decimal
    value_str = value_str.replace(',', '.')
    
    # Remove currency symbols and spaces
    value_str = value_str.replace('€', '').replace(' ', '').lower()
    
    # Extract number (handles both . and , as decimal separator)
    match = re.search(r'([\d.]+)', value_str)
    if not match:
        return 0.0
    
    number = float(match.group(1))
    
    # Convert based on unit (Spanish: mill = millions, mil = thousands)
    if 'mill' in value_str:
        return number  # Already in millions
    elif 'mil' in value_str or 'k' in value_str:
        return number / 1000  # Convert thousands to millions
    elif 'm' in value_str and 'mill' not in value_str:
        return number  # 'm' alone means millions
    else:
        # If no unit specified and number is small, assume thousands
        if number < 100:
            return number / 1000
        else:
            return number / 1000000  # Assume it's in raw format, convert to millions

def scrape_troyes_squad() -> Optional[pd.DataFrame]:
    """
    Scrapes ESTAC Troyes squad data from Transfermarkt
    Uses the EXACT URL provided by user with season 2025
    """
    # EXACT URL from user
    url = 'https://www.transfermarkt.es/estac-troyes/kader/verein/1095/saison_id/2025/plus/1'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Referer': 'https://www.transfermarkt.es/'
    }
    
    try:
        print(f"Scraping from: {url}")
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the main squad table with class 'items'
        table = soup.find('table', class_='items')
        if not table:
            print("[ERROR] Table with class 'items' not found")
            return None
        
        players = []
        tbody = table.find('tbody')
        if not tbody:
            print("[ERROR] Table body not found")
            return None
        
        rows = tbody.find_all('tr')
        print(f"Found {len(rows)} rows in table (expecting ~29 players)")
        
        seen_players = set()
        
        for idx, row in enumerate(rows):
            try:
                cells = row.find_all('td')
                if len(cells) < 5:
                    continue
                
                # Extract player name - from hauptlink class, usually in second column
                name = None
                name_cell = row.find('td', class_='hauptlink')
                if name_cell:
                    name_link = name_cell.find('a')
                    if name_link:
                        name = name_link.get_text(strip=True)
                    else:
                        name = name_cell.get_text(strip=True)
                
                if not name or name == '':
                    continue
                
                if name in seen_players:
                    continue
                seen_players.add(name)
                
                # Extract position - look in all cells for position text
                raw_position = 'Unknown'
                for cell in cells:
                    cell_text = cell.get_text(strip=True)
                    # Check if it's a position (Spanish terms)
                    if any(term in cell_text.lower() for term in ['portero', 'defensa', 'lateral', 'pivote', 
                                                                   'mediocentro', 'extremo', 'delantero', 'centro']):
                        raw_position = cell_text
                        break
                
                position = normalize_position(raw_position)
                
                # Extract age - look for pattern "DD/MM/YYYY (age)"
                age = None
                for cell in cells:
                    cell_text = cell.get_text(strip=True)
                    # Pattern: "12/01/1997 (28)" or similar
                    age_match = re.search(r'\((\d{1,2})\)', cell_text)
                    if age_match:
                        try:
                            potential_age = int(age_match.group(1))
                            if 16 <= potential_age <= 50:
                                age = potential_age
                                break
                        except:
                            pass
                
                if age is None:
                    continue
                
                # Extract market value - look for cells with "mil €" or "mill. €"
                market_value_str = '€0'
                for cell in cells:
                    cell_text = cell.get_text(strip=True)
                    if '€' in cell_text and ('mil' in cell_text.lower() or 'mill' in cell_text.lower()):
                        market_value_str = cell_text
                        break
                
                market_value = parse_market_value(market_value_str)
                
                # Extract contract expiry - MUST be the LAST date column (after "Fichado")
                # Table structure: F. Nacim./Edad | Nac. | Altura | Pie | Fichado | antes | Contrato | Valor
                # Contract date is in the "Contrato" column, which is typically the LAST zentriert cell
                # OR the second-to-last date (after "Fichado" date)
                contract_expires = 'Unknown'
                
                # Get all zentriert cells (centered cells with dates)
                zentriert_cells = row.find_all('td', class_='zentriert')
                dates_found = []
                
                # Collect all dates from zentriert cells with their position
                for idx, z_cell in enumerate(zentriert_cells):
                    z_text = z_cell.get_text(strip=True)
                    # Match date format DD/MM/YYYY without parentheses
                    date_match = re.match(r'^(\d{2}/\d{2}/\d{4})$', z_text)
                    if date_match and '(' not in z_text:
                        try:
                            year = int(z_text.split('/')[2])
                            dates_found.append((idx, z_text, year))
                        except:
                            pass
                
                # Contract end date is typically:
                # 1. The LAST date in the zentriert cells (rightmost column)
                # 2. With year 2025-2030 (future date)
                # 3. NOT the first date (which is usually birth date or signing date)
                if len(dates_found) >= 2:
                    # Take the last date (highest index) that is in future (2025-2030)
                    # This should be the contract end date, not the signing date
                    for idx, date_str, year in reversed(dates_found):
                        if 2025 <= year <= 2030:
                            contract_expires = date_str
                            break
                    # If no future date found, take the last date anyway (might be 2024)
                    if contract_expires == 'Unknown' and dates_found:
                        contract_expires = dates_found[-1][1]
                elif len(dates_found) == 1:
                    # If only one date, check if it's a future date
                    date_str, year = dates_found[0][1], dates_found[0][2]
                    if 2025 <= year <= 2030:
                        contract_expires = date_str
                
                # Alternative: Look for date in cells by position (contract is usually 2nd to last date column)
                if contract_expires == 'Unknown':
                    # Try to find date in all cells, prioritizing later columns
                    all_dates = []
                    for i, cell in enumerate(cells):
                        cell_text = cell.get_text(strip=True)
                        date_match = re.match(r'^(\d{2}/\d{2}/\d{4})$', cell_text)
                        if date_match and '(' not in cell_text:
                            try:
                                year = int(cell_text.split('/')[2])
                                if 2025 <= year <= 2030:
                                    all_dates.append((i, cell_text, year))
                            except:
                                pass
                    
                    # If we found multiple future dates, take the one with highest column index (rightmost)
                    if all_dates:
                        all_dates.sort(key=lambda x: x[0], reverse=True)
                        contract_expires = all_dates[0][1]
                
                players.append({
                    'Player Name': name,
                    'Position': position,
                    'Age': age,
                    'Market Value (M€)': market_value,
                    'Contract Expires': contract_expires
                })
                
            except Exception as e:
                print(f"Error in row {idx}: {e}")
                continue
        
        if len(players) >= 10:  # Need at least 10 players
            print(f"[OK] Successfully scraped {len(players)} REAL players")
            return pd.DataFrame(players)
        else:
            print(f"[ERROR] Only {len(players)} players found, need at least 10")
            return None
        
    except Exception as e:
        print(f"[ERROR] Scraping failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_dummy_data() -> pd.DataFrame:
    """
    Returns realistic dummy data for ESTAC Troyes squad (2024/2025 season)
    Based on actual known players from the team
    """
    dummy_data = {
        'Player Name': [
            'Nicolas de Préville',
            'Renaud Ripart',
            'Thierno Baldé',
            'Yoann Salmier',
            'Gauthier Gallon',
            'Xavier Chavalerin',
            'Rominigue Kouamé',
            'Abdu Conte',
            'Lucas Buades',
            'Jackson Porozo',
            'Mamadou Camara',
            'Wilson Odobert'
        ],
        'Position': [
            'Forward',
            'Forward',
            'Defender',
            'Defender',
            'Goalkeeper',
            'Midfielder',
            'Midfielder',
            'Forward',
            'Midfielder',
            'Defender',
            'Midfielder',
            'Forward'
        ],
        'Age': [34, 32, 23, 31, 29, 33, 28, 25, 22, 24, 26, 19],
        'Market Value (M€)': [1.5, 1.2, 2.5, 0.8, 1.0, 1.8, 1.5, 1.2, 0.6, 2.0, 1.0, 3.5],
        'Contract Expires': [
            '2025-06-30',
            '2025-06-30',
            '2026-06-30',
            '2025-06-30',
            '2024-06-30',
            '2025-06-30',
            '2026-06-30',
            '2025-06-30',
            '2027-06-30',
            '2026-06-30',
            '2025-06-30',
            '2027-06-30'
        ]
    }
    
    return pd.DataFrame(dummy_data)

def get_troyes_squad_data() -> pd.DataFrame:
    """
    Main function: MUST USE REAL DATA from Transfermarkt
    NO DUMMY DATA unless scraping completely fails after all attempts
    """
    print("=" * 70)
    print("OBTENIENDO DATOS REALES DE TRANSFERMARKT")
    print("URL: https://www.transfermarkt.es/estac-troyes/kader/verein/1095/saison_id/2025/plus/1")
    print("=" * 70)
    
    # Try scraping with retries
    max_attempts = 3
    for attempt in range(max_attempts):
        print(f"\n--- Intento {attempt + 1}/{max_attempts} ---")
        df = scrape_troyes_squad()
        
        if df is not None and len(df) >= 10:
            # Validate data quality
            valid_ages = df['Age'].between(16, 50).sum()
            total_value = df['Market Value (M€)'].sum()
            unique_positions = df['Position'].nunique()
            
            print(f"\n[OK] VALIDACION DE DATOS:")
            print(f"   - Jugadores: {len(df)}")
            print(f"   - Edades validas: {valid_ages}/{len(df)}")
            print(f"   - Valor total: {total_value:.2f} MEUR")
            print(f"   - Posiciones: {unique_positions}")
            print(f"   - Edad promedio: {df['Age'].mean():.1f} anos")
            
            if valid_ages >= len(df) * 0.8 and unique_positions >= 3:
                print("\n" + "=" * 70)
                print("[OK] DATOS REALES OBTENIDOS CORRECTAMENTE")
                print("=" * 70)
                return df[['Player Name', 'Position', 'Age', 'Market Value (M€)', 'Contract Expires']].copy()
            else:
                print(f"[WARNING] Datos insuficientes, reintentando...")
        else:
            print(f"[ERROR] Intento {attempt + 1} fallo")
    
    # ONLY use dummy if ALL attempts failed
    print("\n" + "=" * 70)
    print("[ERROR] TODOS LOS INTENTOS DE SCRAPING FALLARON")
    print("[WARNING] Usando datos dummy SOLO como ultimo recurso")
    print("=" * 70)
    return get_dummy_data()
    
    # Uncomment below if you want to try scraping (but validate first)
    # print("Attempting to scrape data from Transfermarkt...")
    # df = scrape_troyes_squad()
    # 
    # # Validate scraped data
    # if df is not None and len(df) > 0:
    #     # Check if ages are reasonable (between 16 and 45)
    #     valid_ages = df['Age'].between(16, 45).sum()
    #     total_players = len(df)
    #     
    #     # If less than 50% have valid ages, use dummy data
    #     if valid_ages < total_players * 0.5:
    #         print(f"Scraped data has invalid ages ({valid_ages}/{total_players} valid), using dummy data...")
    #         return get_dummy_data()
    #     
    #     # Filter out invalid rows
    #     df = df[df['Age'].between(16, 45)].copy()
    #     
    #     # Check if we have players in all lines
    #     df['Line'] = df['Position'].apply(lambda x: 'Goalkeeper' if x == 'Goalkeeper' 
    #                                       else 'Defense' if x == 'Defender' 
    #                                       else 'Midfield' if x == 'Midfielder' 
    #                                       else 'Attack' if x == 'Forward' else 'Unknown')
    #     lines_present = df[df['Line'] != 'Unknown']['Line'].nunique()
    #     
    #     if lines_present < 3:  # Should have at least 3 lines (excluding Unknown)
    #         print(f"Scraped data missing lines (only {lines_present} lines found), using dummy data...")
    #         return get_dummy_data()
    #     
    #     print(f"Successfully scraped and validated {len(df)} players")
    #     return df[['Player Name', 'Position', 'Age', 'Market Value (M€)', 'Contract Expires']].copy()
    # else:
    #     print("Scraping failed, using dummy data...")
    #     return get_dummy_data()

if __name__ == '__main__':
    # Test the scraper
    df = get_troyes_squad_data()
    print("\nSquad Data:")
    print(df.to_string())
    print(f"\nTotal players: {len(df)}")
    print(f"Total squad value: {df['Market Value (M€)'].sum():.2f} M€")

