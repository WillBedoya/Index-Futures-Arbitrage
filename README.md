# Index Futures Arbitrage
## Brief Description
Python script that seeks to find arbitrage opportunities between an index and its respective futures contract (i.e. DJI vs. YM).

## More Detailed Description
Calculates the fair value of the futures contract and decides to enter a trade if the futures contract is overpriced/underpriced relative to the index (including bid/ask spreads). Inventory is managed by only having exposure to +/-1 contract at any time. The value of the index is priced using bid/ask prices of the stocks in the index, since the quoted index price considers each underlying stock's market price. This market price is a less accurate representation compared to calculating using real-time bid/ask values.

## Results

## Challenges
