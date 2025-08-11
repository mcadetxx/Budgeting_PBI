# Budgeting_PBI

@Owner: Marckenrold Cadet
# Power BI Budgeting Dashboard (ARIMA) – Documentation 

This is everything needed to assemble a 3‑page Power BI report with an ARIMA/SARIMAX forecast.

## What’s inside
- `data/budget_sample.csv` – Sample 36‑month dataset (Dept × Category × Date with Budget/Actual)
- `scripts/powerbi_arima_script.py` – Python script for SARIMAX forecasting per Department×Category
- `dax/powerbi_dax_measures.txt` – Copy/paste measures for KPIs, YTD, and projections
- `theme/powerbi_theme_budget_forecast.json` – Clean theme with legible defaults
- `README.md` – This file

## Quick Build
1) Open **Power BI Desktop** → **Get Data → Text/CSV** → import `data/budget_sample.csv` as **BudgetData**.
2) **File → Options → Python scripting** → select a Python env with: `pandas`, `numpy`, `statsmodels`.
3) **Transform Data** → **Run Python script** → paste contents of `scripts/powerbi_arima_script.py` → return `result` → name it **ForecastData**.
4) **Model view** → create relationships (Department, Category, Date) between BudgetData and ForecastData.
5) **View → Themes → Browse** → import `theme/powerbi_theme_budget_forecast.json`.
6) **Model view** → New measures → copy from `dax/powerbi_dax_measures.txt`.

## Pages & Visuals
### Page 1 – Executive Summary
- Cards: Total Budget, Total Actual, YTD Variance $, YTD Variance %, Year‑End Projection, Expected Surplus/Deficit
- Line chart: Date on axis; Actual (BudgetData), Budget (BudgetData), Forecast Amount (ForecastData)
- Bar chart: Category vs [YTD Variance $]
- Optional: TopN cards for Over/Under Budget (use filters on [YTD Variance $])

### Page 2 – Department & Category Drilldown
- Slicers: Department, Category, Date (Month/Quarter)
- Matrix: Rows = Department→Category; Columns = Year/Month; Values = Budget, Actual, [YTD Variance $]
- Decomposition tree: Analyze [YTD Variance $] by Department→Category→Month

### Page 3 – Forecast Analysis
- Line chart: Date vs Actual/Budget/Forecast Amount (or Forecast (Adj) from What‑If parameter)
- Table: Date, Department, Category, Forecast, Lower, Upper
- What‑If parameter: InflationAdj % (−5%..+10%, step 0.5%)
  ```
  Forecast (Adj) = [Forecast Amount] * (1 + 'InflationAdj %'[InflationAdj % Value])
  ```

## Troubleshooting
- If Python step errors: ensure `statsmodels` is installed (`pip install statsmodels`).
- If visuals show duplicates: use a single Date column in one table for the axis; relate on Dept/Category only.
- If the forecast looks flat: verify at least 24 months of history per Department×Category for a good model fit.

Enjoy! 🔧📈
