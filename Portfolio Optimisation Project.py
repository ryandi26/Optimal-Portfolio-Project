
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import datetime as dt
import yfinance as yf
import pandas_datareader.data as web
from scipy.optimize import minimize
import statsmodels.api as sm
from additional_functions import portfolio_return, portfolio_std, equal_weight, minimum_variance, max_sharpe, simulate_portfolios, get_beta

"""# **Question 1**"""

tickers = ['JNJ', 'JPM', 'NFLX', 'NVDA', 'TSLA', '^GSPC']

start = "2024-03-20"
end = "2024-04-30"

Prices = yf.download(tickers, start, end)["Adj Close"]

Prices.rename(columns = {'JNJ':'Johnson&Johnson', 'JPM':'JPMorgan', 'NFLX':'Netflix', 'NVDA':'NVIDIA', 'TSLA':'Tesla', '^GSPC':'S&P500'}, inplace=True)

Prices.index = Prices.index.strftime('%d-%m-%Y')

Prices.dropna(inplace = True)

Returns = Prices.pct_change()*100

"""# **Question 2**"""

Risk_Free_Rate = web.DataReader('DTB4WK', 'fred', start, end)
Risk_Free_Rate.index = Risk_Free_Rate.index.strftime('%d-%m-%Y')

Risk_Free_Rate.rename(columns={'DTB4WK': 'Risk Free Rate'}, inplace=True)

Risk_Free_Rate.dropna(inplace=True)

def deannualize(annual_rate, periods=250):
    return ((1 + annual_rate/100) ** (1/periods) - 1) * 100

Daily_Risk_Free_Rate = deannualize(Risk_Free_Rate)

Daily_Risk_Free_Rate.dropna(inplace=True)

"""# **Question 4**"""

Prices.describe()

Merged_Data = Returns.join(Daily_Risk_Free_Rate)
Merged_Data.dropna(inplace=True)

Merged_Data.describe()

cov_mat = Merged_Data.iloc[:,0:5].cov()
cov_mat

cov_mat = Merged_Data.iloc[:,0:5].corr()
cov_mat

def Plot_Share_Price(data, ticker_name):
    plt.figure(figsize=(13, 5))
    plt.plot(data[ticker_name], color='green', linewidth=2)
    plt.title(f"{ticker_name} Share Price", fontweight='bold')
    plt.xlabel("Time", fontweight='bold')
    plt.ylabel("Stock Price ($)", fontweight='bold')
    plt.xticks(data.index, rotation=45)
    plt.grid(visible=True, linestyle='--', linewidth=0.7, alpha=0.7)
    plt.show()

def Plot_Stock_Returns(data, ticker_name):
    returns = data[ticker_name].pct_change() * 100
    plt.figure(figsize=(13, 5))
    plt.plot(returns, color='green', linewidth=2)
    plt.title(f"{ticker_name} Stock Returns", fontweight='bold')
    plt.xlabel("Time", fontweight='bold')
    plt.ylabel("Daily Stock Returns (%)", fontweight='bold')
    plt.xticks(data.index, rotation=45)
    plt.grid(visible=True, linestyle='--', linewidth=0.7, alpha=0.7)
    plt.show()

def Plot_Histogram(data, ticker_name):
    plt.figure(figsize=(10, 6))
    plt.hist(data[ticker_name], bins=50, color='darkgreen', edgecolor='black')
    plt.title(f"Histogram of {ticker_name} Prices", fontweight='bold')
    plt.xlabel("Price", fontweight='bold')
    plt.ylabel("Frequency", fontweight='bold')
    plt.show()

def Plot_Histogram_Returns(data, ticker_name):
    returns = data[ticker_name].pct_change() * 100  # Calculate returns
    plt.figure(figsize=(10, 6))
    plt.hist(returns.dropna(), bins=50, color='darkgreen', edgecolor='black')  # Drop NaN values for histogram
    plt.title(f"Histogram of {ticker_name} Returns", fontweight='bold')
    plt.xlabel("Returns (%)", fontweight='bold')
    plt.ylabel("Frequency", fontweight='bold')
    plt.show()

for ticker in Prices.columns:
    Plot_Share_Price(Prices, ticker)
    Plot_Stock_Returns(Prices, ticker)
    Plot_Histogram(Prices, ticker)
    Plot_Histogram_Returns(Prices, ticker)

"""# **Question 5**

**Beta Calculation**
"""

Companies = ["Johnson&Johnson", "JPMorgan", "Netflix", "NVIDIA", "Tesla"]

