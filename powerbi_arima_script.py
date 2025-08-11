#@Owner: Marckenrold Cadet
#Power BI Python script for ARIMA/SARIMAX forecasting per Department+Category (monthly)
# Requirements: pandas, numpy, statsmodels
# In Power Query: Home > Run Python script (after enabling Python scripting in Options)
# Assumes Power BI provides a DataFrame named `dataset` with columns: Date, Department, Category, Budget, Actual

import pandas as pd
import numpy as np
from datetime import timedelta
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings

warnings.filterwarnings("ignore")

# --- Parameters ---
forecast_horizon = 12   # months
season_length = 12      # monthly seasonality

# --- Prep ---
df = dataset.copy()
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date')

# Ensure monthly frequency per group
def to_monthly(group):
    g = group.set_index('Date').asfreq('MS')
    return g

group_cols = ['Department','Category']
df_grouped = df.groupby(group_cols, as_index=False).apply(to_monthly).reset_index(level=0, drop=True).reset_index()

# Helper: fit SARIMAX with mini grid search by AIC
def fit_best_sarimax(y, seasonal=True):
    # Require at least 24 points
    if y.dropna().shape[0] < 24:
        return None, None
    orders = [(1,1,0),(1,1,1),(2,1,1)]
    seas_orders = [(1,1,0,season_length),(1,1,1,season_length)] if seasonal else [(0,0,0,0)]
    best_aic = np.inf
    best_model = None
    best_cfg = None
    for order in orders:
        for seas in seas_orders:
            try:
                model = SARIMAX(y, order=order, seasonal_order=seas, enforce_stationarity=False, enforce_invertibility=False)
                res = model.fit(disp=False)
                if res.aic < best_aic:
                    best_aic = res.aic
                    best_model = res
                    best_cfg = (order, seas)
            except Exception:
                continue
    return best_model, best_cfg

out_rows = []

for (dept, cat), g in df_grouped.groupby(group_cols):
    # Use Actuals for forecasting; if missing, fallback to Budget
    y = g['Actual'].astype(float)
    if y.isna().all():
        y = g['Budget'].astype(float)

    model, cfg = fit_best_sarimax(y, seasonal=True)
    last_date = g['Date'].max()
    # build future index
    future_index = pd.date_range((last_date + pd.offsets.MonthBegin(1)), periods=forecast_horizon, freq='MS')

    if model is not None:
        fcst = model.get_forecast(steps=forecast_horizon)
        mean = fcst.predicted_mean
        conf = fcst.conf_int(alpha=0.2)  # 80% interval
        lower = conf.iloc[:,0]
        upper = conf.iloc[:,1]
        forecast_df = pd.DataFrame({
            'Date': future_index,
            'Department': dept,
            'Category': cat,
            'Forecast': mean.values,
            'Lower': lower.values,
            'Upper': upper.values
        })
    else:
        # If not enough data, simple carry-forward
        last_val = y.dropna().iloc[-1] if not y.dropna().empty else 0.0
        forecast_df = pd.DataFrame({
            'Date': future_index,
            'Department': dept,
            'Category': cat,
            'Forecast': np.repeat(last_val, forecast_horizon),
            'Lower': np.repeat(last_val*0.9, forecast_horizon),
            'Upper': np.repeat(last_val*1.1, forecast_horizon)
        })

    hist_df = g[['Date','Department','Category','Budget','Actual']].copy()
    # Merge to long form
    hist_df['Forecast'] = np.nan
    hist_df['Lower'] = np.nan
    hist_df['Upper'] = np.nan

    combined = pd.concat([hist_df, forecast_df[['Date','Department','Category','Forecast','Lower','Upper']]], ignore_index=True, sort=False)
    out_rows.append(combined)

result = pd.concat(out_rows, ignore_index=True)
# Power BI expects a dataframe returned as `result`
result