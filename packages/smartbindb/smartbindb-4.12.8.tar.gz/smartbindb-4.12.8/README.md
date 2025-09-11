# SmartBinDB

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)
![Version](https://img.shields.io/badge/Version-4.16.8-green)

A powerful asynchronous Python library for retrieving Bank Identification Number (BIN) database information, supporting lightning-fast lookups by country name, bank name, and individual BINs. Optimized for bots, MTProto API frameworks, and Python scripts, SmartBinDB is the ultimate solution for developers needing reliable and high-performance BIN data access. **This is a closed-source project, and the source code is not available for public distribution.**

## Why SmartBinDB is the Best

- **Lightning-Fast Performance**: Utilizes a pre-built binary database (`smartbin.db`) with `pickle` serialization for near-instantaneous data loading and O(1) BIN lookups, eliminating the overhead of parsing multiple JSON files.
- **Comprehensive BIN Coverage**: Ensures no BINs are skipped, with robust indexing of all entries (e.g., `515462` for US, `515452` for Spain) from the binary database, guaranteeing 100% data fidelity.
- **Seamless Integration**: Designed for easy integration with Telegram bots, MTProto API frameworks, and standalone Python scripts, with minimal dependencies for maximum compatibility.
- **Optimized for Scalability**: Supports high-throughput queries with efficient memory usage, ideal for large-scale applications and real-time bot responses.
- **Robust Error Handling**: Provides clear error messages for missing or corrupted database files, ensuring developers can quickly diagnose issues.

## Features

- **Asynchronous Operations**: Built with `asyncio` for non-blocking, high-performance data retrieval, perfect for real-time applications.
- **Flexible Lookups**: Perform searches by country code (e.g., `US`, `ES`), bank name, or specific BIN number, with optional result limits for large datasets.
- **Comprehensive BIN Data**: Returns detailed information including BIN, brand, type, issuer, country, and more, with proper country name and flag emoji support via `pycountry`.
- **Binary Database Efficiency**: Loads data exclusively from a single `smartbin.db` file, pre-indexed for speed, eliminating the need for JSON file parsing.
- **US-Specific Handling**: Aggregates data for `US`, `US1`, and `US2` country codes under a single `US` query, with a maximum limit of 8000 results for scalability.
- **Minimal Dependencies**: Requires only `pycountry` and `pycountry-convert`, with `pickle` and `asyncio` provided by the Python standard library.
- **Compatible with Python 3.8+**: Works seamlessly across all modern Python versions, ensuring broad compatibility.

## Installation

Install SmartBinDB via pip:

```bash
pip install smartbindb
```

Ensure the `smartbin.db` file is present in the `smartbindb/data/` directory after installation. This pre-built binary database contains all BIN data and is required for operation.

## Usage

### Basic Asyncio Example
```python
import asyncio
from smartbindb import SmartBinDB

async def main():
    smartdb = SmartBinDB()
    print("What would you like to do?")
    print("1. BIN lookup")
    print("2. Bank based search")
    print("3. Country based search")
    choice = input("Enter your choice (1, 2, or 3): ")

    if choice == "1":
        bin_number = input("Enter BIN number: ")
        result = await smartdb.get_bin_info(bin_number)
        print("BIN info:", result)
    elif choice == "2":
        bank_name = input("Enter bank name: ")
        use_limit = input("Do you want to use a limit? (yes/no): ").lower()
        limit = None
        if use_limit == "yes":
            limit = int(input("Enter limit: "))
        result = await smartdb.get_bins_by_bank(bank_name, limit)
        print("Bank results:", result)
    elif choice == "3":
        country_code = input("Enter country code: ").upper()
        use_limit = input("Do you want to use a limit? (yes/no): ").lower()
        limit = None
        if use_limit == "yes":
            limit = int(input("Enter limit: "))
        result = await smartdb.get_bins_by_country(country_code, limit)
        print("Country results:", result)
    else:
        print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    asyncio.run(main())
```

### Example Output
For a BIN lookup (`515452`):
```python
Loaded from binary DB: 228 countries and 327013 BINs
What would you like to do?
1. BIN lookup
2. Bank based search
3. Country based search
Enter your choice (1, 2, or 3): 1
Enter BIN number: 515452
BIN info: {
    'status': 'SUCCESS',
    'data': [{
        'bin': '515452',
        'brand': 'MASTERCARD',
        'category': 'PLATINUM',
        'CardTier': 'PLATINUM MASTERCARD',
        'country_code': 'ES',
        'Type': 'DEBIT',
        'country_code_alpha3': 'ESP',
        'Country': {'A2': 'ES', 'A3': 'ESP', 'N3': '724', 'Name': 'Spain', 'Cont': 'Europe'},
        'issuer': 'OPEN BANK, S.A.',
        'phone': '',
        'type': 'DEBIT',
        'website': ''
    }],
    'count': 1,
    'filtered_by': 'bin',
    'api_owner': '@ISmartCoder',
    'api_channel': '@TheSmartDev',
    'Luhn': True
}
```

## What's New in Version 4.16.8

- **Binary Database Loading**: Replaced JSON file parsing with a single `smartbin.db` binary database, using `pickle` for ultra-fast data loading and minimal overhead.
- **No BIN Skips**: Robust indexing ensures all BINs (e.g., `515462` for US, `515452` for Spain) are loaded correctly, fixing previous issues with missing entries.
- **Optimized Performance**: Achieves "lightning fast" query times with in-memory `BIN_INDEX` for O(1) lookups and cached country data via `@lru_cache`.
- **Streamlined Dependencies**: Reduced to `pycountry` and `pycountry-convert`, leveraging Python’s standard library (`pickle`, `asyncio`) for simplicity and compatibility.
- **Enhanced Error Handling**: Clear error messages for missing or corrupted `smartbin.db`, improving developer experience.

## Why It's So Fast

SmartBinDB 4.16.8 is optimized for speed through:
- **Pre-Built Binary Database**: The `smartbin.db` file is pre-serialized using `pickle`, allowing near-instantaneous deserialization into memory, bypassing the need to parse hundreds of JSON files.
- **In-Memory Indexing**: Uses a `BIN_INDEX` dictionary for O(1) BIN lookups, ensuring queries like `/bin 515462` or `/bin 515452` return results in milliseconds.
- **Cached Country Data**: The `@lru_cache` decorator on `get_country_info` minimizes overhead for country name and flag lookups, critical for Telegram bot responses.
- **No File I/O Overhead**: Eliminates runtime JSON file access, making it ideal for high-throughput applications like bots and APIs.

## Contributing
This is a closed-source project, and contributions are not accepted at this time.

## License
This project is proprietary and not licensed for open-source use.

## Contact
- **Author**: @ISmartCoder
- **Email**: abirxdhackz.info.me@gmail.com
- **GitHub**: [abirxdhack](https://github.com/abirxdhack)
- **Documentation**: [SmartBinDB Docs](https://abirxdhack.github.io/SmartBinDBDocs/)

