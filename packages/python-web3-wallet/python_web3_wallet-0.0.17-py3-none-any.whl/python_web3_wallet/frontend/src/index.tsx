import React from "react"
import ReactDOM from "react-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { getDefaultConfig, RainbowKitProvider } from "@rainbow-me/rainbowkit";
import { WagmiProvider } from "wagmi";
import { Chain, gnosis } from "wagmi/chains";
import PythonWeb3Wallet from "./PythonWeb3Wallet";

const queryClient = new QueryClient();

// for using with forked-Gnosis chain
const gnosisRemoteAnvil = {
  id: 8564,
  name: 'Gnosis-Fork',
  nativeCurrency: {
    name: 'xDAI',
    symbol: 'XDAI',
    decimals: 18
  },
  rpcUrls: {
    default: { http: [process.env.REACT_APP_RPC_URL!] },
  },
} as const satisfies Chain;

console.log('debug', process.env.REACT_APP_DEBUG_VARIABLE);

const config = getDefaultConfig({
  appName: 'app',
  projectId: process.env.REACT_APP_RAINBOW_PROJECT_ID!,
  chains: [
    gnosis,
    gnosisRemoteAnvil
  ],
});

ReactDOM.render(
  <WagmiProvider config={config}>
    <QueryClientProvider client={queryClient}>
      <RainbowKitProvider>
        <PythonWeb3Wallet />
      </RainbowKitProvider>
    </QueryClientProvider>
  </WagmiProvider>,
  document.getElementById("root")
)