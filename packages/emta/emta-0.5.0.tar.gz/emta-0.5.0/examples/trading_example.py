#!/usr/bin/env python3
"""Example usage of the Eastmoney Trading Library"""

from emta import OrderType, TradingAgent


def main() -> None:
    # Create a trading agent
    agent = TradingAgent("your_username", "your_password")

    # Login to Eastmoney
    if agent.login():
        print("Successfully logged in to Eastmoney")

        # Get account information
        account_info = agent.get_account_info()
        print(f"Account balance: {account_info}")

        # Get market data
        market_data = agent.get_market_data("600000")
        print(f"Market data for 600000: {market_data}")

        # Place a buy order
        order_id = agent.place_order("600000", OrderType.BUY, 100, market_data or 10.5)
        if order_id:
            print(f"Order placed successfully with ID: {order_id}")

        # Logout
        agent.logout()
        print("Logged out successfully")
    else:
        print("Failed to log in to Eastmoney")


if __name__ == "__main__":
    main()
