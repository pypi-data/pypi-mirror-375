"""
cleanroom: tiny, extensible pandas utilities for aliasing + basic cleaning

Design goals:
- **Simple**: small set of pure functions you can compose
- **Extensible**: pass custom alias maps; minimal defaults
- **Flexible I/O**: works on `pd.Series`, a DataFrame column, or entire DataFrame

Public API:
- `clean_email(series)` -> Series
- `clean_name(series, alias_map=None, case="title")` -> Series
- `clean_phone(series, default_country="US")` -> Series
- `clean_number(series)` -> Series (digits only, e.g. ZIP or IDs)
- `clean_state(series, state_map=None)` -> Series
- `clean_country(series, country_map=None)` -> Series
- `apply_schema(df, schema)` -> DataFrame (returns a NEW df with transformed columns)
- `auto_clean(df)` -> DataFrame (auto-applies cleaners based on matching column names)
"""
from __future__ import annotations

__version__ = "1.3.4"

import re
from typing import Mapping, Optional, Sequence, Union, Iterable

import numpy as np
import pandas as pd

SeriesLike = Union[pd.Series, Iterable]

# -----------------
# Helper utilities
# -----------------
_ws_re = re.compile(r"\s+")
_non_digits = re.compile(r"[^0-9]")
_non_alpha_space = re.compile(r"[^A-Z ]")

DEFAULT_STATE_MAP = {
    "ALABAMA":"AL","ALASKA":"AK","ARIZONA":"AZ","ARKANSAS":"AR","CALIFORNIA":"CA",
    "COLORADO":"CO","CONNECTICUT":"CT","DELAWARE":"DE","FLORIDA":"FL","GEORGIA":"GA",
    "HAWAII":"HI","IDAHO":"ID","ILLINOIS":"IL","INDIANA":"IN","IOWA":"IA","KANSAS":"KS",
    "KENTUCKY":"KY","LOUISIANA":"LA","MAINE":"ME","MARYLAND":"MD","MASSACHUSETTS":"MA",
    "MICHIGAN":"MI","MINNESOTA":"MN","MISSISSIPPI":"MS","MISSOURI":"MO","MONTANA":"MT",
    "NEBRASKA":"NE","NEVADA":"NV","NEW HAMPSHIRE":"NH","NEW JERSEY":"NJ","NEW MEXICO":"NM",
    "NEW YORK":"NY","NORTH CAROLINA":"NC","NORTH DAKOTA":"ND","OHIO":"OH","OKLAHOMA":"OK",
    "OREGON":"OR","PENNSYLVANIA":"PA","RHODE ISLAND":"RI","SOUTH CAROLINA":"SC","SOUTH DAKOTA":"SD",
    "TENNESSEE":"TN","TEXAS":"TX","UTAH":"UT","VERMONT":"VT","VIRGINIA":"VA","WASHINGTON":"WA",
    "WEST VIRGINIA":"WV","WISCONSIN":"WI","WYOMING":"WY","DISTRICT OF COLUMBIA":"DC", "Washington DC":"DC", "PENSYLVENIA":"PA", "Washington, DC":"DC", "D.C.": "DC"
}

DEFAULT_COUNTRY_MAP = {
    "US":"US","USA":"US","UNITED STATES":"US","UNITED STATES OF AMERICA":"US","AMERICA":"US",
    "CANADA":"CA","CAN":"CA","CA":"CA", 
    "UK":"GB","UNITED KINGDOM":"GB","BRITAIN":"GB","GB":"GB",
    "AUSTRALIA":"AU","AU":"AU","AUS":"AU",
    "NEW ZEALAND":"NZ","NZ":"NZ","NZL":"NZ",
    "SOUTH AFRICA":"ZA","ZA":"ZA","ZAF":"ZA",
    "SOUTH KOREA":"KR","KR":"KR","KOR":"KR",
    "JAPAN":"JP","JP":"JP","JPN":"JP",
    "CHINA":"CN","CN":"CN","CHN":"CN",
    "MEXICO":"MX","MX":"MX","MEX":"MX",
    "PUERTO RICO":"PR","PR":"PR","PRI":"PR",
}


def _to_series(x: SeriesLike, name: Optional[str] = None) -> pd.Series:
    if isinstance(x, pd.Series):
        return x
    return pd.Series(list(x), name=name)


