# Script para reiniciar la app Streamlit
Write-Host "Iniciando ESTAC Troyes Analysis App..." -ForegroundColor Green
Write-Host ""

# Navegar al directorio
Set-Location "C:\Users\Betan\troyes_analysis"

# Verificar que los archivos existen
if (-not (Test-Path "app.py")) {
    Write-Host "ERROR: app.py no encontrado!" -ForegroundColor Red
    exit 1
}

# Iniciar Streamlit
Write-Host "Ejecutando: streamlit run app.py" -ForegroundColor Cyan
streamlit run app.py

