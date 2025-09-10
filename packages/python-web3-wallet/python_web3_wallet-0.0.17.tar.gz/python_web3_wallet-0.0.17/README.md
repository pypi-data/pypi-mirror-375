# Python Web3 Wallet

Streamlit component that allows you to connect a wallet and trigger send transactions.

## Installation instructions

```sh
pip install web3-wallet-connect
```
 
## Usage instructions

```python
import streamlit as st

from python_web3_wallet import wallet_component

c = wallet_component(recipient="0x...", amount_in_ether="0.01")  # Displays RainbowKit wallet
# Optionally data (as a Hex-formatted string) can be passed to populate the data field when sending a transaction.
# c = wallet_component(recipient="0x...", amount_in_ether="0.01", data="0x78da2b492d2e0100045d01c1")
```