def _first_non_null(df: pd.DataFrame, cols: Sequence[str]) -> pd.Series:
    sel = [df[c] if c in df.columns else pd.Series([np.nan]*len(df)) for c in cols]
    out = sel[0].copy()
    for s in sel[1:]:
        out = out.where(out.notna() & (out.astype(str).str.len()>0), s)
    return out


# -----------------
# Cleaning functions
# -----------------

def clean_email(series: SeriesLike) -> pd.Series:
    s = _to_series(series).astype(str).str.strip().str.lower()
    return s.replace({"nan": np.nan})


def clean_name(series: SeriesLike, alias_map: Optional[Mapping[str, str]] = None, case: str = "title") -> pd.Series:
    """Clean names with simple capitalization: first letter uppercase, rest lowercase."""
    s = _to_series(series).astype(str).str.strip()
    s = s.map(lambda v: _ws_re.sub(" ", v) if isinstance(v, str) else v)
    
    def simple_capitalize(name_str):
        if pd.isna(name_str) or name_str in ['', 'nan', 'NaN']:
            return np.nan
        
        # Convert to string and strip
        name_str = str(name_str).strip()
        if not name_str:
            return np.nan
            
        # Simple capitalization: first letter upper, rest lower
        return name_str[0].upper() + name_str[1:].lower() if len(name_str) > 0 else name_str
    
    s = s.map(simple_capitalize)
    
    if alias_map:
        key_map = {k.lower(): v for k, v in alias_map.items()}
        s = s.str.lower().map(lambda k: key_map.get(k, None)).fillna(s)
    
    return s.replace({"": np.nan, "nan": np.nan})


def clean_phone(series: SeriesLike, default_country: str = "US") -> pd.Series:
    """Clean phone numbers to return just 10 digits (no formatting)."""
    s = _to_series(series).astype(str)
    
    def clean_single_phone(phone_str):
        if pd.isna(phone_str) or phone_str in ['', 'nan', 'NaN']:
            return np.nan
        
        # Extract only digits
        digits = _non_digits.sub("", str(phone_str))
        
        if not digits:
            return np.nan
        
        # Handle different digit lengths
        if len(digits) == 10:
            # Perfect 10-digit US phone number
            return digits
        elif len(digits) == 11 and digits.startswith('1'):
            # 11 digits starting with 1 (US country code) - remove the 1
            return digits[1:]
        elif len(digits) == 7:
            # 7-digit local number - keep as is for now
            return digits
        elif len(digits) > 11:
            # International or invalid - return original if it has some digits
            return digits
        else:
            # Less than 7 digits or other edge cases
            return digits if digits else np.nan
    
    return s.map(clean_single_phone)


def clean_number(series: SeriesLike) -> pd.Series:
    """Keep only digits (useful for IDs, but not recommended for ZIP codes)."""
    s = _to_series(series).astype(str)
    return s.map(lambda x: _non_digits.sub("", x)).replace({"": np.nan})


def clean_zip(series: SeriesLike) -> pd.Series:
    """Clean ZIP codes, preserving hyphens for ZIP+4 format (12345-6789)."""
    s = _to_series(series).astype(str).str.strip()
    
    def clean_single_zip(zip_str):
        if pd.isna(zip_str) or zip_str in ['', 'nan', 'NaN']:
            return np.nan
        
        # Remove everything except digits and hyphens
        cleaned = re.sub(r'[^0-9\-]', '', str(zip_str))
        
        if not cleaned:
            return np.nan
        
        # Handle different ZIP formats
        if '-' in cleaned:
            parts = cleaned.split('-')
            if len(parts) == 2:
                zip5, zip4 = parts
                # Validate ZIP+4 format (5 digits - 4 digits)
                if len(zip5) == 5 and zip5.isdigit() and len(zip4) == 4 and zip4.isdigit():
                    return f"{zip5}-{zip4}"
                # If not valid ZIP+4, just return the first 5 digits if valid
                elif len(zip5) == 5 and zip5.isdigit():
                    return zip5
        
        # Handle 5-digit ZIP
        if len(cleaned) == 5 and cleaned.isdigit():
            return cleaned
        
        # Handle 9-digit ZIP without hyphen (convert to ZIP+4)
        if len(cleaned) == 9 and cleaned.isdigit():
            return f"{cleaned[:5]}-{cleaned[5:]}"
        
        # If we get here, return the cleaned string or NaN if empty
        return cleaned if cleaned else np.nan
    
    return s.map(clean_single_zip)