Excess_Returns = ({
    "Johnson&Johnson": Merged_Data["Johnson&Johnson"] - Merged_Data["Risk Free Rate"],
    "JPMorgan": Merged_Data["JPMorgan"] - Merged_Data["Risk Free Rate"],
    "Netflix": Merged_Data["Netflix"] - Merged_Data["Risk Free Rate"],
    "NVIDIA": Merged_Data["NVIDIA"] - Merged_Data["Risk Free Rate"],
    "Tesla": Merged_Data["Tesla"] - Merged_Data["Risk Free Rate"]
})

X = pd.DataFrame({"Market Risk Premium": Merged_Data["S&P500"] - Merged_Data["Risk Free Rate"]})

X = sm.add_constant(X)

Beta_Series_OLS = {}

for company in Companies:
    y = pd.DataFrame({f"Excess Return {company}": Excess_Returns[company]})

    model = sm.OLS(y, X).fit()

    Beta_Series_OLS[company] = model.params["Market Risk Premium"]

    print(f"OLS Regression Results for {company}")
    print(model.summary())
    print("\n")

Beta_Series_OLS

JNJ_Beta_OLS = Beta_Series_OLS["Johnson&Johnson"]
JPM_Beta_OLS = Beta_Series_OLS["JPMorgan"]
NFLX_Beta_OLS = Beta_Series_OLS["Netflix"]
NVDA_Beta_OLS = Beta_Series_OLS["NVIDIA"]
TSLA_Beta_OLS = Beta_Series_OLS["Tesla"]

"""**Risk and Return (Annualised)**"""

JNJ_return = np.mean(Merged_Data["Johnson&Johnson"])*250
JNJ_std = np.std(Merged_Data["Johnson&Johnson"], ddof=1)*np.sqrt(250)

JNJ_return1 = np.mean(Merged_Data["Johnson&Johnson"])
JNJ_std1 = np.std(Merged_Data["Johnson&Johnson"], ddof=1)

JPM_return = np.mean(Merged_Data["JPMorgan"])*250
JPM_std = np.std(Merged_Data["JPMorgan"], ddof=1)*np.sqrt(250)

NFLX_return = np.mean(Merged_Data["Netflix"])*250
NFLX_std = np.std(Merged_Data["Netflix"], ddof=1)*np.sqrt(250)

NVDA_return = np.mean(Merged_Data["NVIDIA"])*250
NVDA_std = np.std(Merged_Data["NVIDIA"], ddof=1)*np.sqrt(250)

TSLA_return = np.mean(Merged_Data["Tesla"])*250
TSLA_std = np.std(Merged_Data["Tesla"], ddof=1)*np.sqrt(250)
TSLA_std

RFRate_return = np.mean(Merged_Data["Risk Free Rate"])*250
RFRate_std = np.std(Merged_Data["Risk Free Rate"], ddof=1)*np.sqrt(250)

Mean_Series = [JNJ_return, JPM_return, NFLX_return, NVDA_return, TSLA_return, RFRate_return]

print("Mean Returns:")
print(Mean_Series)

STD_Series = [JNJ_std, JPM_std, NFLX_std, NVDA_std, TSLA_std, RFRate_std]

print("Mean Standard Deviation:")
print(STD_Series)

"""**Sharpe and Treynor Ratios**"""

JNJ_Sharpe_Ratio = (JNJ_return - RFRate_return)/JNJ_std

JNJ_Treynor_Ratio = (JNJ_return - RFRate_return)/JNJ_Beta_OLS

JPM_Sharpe_Ratio = (JPM_return - RFRate_return)/JPM_std

JPM_Treynor_Ratio = (JPM_return - RFRate_return)/JPM_Beta_OLS

NFLX_Sharpe_Ratio = (NFLX_return - RFRate_return)/NFLX_std

NFLX_Treynor_Ratio = (NFLX_return - RFRate_return)/NFLX_Beta_OLS

NVDA_Sharpe_Ratio = (NVDA_return - RFRate_return)/NVDA_std

NVDA_Treynor_Ratio = (NVDA_return - RFRate_return)/NVDA_Beta_OLS

TSLA_Sharpe_Ratio = (TSLA_return - RFRate_return)/TSLA_std

TSLA_Treynor_Ratio = (TSLA_return - RFRate_return)/TSLA_Beta_OLS

Sharpe_Ratio_Series = [JNJ_Sharpe_Ratio, JPM_Sharpe_Ratio, NFLX_Sharpe_Ratio, NVDA_Sharpe_Ratio, TSLA_Sharpe_Ratio]

