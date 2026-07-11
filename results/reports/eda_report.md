# Exploratory Data Analysis Report
## Brent Oil Prices from BrentOilPrices.csv
### Data Period: 1987-07-02 00:00:00 to 2022-11-14 00:00:00

### Data Overview
- **Total Records**: 8981
- **Date Range**: 1987-07-02 00:00:00 to 2022-11-14 00:00:00
- **Price Range**: $9.10 - $143.95
- **Average Price**: $48.52

### Summary Statistics
| Metric | Value |
|--------|-------|
| Mean Log Return | 0.000178 |
| Std Log Return | 0.025571 |
| Skewness | -1.7419 |
| Kurtosis | 65.7069 |

### Stationarity Tests
- **Price Series ADF p-value**: 0.290087
- **Log Returns ADF p-value**: 0.000000

*Interpretation*: The log returns are stationary (p < 0.05), confirming our modeling approach using log returns.

### Key Observations
1. **Volatility Clustering**: Periods of high volatility tend to cluster together
2. **Fat Tails**: The return distribution exhibits excess kurtosis
3. **Mean Reversion**: Prices show mean-reverting behavior over longer horizons
4. **Structural Breaks**: Multiple periods of regime change are visible in the time series

### Figures Generated
- Time series plot of prices and returns
- Distribution plots of returns
- ACF/PACF plots
- Volatility clustering visualization

### Recommendations for Modeling
1. Use log returns for stationarity
2. Account for volatility clustering in model specification
3. Consider multiple change points to capture regime changes
4. Use Bayesian methods to quantify uncertainty in change point detection
