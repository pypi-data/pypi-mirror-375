import asyncio
import os
import time
import pickle
import pycountry
import pycountry_convert
from typing import Optional, List, Dict
from functools import lru_cache

class SmartBinDB:
    def __init__(self):
        self.COUNTRY_JSON_DIR = os.path.join(os.path.dirname(__file__), "data")
        self.BINARY_DB = os.path.join(self.COUNTRY_JSON_DIR, "smartbin.db")
        self.BIN_INDEX = {}
        self.COUNTRY_DATA = {}
        self.START_TIME = time.time()
        self.load_data()

    def load_data(self):
        if not os.path.exists(self.BINARY_DB):
            print(f"Binary DB not found: {self.BINARY_DB}")
            return
        try:
            with open(self.BINARY_DB, 'rb') as f:
                data = pickle.load(f)
            self.COUNTRY_DATA = data.get('country_data', {})
            self.BIN_INDEX = data.get('bin_index', {})
            total_bins = len(self.BIN_INDEX)
            print(f"Loaded from binary DB: {len(self.COUNTRY_DATA)} countries and {total_bins} BINs")
        except Exception as e:
            print(f"Error loading binary DB: {str(e)}")

    @lru_cache(maxsize=256)
    def get_country_info(self, country_code: str) -> dict:
        country_code = country_code.upper()
        lookup_code = 'US' if country_code in ['US1', 'US2'] else country_code
        country = pycountry.countries.get(alpha_2=lookup_code)
        if not country:
            return {
                "A2": country_code,
                "A3": "",
                "N3": "",
                "Name": "",
                "Cont": ""
            }
        try:
            continent_code = pycountry_convert.country_alpha2_to_continent_code(country.alpha_2)
            continent = pycountry_convert.convert_continent_code_to_continent_name(continent_code)
        except Exception as e:
            print(f"Error getting continent for {country_code}: {str(e)}")
            continent = ""
        return {
            "A2": country.alpha_2,
            "A3": country.alpha_3,
            "N3": country.numeric,
            "Name": country.name,
            "Cont": continent
        }

    def format_entry(self, entry: dict, country_code: str) -> dict:
        country_info = self.get_country_info(country_code)
        return {
            "bin": entry.get('bin', ''),
            "brand": entry.get('brand', ''),
            "category": entry.get('category', ''),
            "CardTier": f"{entry.get('category', '')} {entry.get('brand', '')}".strip(),
            "country_code": country_code,
            "Type": entry.get('type', ''),
            "country_code_alpha3": entry.get('country_code_alpha3', ''),
            "Country": country_info,
            "issuer": entry.get('issuer', ''),
            "phone": entry.get('phone', ''),
            "type": entry.get('type', ''),
            "website": entry.get('website', '')
        }

    async def get_bins_by_bank(self, bank: str, limit: Optional[int] = None) -> dict:
        if not self.COUNTRY_DATA:
            self.load_data()
            if not self.COUNTRY_DATA:
                return {
                    "status": "error",
                    "message": f"Binary database not found or empty: {self.BINARY_DB}",
                    "api_owner": "@ISmartCoder",
                    "api_channel": "@TheSmartDev"
                }
        matching_bins = []
        for country_code, data in self.COUNTRY_DATA.items():
            for entry in data:
                if 'issuer' in entry and bank.lower() in entry['issuer'].lower():
                    matching_bins.append(self.format_entry(entry, country_code))
                    if limit and len(matching_bins) >= limit:
                        break
            if limit and len(matching_bins) >= limit:
                break
        if not matching_bins:
            return {
                "status": "error",
                "message": f"No matches found for bank: {bank}",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }
        return {
            "status": "SUCCESS",
            "data": matching_bins,
            "count": len(matching_bins),
            "filtered_by": "bank",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev",
            "Luhn": True
        }

    async def get_bins_by_country(self, country: str, limit: Optional[int] = None) -> dict:
        if not self.COUNTRY_DATA:
            self.load_data()
            if not self.COUNTRY_DATA:
                return {
                    "status": "error",
                    "message": f"Binary database not found or empty: {self.BINARY_DB}",
                    "api_owner": "@ISmartCoder",
                    "api_channel": "@TheSmartDev"
                }
        country = country.upper()
        if country == 'US':
            matching_bins = []
            for country_code in ['US', 'US1', 'US2']:
                if country_code in self.COUNTRY_DATA:
                    for entry in self.COUNTRY_DATA[country_code]:
                        matching_bins.append(self.format_entry(entry, country_code))
                        if limit and len(matching_bins) >= limit:
                            break
                if limit and len(matching_bins) >= limit:
                    break
            if not matching_bins:
                return {
                    "status": "error",
                    "message": "No data found for country code: US",
                    "api_owner": "@ISmartCoder",
                    "api_channel": "@TheSmartDev"
                }
            if limit is None:
                limit = 1000
            if limit > 8000:
                return {
                    "status": "error",
                    "message": "Maximum limit allowed for US is 8000",
                    "api_owner": "@ISmartCoder",
                    "api_channel": "@TheSmartDev"
                }
            return {
                "status": "SUCCESS",
                "data": matching_bins[:limit],
                "count": len(matching_bins[:limit]),
                "filtered_by": "country",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev",
                "Luhn": True
            }
        else:
            if country not in self.COUNTRY_DATA:
                return {
                    "status": "error",
                    "message": f"No data found for country code: {country}",
                    "api_owner": "@ISmartCoder",
                    "api_channel": "@TheSmartDev"
                }
            data = []
            for entry in self.COUNTRY_DATA[country]:
                data.append(self.format_entry(entry, country))
                if limit and len(data) >= limit:
                    break
            return {
                "status": "SUCCESS",
                "data": data,
                "count": len(data),
                "filtered_by": "country",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev",
                "Luhn": True
            }

    async def get_bin_info(self, bin: str) -> dict:
        if not self.BIN_INDEX:
            self.load_data()
            if not self.BIN_INDEX:
                return {
                    "status": "error",
                    "message": f"Binary database not found or empty: {self.BINARY_DB}",
                    "api_owner": "@ISmartCoder",
                    "api_channel": "@TheSmartDev"
                }
        bin = str(bin).strip()
        if bin in self.BIN_INDEX:
            country_code, entry = self.BIN_INDEX[bin]
            return {
                "status": "SUCCESS",
                "data": [self.format_entry(entry, country_code)],
                "count": 1,
                "filtered_by": "bin",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev",
                "Luhn": True
            }
        return {
            "status": "error",
            "message": f"No matches found for BIN: {bin}",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev"
        }