print("Sharpe Ratios:")
print(Sharpe_Ratio_Series)

Treynor_Ratio_Series = [JNJ_Treynor_Ratio, JPM_Treynor_Ratio, NFLX_Treynor_Ratio, NVDA_Treynor_Ratio, TSLA_Sharpe_Ratio]

print("Treynor Ratios:")
print(Treynor_Ratio_Series)

"""**Daily Sharpe and Treynor Ratios**"""

JNJ_return1 = np.mean(Merged_Data["Johnson&Johnson"])
JNJ_std1 = np.std(Merged_Data["Johnson&Johnson"], ddof=1)

JPM_return1 = np.mean(Merged_Data["JPMorgan"])
JPM_std1 = np.std(Merged_Data["JPMorgan"], ddof=1)

NFLX_return1 = np.mean(Merged_Data["Netflix"])
NFLX_std1 = np.std(Merged_Data["Netflix"], ddof=1)

NVDA_return1 = np.mean(Merged_Data["NVIDIA"])
NVDA_std1 = np.std(Merged_Data["NVIDIA"], ddof=1)

TSLA_return1 = np.mean(Merged_Data["Tesla"])
TSLA_std1 = np.std(Merged_Data["Tesla"], ddof=1)

RFRate_return1 = np.mean(Merged_Data["Risk Free Rate"])
RFRate_std1 = np.std(Merged_Data["Risk Free Rate"], ddof=1)

JNJ_Sharpe_Ratio_Daily = (JNJ_return1 - RFRate_return1)/JNJ_std1

JNJ_Treynor_Ratio_Daily = (JNJ_return1 - RFRate_return1)/JNJ_Beta_OLS

JPM_Sharpe_Ratio_Daily = (JPM_return1 - RFRate_return1)/JPM_std1

JPM_Treynor_Ratio_Daily = (JPM_return1 - RFRate_return1)/JNJ_Beta_OLS

NFLX_Sharpe_Ratio_Daily = (NFLX_return1 - RFRate_return1)/NFLX_std1

NFLX_Treynor_Ratio_Daily = (NFLX_return1 - RFRate_return1)/NFLX_Beta_OLS

NVDA_Sharpe_Ratio_Daily = (NVDA_return1 - RFRate_return1)/NVDA_std1

NVDA_Treynor_Ratio_Daily = (NVDA_return1 - RFRate_return1)/NVDA_Beta_OLS

TSLA_Sharpe_Ratio_Daily = (TSLA_return1 - RFRate_return1)/TSLA_std1

TSLA_Treynor_Ratio_Daily = (TSLA_return1 - RFRate_return1)/TSLA_Beta_OLS

Daily_Sharpe_Ratio_Series = [JNJ_Sharpe_Ratio_Daily, JPM_Sharpe_Ratio_Daily, NFLX_Sharpe_Ratio_Daily, NVDA_Sharpe_Ratio_Daily, TSLA_Sharpe_Ratio_Daily]

print("Daily Sharpe Ratios:")
print(Daily_Sharpe_Ratio_Series)

Daily_Treynor_Ratio_Series = [JNJ_Treynor_Ratio_Daily, JPM_Treynor_Ratio_Daily, NFLX_Treynor_Ratio_Daily, NVDA_Treynor_Ratio_Daily, TSLA_Treynor_Ratio_Daily]

print("Daily Treynor Ratios:")
print(Daily_Treynor_Ratio_Series)

"""**Portfolio Simulation**"""

n_portfolios = 2000

portf_results = simulate_portfolios(Merged_Data.iloc[:,0:5], n_portfolios)

markers = ["o", "X", "d", "P", "1"]

fig, ax = plt.subplots(figsize=(12, 8))

portf_results.plot(kind="scatter", x="Volatility", y="Returns", c="Sharpe ratio", cmap="RdYlGn", edgecolors="black", ax=ax)

ax.set(xlabel="Volatility (Annualised)", ylabel="Expected Returns (Annualised)", title="Efficient Frontier")

Labels = ["Johnson&Johnson", "JPMorgan", "Netflix", "NVIDIA", "Tesla"]
STD_Series = [JNJ_std, JPM_std, NFLX_std, NVDA_std, TSLA_std]
Mean_Series = [JNJ_return, JPM_return, NFLX_return, NVDA_return, TSLA_return]

STD_Series = STD_Series[-5:]
Mean_Series = Mean_Series[-5:]
Labels = Labels[-5:]
markers = markers[:5]

