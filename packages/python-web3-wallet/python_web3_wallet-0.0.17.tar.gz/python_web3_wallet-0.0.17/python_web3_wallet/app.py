_RELEASE = True
import os
import streamlit.components.v1 as components


parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "frontend/build")
#component = components.declare_component("python_web3_wallet", path=build_dir)
# If loading dynamically
component = components.declare_component("python_web3_wallet", url="http://localhost:3001")

import streamlit as st
st.title('My title')
window_close = component(recipient="0x07354C0aD12741E8F222eB439cFf4c01716cA627", amountInEther="0.00001", data='0x78dacb48cdc9c95728cf2fca4901001a0b045d')
st.write(f"window close {window_close}")