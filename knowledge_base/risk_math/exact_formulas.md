# Institutional Quantitative Risk Formulas

## 1. Position Sizing Formula
$$\text{Position Size Capital} = \frac{\text{Total Account Equity} \times \text{Risk Percentage per Trade}}{\text{Entry Price} - \text{Stop-Loss Price}}$$
*Purpose:* Ensures absolute capital preservation by scaling position size inversely to stop-loss distance.

## 2. Risk-to-Reward (R:R) Ratio
$$\text{R:R Ratio} = \frac{\text{Profit Target Price} - \text{Entry Price}}{\text{Entry Price} - \text{Stop-Loss Price}}$$
*Rule:* Must exceed a strict minimum **1:2 threshold** to ensure positive mathematical expectancy.

## 3. ATR Volatility Buffer
$$\text{Dynamic Stop-Loss Distance} = \text{Current ATR (14-period)} \times \text{Multiplier}$$
*Multipliers:* Use **1.5x** for Traditional Equities and **2.5x** for High-Volatility Memecoins to account for structural volatility variances.

## 4. Event-Driven Sizing Modifier
If high-impact macro news (CPI, FOMC) or unexpected product announcements occur within 24 hours, automatically multiply final position size by **0.50** (50% risk reduction) to mitigate binary slippage.