for x, y, label, mark in zip(STD_Series, Mean_Series, Labels, markers):
  ax.scatter(x, y, label=label, marker=mark, s=75, color="red")

ax.legend(loc="upper left", bbox_to_anchor=(1.2, 1), fancybox=True, shadow=True, ncol=2)

plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.5)

plt.show()

"""# **Question 7**"""

E_weights = equal_weight(Merged_Data.iloc[:,0:5])
Portfolio_Return_EW = portfolio_return(E_weights, Merged_Data.iloc[:,0:5])
Portfolio_STD_EW1 = portfolio_std(E_weights, Merged_Data.iloc[:,0:5])

E_weights

Portfolio_Return_EW

Portfolio_STD_EW1

Selected_Stocks = Merged_Data.iloc[:, :5]

cov_matrix = Selected_Stocks.cov()
print("Covariance Matrix:\n", cov_matrix)

correlation_matrix = Selected_Stocks.corr()
print("Correlation Matrix:\n", correlation_matrix)

Portfolio_Variance_EW = np.dot(E_weights.T, np.dot(cov_matrix, E_weights))
Portfolio_Variance_EW

Portfolio_STD_EW2 = np.sqrt(Portfolio_Variance_EW)
Portfolio_STD_EW2

Portfolio_Sharpe_EW = (Portfolio_Return_EW - RFRate_return) / Portfolio_STD_EW1

Max_Sharpe_Ratio = portf_results["Sharpe ratio"].max()

print("Equal Weighted Portfolio Sharpe Ratio:", Portfolio_Sharpe_EW)
print("Maximum Sharpe Ratio from Simulated Portfolios:", Max_Sharpe_Ratio)

is_efficient = Portfolio_Sharpe_EW >= Max_Sharpe_Ratio
print("Is the Equal Weighted Portfolio Efficient?", is_efficient)

"""# **Question 8**"""

MV_weights = minimum_variance(Merged_Data.iloc[:,0:5])
Portfolio_Return_MV = portfolio_return(MV_weights, Merged_Data.iloc[:,0:5])
Portfolio_STD_MV = portfolio_std(MV_weights, Merged_Data.iloc[:,0:5])

MV_weights

Portfolio_Return_MV

Portfolio_STD_MV

MS_weights = max_sharpe(Merged_Data.iloc[:,0:5], RFRate_return)
Portfolio_Return_MS = portfolio_return(MS_weights, Merged_Data.iloc[:,0:5])
Portfolio_STD_MS = portfolio_std(MS_weights, Merged_Data.iloc[:,0:5])

MS_weights

Portfolio_Return_MS

Portfolio_STD_MS

markers = ["o", "X", "d", "P", "1"]

fig, ax = plt.subplots(figsize=(12, 8))

portf_results.plot(kind="scatter", x="Volatility", y="Returns", c="Sharpe ratio", cmap="RdYlGn", edgecolors="black", ax=ax)

ax.set(xlabel="Volatility", ylabel="Expected Returns", title="Efficient Frontier")

Mean_Series = [JNJ_return, JPM_return, NFLX_return, NVDA_return, TSLA_return]
STD_Series = [JNJ_std, JPM_std, NFLX_std, NVDA_std, TSLA_std]
Labels = ["Johnson&Johnson", "JPMorgan", "Netflix", "NVIDIA", "Tesla"]

STD_Series = STD_Series[-5:]
Mean_Series = Mean_Series[-5:]
Labels = Labels[-5:]
markers = markers[:5]

for x, y, label, mark in zip(STD_Series, Mean_Series, Labels, markers):
  ax.scatter(x, y, label=label, marker=mark, s=75, color="red")

ax.scatter(Portfolio_STD_EW2, Portfolio_Return_EW, color='fuchsia', marker='2', s=75, label='Equal Weight Portfolio')

ax.scatter(Portfolio_STD_MV, Portfolio_Return_MV, color='blue', marker='o', s=75, label='Global Minimum Variance Portfolio')

ax.scatter(Portfolio_STD_MS, Portfolio_Return_MS, color='white', edgecolor='black', marker='*', s=40, label='Max Sharpe Ratio Portfolio (100% Tesla Allocation)')

ax.legend(loc="upper left", bbox_to_anchor=(1.2, 1), fancybox=True, shadow=True, ncol=2)

plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.5)

plt.show()

"""# **Question 9 - CML**"""

markers = ["o", "X", "d", "P", "1"]

fig, ax = plt.subplots(figsize=(12, 8))

portf_results.plot(kind="scatter", x="Volatility", y="Returns", c="Sharpe ratio", cmap="RdYlGn", edgecolors="black", ax=ax)

