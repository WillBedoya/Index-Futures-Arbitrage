# Index Futures Arbitrage
## Brief Description
Python script that seeks to find arbitrage opportunities between an index and its respective futures contract (i.e. DJI vs. YM).
Libraries used inlcude ib_insync, numpy, math, datetime, yfinance.

## More Detailed Description
The script calculates the fair value of a futures contract and initiates a trade if it identifies the contract as overpriced or underpriced relative to the index, taking into account the bid/ask spreads. Inventory is managed by only having exposure to +/-1 contract at any time. The value of the index is priced using bid/ask prices of the stocks in the index, since the quoted index price just considers each underlying stock's market price. This market price represents the index less accurately than a calculation based on real-time bid/ask values for each component of the index.

## Challenges
One challenging aspect of this algorithm was ensuring that the correct number of shares were purchased/sold each time an order of the futures contract was executed. Initially, I used the Dow divisor to calculate the index price and how many shares of each stock in the index were needed at any given point in time. However, it was quickly clear that such an approach would not be fully accurate since the percent weighting of each component changes over time. To address this, I calculated the number of shares of each stock purchased during the index's most recent rebalancing. The number of shares in the index doesn't change except during each rebalancing, so this was a viable solution.

Another challenge I came across was execution risk. There were times when a market order for the futures contract was filled, but not all of the market orders for each of the 30 index components were filled at the same moment. To resolve this, I decreased the throttling time from 0.05 seconds to closer to 0.5-1.0 second(s). While this diminishes the speed at which the algorithm runs, it was necessary to resolve this major problem. I am currently working on a way to resolve the execution risk challenge while not limiting the speed of the algorithm.

## Results
TBD. In this section, I intend to present a comprehensive analysis of the arbitrage opportunities identified and exploited by the script, including the frequency of these opportunities, average profit margins, and the success rate of executed trades. This analysis will highlight the effectiveness of the algorithm in real-time market conditions.
