
# Bitcoin Address Dataset

> **Professional README template** for the Bitcoin Address Dataset repository.

<!-- Banner -->
<p align="center">
  <img src="assets/bitcoin-stats.svg" width="1000" alt="Bitcoin Dataset Banner">
</p>

<p align="center">
  <a href="https://github.com/rijol95-web3/bitcoin-tools/actions/workflows/update-bitcoin-banner.yml">
    <img src="https://github.com/rijol95-web3/bitcoin-tools/actions/workflows/update-bitcoin-banner.yml/badge.svg" alt="Live Banner">
  </a>
  <img src="https://img.shields.io/github/license/rijol95-web3/bitcoin-tools">
  <img src="https://img.shields.io/github/stars/rijol95-web3/bitcoin-tools">
  <img src="https://img.shields.io/github/forks/rijol95-web3/bitcoin-tools">
  <img src="https://img.shields.io/github/repo-size/rijol95-web3/bitcoin-tools">
  <img src="https://img.shields.io/github/last-commit/rijol95-web3/bitcoin-tools">
</p>

A curated dataset containing **56,701,876 Bitcoin addresses**, distributed as **94 optimized 24 MiB chunks** for blockchain research, indexing, analytics, and balance scanning.

---

# Features

- 56,701,876 Bitcoin addresses
- 94 optimized chunks
- One address per line
- UTF-8 text format
- Merge utility
- Windows balance checker
- SQLite progress database
- Resume interrupted scans
- GitHub Actions live BTC banner
- Automatic banner updates

---

# Dataset Information

| Property | Value |
|---|---:|
| Network | Bitcoin Mainnet |
| Addresses | 56,701,876 |
| Chunks | 94 |
| Chunk Size | 24 MiB |
| Format | TXT |
| Encoding | UTF-8 |

---

# Repository Layout

```text
bitcoin-tools/
│
├── btc addresses/
├── assets/
├── scripts/
├── .github/workflows/
├── btc-balance-checker.exe
├── merge_chunks.py
└── README.md
```

---

# Clone

```bash
git clone https://github.com/rijol95-web3/bitcoin-tools.git
cd bitcoin-tools
```

---

# Merge Dataset

```bash
python merge_chunks.py
```

Output:

```text
btc_addresses.txt
```

---

# Balance Checker

Run:

```bat
btc-balance-checker.exe
```

The application automatically:

- Reads all chunk files
- Validates Bitcoin addresses
- Queries multiple public APIs
- Stores progress in SQLite
- Can resume after interruption
- Exports checked results
- Saves positive balances separately

---

# Command Examples

```bat
btc-balance-checker.exe
btc-balance-checker.exe --limit 100
btc-balance-checker.exe --workers 4
btc-balance-checker.exe --delay 0.5
btc-balance-checker.exe --confirmed-only
btc-balance-checker.exe --retry-errors
btc-balance-checker.exe --export-only
btc-balance-checker.exe --help
```

---

# Generated Files

- balance_progress.sqlite3
- balance_results.txt
- positive_balances.txt
- balance_errors.txt

---

# Live Bitcoin Banner

The repository includes a GitHub Actions workflow that automatically updates the banner.

Displayed information:

- BTC/USD Price
- 24-hour Change
- Dataset Statistics
- Last Update Time

## 💹 Price Sources

<p align="center">

<a href="https://www.coingecko.com/" target="_blank">
<img src="https://cdn.simpleicons.org/coingecko/8DC63F" width="48" alt="CoinGecko"><br>
<b>CoinGecko</b>
</a>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;

<a href="https://www.coinbase.com/" target="_blank">
<img src="https://cdn.simpleicons.org/coinbase/0052FF" width="48" alt="Coinbase"><br>
<b>Coinbase</b>
</a>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;

<a href="https://www.kraken.com/" target="_blank">
<img src="https://cdn.simpleicons.org/kraken/5741D9" width="48" alt="Kraken"><br>
<b>Kraken</b>
</a>

</p>

The live BTC price shown in the repository banner is aggregated from multiple free public market data providers to improve reliability and provide fallback if one provider is temporarily unavailable.

Workflow:

```text
Actions
└── Update Bitcoin Price Banner
```

Run manually:

```text
Actions
→ Update Bitcoin Price Banner
→ Run workflow
```

---

# Performance

This repository contains over **56 million** Bitcoin addresses.

Scanning the entire dataset through public APIs may take a long time because of API rate limits.

For maximum performance, use a local Bitcoin node.

---

# Security

The software:

- Does NOT request private keys
- Does NOT request seed phrases
- Does NOT modify wallets
- Does NOT sign transactions
- Only reads public blockchain data

---

# Disclaimer

This repository is intended for research, education, blockchain analytics, and software development.

Bitcoin balances change over time. Results depend on the selected API provider and the current blockchain state.

---

# License

See the LICENSE file.

---

<p align="center">
Made with RiJoL95 ❤️ for the Bitcoin open-source community.
</p>
