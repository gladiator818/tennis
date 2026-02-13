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