def clean_state(series: SeriesLike, state_map: Optional[Mapping[str, str]] = None) -> pd.Series:
    m = state_map or DEFAULT_STATE_MAP
    s = _to_series(series).astype(str).str.strip().str.upper()
    return s.map(m).fillna(s)


def clean_country(series: SeriesLike, country_map: Optional[Mapping[str, str]] = None) -> pd.Series:
    m = country_map or DEFAULT_COUNTRY_MAP
    up = _to_series(series).astype(str).str.strip().str.upper()
    up = up.map(lambda x: _non_alpha_space.sub("", x))
    return up.map(m).fillna(up)


# -----------------
# DataFrame helpers
# -----------------

def apply_schema(df: pd.DataFrame, schema: Mapping[str, Mapping]) -> pd.DataFrame:
    """Return a NEW DataFrame with the specified columns transformed."""
    out = df.copy()
    for out_col, spec in schema.items():
        func = spec["func"]
        src = spec.get("source", out_col)
        kwargs = spec.get("kwargs", {})

        if isinstance(src, list):
            series = _first_non_null(out, src)
        else:
            series = out[src] if src in out.columns else pd.Series([np.nan]*len(out))

        out[out_col] = func(series, **kwargs)
    return out


def _find_column_by_pattern(df: pd.DataFrame, patterns: list) -> Optional[str]:
    """Find the first column that matches any of the given patterns (case-insensitive)."""
    cols_lower = [col.lower() for col in df.columns]
    for pattern in patterns:
        pattern_lower = pattern.lower()
        for i, col_lower in enumerate(cols_lower):
            # Remove spaces, underscores, and common separators for matching
            normalized_col = re.sub(r'[_\s\-\.]+', '', col_lower)
            normalized_pattern = re.sub(r'[_\s\-\.]+', '', pattern_lower)
            # More precise matching: exact match or one contains the other but with length similarity
            if normalized_pattern == normalized_col:
                return df.columns[i]
            elif normalized_pattern in normalized_col and len(normalized_col) <= len(normalized_pattern) + 2:
                return df.columns[i]
            elif normalized_col in normalized_pattern and len(normalized_pattern) <= len(normalized_col) + 2:
                return df.columns[i]
    return None


def auto_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Automatically clean known columns with flexible column name matching."""
    out = df.copy()
    
    # Email patterns
    email_col = _find_column_by_pattern(out, ['email', 'e-mail', 'mail', 'email_address', 'e_mail'])
    if email_col:
        out[email_col] = clean_email(out[email_col])
    
    # First name patterns
    fname_col = _find_column_by_pattern(out, ['first_name', 'first name', 'fname', 'f_name', 'f name', 'firstname', 'given_name', 'given name'])
    if fname_col:
        out[fname_col] = clean_name(out[fname_col])
    
    # Last name patterns
    lname_col = _find_column_by_pattern(out, ['last_name', 'last name', 'lname', 'l_name', 'l name', 'lastname', 'surname', 'family_name', 'family name'])
    if lname_col:
        out[lname_col] = clean_name(out[lname_col])
    
    # Phone patterns
    phone_col = _find_column_by_pattern(out, ['phone', 'phone_number', 'phone number', 'pnumber', 'p_number', 'p number', 'telephone', 'tel', 'mobile', 'cell_number', 'cell number'])
    if phone_col:
        out[phone_col] = clean_phone(out[phone_col])
    
    # ZIP/Postal code patterns
    zip_col = _find_column_by_pattern(out, ['zip', 'zip_code', 'zip code', 'zipcode', 'postal_code', 'postal code', 'postcode', 'post_code'])
    if zip_col:
        out[zip_col] = clean_zip(out[zip_col])
    
    # State patterns
    state_col = _find_column_by_pattern(out, ['state', 'st', 'province', 'prov', 'region'])
    if state_col:
        out[state_col] = clean_state(out[state_col])
    
    # Country patterns
    country_col = _find_column_by_pattern(out, ['country', 'nation', 'nationality', 'ctry', 'c'])
    if country_col:
        out[country_col] = clean_country(out[country_col])
    
    return out


__all__ = [
    "clean_email",
    "clean_name",
    "clean_phone",
    "clean_number",
    "clean_zip",
    "clean_state",
    "clean_country",
    "apply_schema",
    "auto_clean",
]
