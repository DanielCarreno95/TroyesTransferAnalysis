"""
Script to verify scraper is extracting correct data
Compares with expected values from Transfermarkt
"""

from scraper import get_troyes_squad_data
import pandas as pd

# Expected values from Transfermarkt (based on user's data)
EXPECTED_PLAYERS = 29
EXPECTED_TOTAL_VALUE = 27.93  # According to Transfermarkt
EXPECTED_AVG_AGE = 24.9  # According to Transfermarkt

# Key players to verify
KEY_PLAYERS = {
    'Mathys Detourbet': {'Position': 'Forward', 'Age': 18, 'Value': 4.0},
    'Tawfik Bentayeb': {'Position': 'Forward', 'Age': 23, 'Value': 3.0},
    'Jaurès Assoumou': {'Position': 'Forward', 'Age': 23, 'Value': 3.0},
    'Martin Adeline': {'Position': 'Midfielder', 'Age': 22, 'Value': 3.0},
    'Ismaël Boura': {'Position': 'Defender', 'Age': 25, 'Value': 2.5},
}

print("=" * 70)
print("VERIFICACIÓN DE DATOS DEL SCRAPER")
print("=" * 70)

df = get_troyes_squad_data()

print(f"\nESTADISTICAS GENERALES:")
print(f"   Total jugadores: {len(df)}")
print(f"   Valor total: {df['Market Value (M€)'].sum():.2f} M€")
print(f"   Edad promedio: {df['Age'].mean():.1f} años")
print(f"   Posiciones únicas: {df['Position'].nunique()}")

print(f"\nVALIDACION:")
errors = []

# Check total players
if len(df) != EXPECTED_PLAYERS:
    errors.append(f"[ERROR] Numero de jugadores incorrecto: {len(df)} (esperado: {EXPECTED_PLAYERS})")
else:
    print(f"[OK] Numero de jugadores correcto: {len(df)}")

# Check total value (allow small difference)
total_value = df['Market Value (M€)'].sum()
if abs(total_value - EXPECTED_TOTAL_VALUE) > 1.0:
    errors.append(f"[WARNING] Valor total diferente: {total_value:.2f} MEUR (esperado: {EXPECTED_TOTAL_VALUE} MEUR)")
else:
    print(f"[OK] Valor total correcto: {total_value:.2f} MEUR")

# Check average age
avg_age = df['Age'].mean()
if abs(avg_age - EXPECTED_AVG_AGE) > 1.0:
    errors.append(f"[WARNING] Edad promedio diferente: {avg_age:.1f} anos (esperado: {EXPECTED_AVG_AGE} anos)")
else:
    print(f"[OK] Edad promedio correcta: {avg_age:.1f} anos")

# Check key players
print(f"\nVERIFICANDO JUGADORES CLAVE:")
for player_name, expected_data in KEY_PLAYERS.items():
    player_row = df[df['Player Name'] == player_name]
    if len(player_row) == 0:
        errors.append(f"[ERROR] Jugador no encontrado: {player_name}")
        print(f"   [ERROR] {player_name}: NO ENCONTRADO")
    else:
        row = player_row.iloc[0]
        issues = []
        if row['Position'] != expected_data['Position']:
            issues.append(f"Posición: {row['Position']} (esperado: {expected_data['Position']})")
        if row['Age'] != expected_data['Age']:
            issues.append(f"Edad: {row['Age']} (esperado: {expected_data['Age']})")
        if abs(row['Market Value (M€)'] - expected_data['Value']) > 0.1:
            issues.append(f"Valor: {row['Market Value (M€)']} M€ (esperado: {expected_data['Value']} M€)")
        
        if issues:
            errors.append(f"[WARNING] {player_name}: {', '.join(issues)}")
            print(f"   [WARNING] {player_name}: {', '.join(issues)}")
        else:
            print(f"   [OK] {player_name}: Correcto")

# Check contract dates
print(f"\nVERIFICANDO FECHAS DE CONTRATO:")
contract_issues = df[df['Contract Expires'].str.contains(r'\d{2}/\d{2}/\d{4}', na=False, regex=True) == False]
if len(contract_issues) > 0:
    print(f"   [WARNING] {len(contract_issues)} jugadores con fechas de contrato incorrectas:")
    for idx, row in contract_issues.head(5).iterrows():
        print(f"      - {row['Player Name']}: '{row['Contract Expires']}'")
    errors.append(f"[WARNING] {len(contract_issues)} jugadores con fechas de contrato incorrectas")
else:
    print(f"   [OK] Todas las fechas de contrato tienen formato correcto")

# Final summary
print("\n" + "=" * 70)
if len(errors) == 0:
    print("[OK] TODOS LOS DATOS SON CORRECTOS")
    print("[OK] EL SCRAPER ESTA FUNCIONANDO PERFECTAMENTE")
else:
    print(f"[WARNING] SE ENCONTRARON {len(errors)} PROBLEMAS:")
    for error in errors:
        print(f"   {error}")
print("=" * 70)

# Show sample data
print("\nMUESTRA DE DATOS (primeros 5 jugadores):")
print(df.head().to_string(index=False))

