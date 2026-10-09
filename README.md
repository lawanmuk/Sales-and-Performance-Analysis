# 📊 Sales Performance Analysis  
A data analysis project exploring sales trends, top products, and customer behavior.

## 🛠️ Tools  
- Python (pandas, Matplotlib, seaborn, Plotly)
- SQL (DuckDB)
- Forecasting (statsmodels Holt-Winters)
- Streamlit (interactive dashboard)

## 📌 Key Insights  
1. **Top Category**: Technology generates the highest sales.  
2. **Best Months**: November and December are the strongest months, with November about 86% above the monthly average. 
3. **Regional Trend**: West region outperforms others.  

## 🚀 How to Run
1. Clone the repo and create a virtual environment.
2. Install the project: `pip install -e .`
3. Build all charts: `sales-analysis run` (add `--show` to open them)
4. See headline numbers: `sales-analysis summary`

## 📈 Dashboard
Install the extras and launch it:

    pip install -e ".[dashboard]"
    streamlit run app/dashboard.py

Filter by date, region, category and segment, compare against the previous period, see a 6 month forecast and download the filtered data as CSV.

## 🗄️ SQL and Forecast
    pip install -e ".[sql]"
    sales-analysis sql --list            # see the 8 queries
    sales-analysis sql top_products      # run one with DuckDB
    sales-analysis forecast              # backtest models and forecast 6 months

The queries live in `src/sales_analysis/queries/` and use window functions, CTEs and NTILE scoring.