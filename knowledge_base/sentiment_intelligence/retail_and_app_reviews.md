# Retail Sentiment & AI Trading App Failure Analysis

## 1. Aggregated Insights from Reddit & Trading App Reviews
- **Core Retail Complaints:** Analysis of user reviews across existing AI trading apps and community forums (r/algotrading, r/Daytrading) highlights three primary failure modes:
  1. *Overfitting to Lagging Indicators:* Apps relying purely on static RSI and MACD crossovers get severely whipped during choppy, sideways market regimes.
  2. *Ignoring Liquidity Cascades:* Generic AI models fail to account for derivative funding rates and open interest unwinds, treating crypto and equities with identical rules.
  3. *Horrible Risk-to-Reward Ratios:* Many retail tools suggest tight profit targets with wide stop-losses, resulting in a negative mathematical expectancy even with a 60% win rate.

## 2. High-Volatility Memecoin & Sentiment Velocity Rules
- **Exponential Attention Feedback Loops:** Memecoins and high-beta assets do not trade on traditional fundamentals; they trade on *sentiment velocity* (the rate of change of social media mentions and volume).
- **The Overbought Anomaly:** Traditional RSI rules dictate that an RSI > 80 signals immediate mean reversion. In high-sentiment velocity regimes, RSI can remain pinned above 80 for 5 to 10 trading sessions, punishing mean-reversion short sellers.
- **The Liquidity Cliff:** When social volume plateaus, bids vanish instantly from the order book, triggering severe, vertical downward liquidity cascades.
