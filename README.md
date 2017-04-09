# implied-volatility-smirk-trading
The Implied Volatility Smirk of Individual Option in S&P 500 Shows its Underlying Asset’s Return.

## Idea behind the strategy
Garlean, Pedersen and Poteshman(2007) find demand of index option is positively related to option expensiveness measured by implied volatility, which consequently affects the steepness of the implied volatility skew.

We can define SKEW as the different between the implied volatility of OTM put and ATM call, where implied volatility of ATM calls as the benchmark of implied volatility, because it is generally believed that ATM call are one of the most liquid options traded and should reflect investors’ consensus of the firm’s uncertainty.

If there is an overwhelming pessimistic perception of the stock, investors would tend to buy put options either for protection against future stock price drops(hedge purpose) or for a high potential return on the long put positions(speculative purpose). If there are more investors wiling to long the put than those wiling to short the put, both the price and implied volatility of the put would increase, reflecting higher demand and it leads to a steeper volatility skew.

In general, high buying pressure for puts and steep volatility skew are associated with bad news about future stock prices. Empirically, we can use OTM puts to capture the severity of the bad news. When bad news is more severe, in terms of probability and magnitude, we expect stronger buying pressure on OTM put and an increase in our SKEW variable. 

This idea is based on Yuhuang, Xiao and Zhang’s paper(What Does Individual Option Volatility Smirk Tell Us About Future Equity Returns).

## Trading based on SKEW
I firstly filter the options that their underlying assets are not in S&P 500 list, then calculating each option's implied volatility. From the daily SKEW, I caculate an average weekly SKEW of daily SKEWs from Tuesday to Tuesday. Since the smaller the SKEW, the better the stock may perform, I sorted the weekly SKEW from smallest to bigges. The trading portfolio is the first 20% of options' stocks which have the smaller weekly SKEW.

# implied_volatility.py
This program calculates the implied volatilities of individual options whose underlying assets is in S&P 500.

# daily_skew.py
This program calculate the defined SKEW.

# weekly_skew.py
This program compute the one week average of daily SKEW, from Tuesday to Tuesday.
