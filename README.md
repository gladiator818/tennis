# ATP Top-100 Coach-Ready Performance Reports

Sistema de analítica para generar reportes de fortalezas/debilidades (coach-ready) para jugadores ATP masculinos Top-100.

## Qué incluye
- Ingesta configurable:
  - **Open-source (por defecto):** Jeff Sackmann (`tennis_atp`).
  - **Comercial (placeholder):** interfaz extensible para enriquecer métricas faltantes.
  - **Sin scraping ATP Tour** por defecto.
- Pipeline ETL reproducible: `data/raw -> data/processed -> db/tennis.duckdb`.
- Modelo de datos: `players`, `matches`, `match_stats`, `rankings`.
- Feature engineering por:
  - superficie (`Hard`, `Clay`, `Grass`, `Unknown`) + `is_indoor` inferido,
  - tier (`ATP 250`, `ATP 500`, `ATP 1000`, `Grand Slam`),
  - período (`52w`, `career`),
  - contexto (`vs Top10`, `vs Top20`, `tiebreaks`, `deciding sets`, `break points`).
- Normalización por percentiles y z-scores por superficie.
- Motor de insights:
  - reglas interpretables (umbral percentiles),
  - perfil simple (`serve-bot`, `baseliner`, `all-court`, `counterpuncher`).
- Salidas:
  - CLI para jugador individual y Top-100,
  - export CSV/JSON/Markdown por jugador,
  - tabla comparativa Top-100,
  - informe de cobertura de stats completos vs proxy.

## Setup
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```


## Quickstart (copiar y pegar)

### Opción A — Ejecutar todo de una vez
> Copia este bloque completo en tu terminal:

```bash
cd /workspace/tennis
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev]'

# Ingesta + ETL + base local
tennis-analytics ingest --years 2023,2024,2025 --source jeff

# Reporte de un jugador
tennis-analytics report-player --player "Carlos Alcaraz"

# Resumen Top-100
tennis-analytics report-top100

# Cobertura full/proxy
tennis-analytics report-coverage
```

### Opción B — Si `tennis-analytics` no existe en tu PATH
> Usa estos comandos equivalentes:

```bash
cd /workspace/tennis
source .venv/bin/activate
python -m tennis_analytics.cli ingest --years 2023,2024,2025 --source jeff
python -m tennis_analytics.cli report-player --player "Carlos Alcaraz"
python -m tennis_analytics.cli report-top100
python -m tennis_analytics.cli report-coverage
```

### Archivos que debes ver al final
```bash
ls -lah db/tennis.duckdb reports/top100_summary.csv reports/coverage_report.md reports/players/carlos_alcaraz.md
```

## Guía para principiantes (paso a paso)

> Si eres principiante, sigue estos pasos **exactamente en orden**.

### 0) Requisitos previos
- Tener **Python 3.11** instalado.
- Tener **internet** para descargar dependencias y datasets.

Comprueba versión de Python:
```bash
python3 --version
```
Debe mostrar algo como `Python 3.11.x`.

### 1) Entrar al proyecto
```bash
cd /workspace/tennis
```

### 2) Crear entorno virtual
```bash
python3.11 -m venv .venv
```

### 3) Activar entorno virtual
```bash
source .venv/bin/activate
```
Si funcionó, verás `(.venv)` al inicio de la línea de tu terminal.

### 4) Instalar dependencias
```bash
pip install -e '.[dev]'
```

### 5) Cargar datos + ETL + base DuckDB
```bash
python -m tennis_analytics.cli ingest --years 2023,2024,2025 --source jeff
```
Esto hace:
- descarga CSVs en `data/raw/`,
- procesa a `data/processed/`,
- crea base `db/tennis.duckdb`.

### 6) Generar un reporte de 1 jugador
```bash
python -m tennis_analytics.cli report-player --player "Carlos Alcaraz"
```
Salida esperada (archivos):
- `reports/players/carlos_alcaraz.md`
- `reports/players/carlos_alcaraz.json`

### 7) Generar resumen Top-100
```bash
python -m tennis_analytics.cli report-top100
```
Salida esperada:
- `reports/top100_summary.csv`

### 8) Generar reportes para todos los Top-100
```bash
python -m tennis_analytics.cli report-all-players
```

### 9) Generar informe de cobertura full/proxy
```bash
python -m tennis_analytics.cli report-coverage
```
Salida esperada:
- `reports/coverage_report.md`

### 10) Ver ejemplos ya incluidos
```bash
ls reports/examples
```

## Problemas comunes

### Error: `ModuleNotFoundError` (pandas/duckdb/etc)
No se instalaron dependencias. Repite:
```bash
source .venv/bin/activate
pip install -e '.[dev]'
```

### Error por red/proxy al instalar o descargar datos
Tu entorno no tiene salida a internet o está detrás de proxy. Solución:
- ejecutar en una máquina con internet,
- o configurar `HTTP_PROXY`/`HTTPS_PROXY`.

### Error: `Player not found`
Primero ejecuta `ingest`; luego usa el nombre exactamente como aparece en los datos.

## Uso CLI
```bash
# 1) Ingesta + ETL + carga a duckdb
python -m tennis_analytics.cli ingest --years 2023,2024,2025 --source jeff

# 2) Reporte jugador
python -m tennis_analytics.cli report-player --player "Carlos Alcaraz"

# 3) Reportes Top-100
python -m tennis_analytics.cli report-top100
python -m tennis_analytics.cli report-all-players

# 4) Cobertura full/proxy
python -m tennis_analytics.cli report-coverage
```

## Métricas
### Full (si hay match_stats)
- `spw_pct`, `rpw_pct`, `bp_saved_pct`, `bp_converted_pct`, `tb_win_pct`, `deciding_set_win_pct`, `win_pct`.

### Proxy (si faltan stats detallados)
- Se mantiene `win_pct`, `tb_win_pct`, `deciding_set_win_pct`, segmentos por superficie/tier/contexto.
- `metric_mode` marca explícitamente `full` o `proxy` según cobertura de partidos completos.

## Cobertura y limitaciones
- `reports/coverage_report.md` muestra `% partidos con stats completos` por jugador y tier.
- Métricas no disponibles sin feed comercial/point-by-point:
  - hold% y break% exactos por juegos de servicio/retorno,
  - presión por punto/shot-quality.
- Para cubrir faltantes, implementar `CommercialApiSource`.

## Fuentes y licencias
- Datos base: Jeff Sackmann tennis datasets (open-source, revisar licencia y términos del repo original).
- APIs comerciales: sujetas a licencia del proveedor.

## Ejemplos de reportes
Se incluyen 3 reportes de ejemplo en `reports/examples/`:
- `novak_djokovic.md`
- `carlos_alcaraz.md`
- `jannik_sinner.md`
