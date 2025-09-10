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

__version__ = "1.0.0"

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
    "WEST VIRGINIA":"WV","WISCONSIN":"WI","WYOMING":"WY","DISTRICT OF COLUMBIA":"DC", "Washington DC":"DC"
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
    s = _to_series(series).astype(str).str.strip()
    s = s.map(lambda v: _ws_re.sub(" ", v) if isinstance(v, str) else v)
    if case == "lower":
        s = s.str.lower()
    elif case == "upper":
        s = s.str.upper()
    else:
        def _tc(x):
            parts = x.title().split(" ")
            small = {"Of","And","De","Van","Von","Da"}
            return " ".join(p.lower() if p in small else p for p in parts)
        s = s.map(_tc)
    if alias_map:
        key_map = {k.lower(): v for k, v in alias_map.items()}
        s = s.str.lower().map(lambda k: key_map.get(k, None)).fillna(s)
    return s.replace({"": np.nan, "nan": np.nan})


def clean_phone(series: SeriesLike, default_country: str = "US") -> pd.Series:
    s = _to_series(series).astype(str)
    digits = s.map(lambda x: _non_digits.sub("", x))
    def fmt(d, raw):
        if not d:
            return np.nan
        if len(d) == 10 and default_country == "US":
            return "+1" + d
        if 11 <= len(d) <= 15:
            return "+" + d
        if len(d) == 7 and default_country == "US":
            return d
        return raw.strip() if raw.strip() else np.nan
    return pd.Series([fmt(d, r) for d, r in zip(digits, s)], index=s.index)


def clean_number(series: SeriesLike) -> pd.Series:
    """Keep only digits (useful for ZIP codes or IDs)."""
    s = _to_series(series).astype(str)
    return s.map(lambda x: _non_digits.sub("", x)).replace({"": np.nan})


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
            if normalized_pattern in normalized_col or normalized_col in normalized_pattern:
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
    phone_col = _find_column_by_pattern(out, ['phone', 'phone_number', 'phone number', 'telephone', 'tel', 'mobile', 'cell_number', 'cell number', 'pnumber'])
    if phone_col:
        out[phone_col] = clean_phone(out[phone_col])
    
    # ZIP/Postal code patterns
    zip_col = _find_column_by_pattern(out, ['zip', 'zip_code', 'zip code', 'zipcode', 'postal_code', 'postal code', 'postcode', 'post_code'])
    if zip_col:
        out[zip_col] = clean_number(out[zip_col])
    
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
    "clean_state",
    "clean_country",
    "apply_schema",
    "auto_clean",
]