ax.set(xlabel="Volatility", ylabel="Expected Returns", title="Efficient Frontier")

Mean_Series = [JNJ_return, JPM_return, NFLX_return, NVDA_return, TSLA_return, RFRate_return]
STD_Series = [JNJ_std, JPM_std, NFLX_std, NVDA_std, TSLA_std, RFRate_std]
Labels = ["Johnson&Johnson", "JPMorgan", "Netflix", "NVIDIA", "Tesla"]

STD_Series = STD_Series[-5:]
Mean_Series = Mean_Series[-5:]
Labels = Labels[-5:]
markers = markers[:5]

for x, y, label, mark in zip(STD_Series, Mean_Series, Labels, markers):
  ax.scatter(x, y, label=label, marker=mark, s=75, color="red")

ax.scatter(Portfolio_STD_EW2, Portfolio_Return_EW, color='fuchsia', marker='2', s=75, label='Equal Weight Portfolio')

ax.scatter(Portfolio_STD_MV, Portfolio_Return_MV, color='blue', marker='o', s=75, label='Global Minimum Variance Portfolio')

ax.scatter(Portfolio_STD_MS, Portfolio_Return_MS, color='white', edgecolor='black', marker='*', s=40, label='Max Sharpe Ratio Portfolio')

ax.plot([RFRate_std, Portfolio_STD_MS * 1.4], [RFRate_return, Portfolio_Return_MS * 1.4], "b--")

ax.legend(loc="upper left", bbox_to_anchor=(1.2, 1), fancybox=True, shadow=True, ncol=2)

plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.5)

plt.show()

"""# **Question 10 - SML**"""

JNJ_beta = get_beta(Merged_Data["Johnson&Johnson"], Merged_Data["S&P500"], Merged_Data["Risk Free Rate"])

JPM_beta = get_beta(Merged_Data["JPMorgan"], Merged_Data["S&P500"], Merged_Data["Risk Free Rate"])

NFLX_beta = get_beta(Merged_Data["Netflix"], Merged_Data["S&P500"], Merged_Data["Risk Free Rate"])

NVDA_beta = get_beta(Merged_Data["NVIDIA"], Merged_Data["S&P500"], Merged_Data["Risk Free Rate"])

TSLA_beta = get_beta(Merged_Data["Tesla"], Merged_Data["S&P500"], Merged_Data["Risk Free Rate"])

Equal_Weight_Portfolio = Merged_Data.iloc[:,0:5] @ E_weights.T

EW_beta = get_beta(Equal_Weight_Portfolio, Merged_Data["S&P500"], Merged_Data["Risk Free Rate"])

Minimum_Variance_Portfolio = Merged_Data.iloc[:,0:5] @ MV_weights.T

MV_beta = get_beta(Minimum_Variance_Portfolio, Merged_Data["S&P500"], Merged_Data["Risk Free Rate"])

Maximum_Sharpe_Portfolio = Merged_Data.iloc[:,0:5] @ MS_weights.T

MS_beta = get_beta(Maximum_Sharpe_Portfolio, Merged_Data["S&P500"], Merged_Data["Risk Free Rate"])

Beta_Series = [JNJ_beta, JPM_beta, NFLX_beta, NVDA_beta, TSLA_beta, 0, 1, EW_beta, MV_beta, MS_beta]

Mean_Series = [JNJ_return, JPM_return, NFLX_return, NVDA_return, TSLA_return, RFRate_return, np.mean(Merged_Data["S&P500"])*250, Portfolio_Return_EW, Portfolio_Return_MV, Portfolio_Return_MS]
Labels = ["Johnson&Johnson", "JPMorgan", "Netflix", "NVIDIA", "Tesla", "Risk Free Rate", "Market Index", "Equal Weight", "Minimum Variance", "Maximum Sharpe", "Market Index"]

for x, y, label in zip(Beta_Series, Mean_Series, Labels):
 plt.scatter(x, y, label=label)

plt.xlim([min(Beta_Series)-0.5, max(Beta_Series)+0.5])
plt.ylim([min(Mean_Series)-10, max(Mean_Series)+10])
plt.legend(loc="upper left", bbox_to_anchor=(1.04, 1),
fancybox=True, shadow=True, ncol=2)
plt.xlabel("Beta")
plt.ylabel("Mean (%)")
plt.title("Mean-Beta of Assets and Portfolios")

plt.plot([0, 1],[RFRate_return, np.mean(Merged_Data["S&P500"])*250], "b--")
plt.show()
