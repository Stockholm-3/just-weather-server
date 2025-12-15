#!/usr/bin/env python3
"""
Generate city datasets from SimpleMaps worldcities.csv
Creates hot_cities.json and all_cities.json for autocomplete
"""

import csv
import json
import sys
import unicodedata

def normalize_city_name(name):
    """
    Normalize city name for alphabetical sorting with proper Latin transliteration.

    Special character mappings:
    - Đ/đ → D/d (Vietnamese)
    - Ø/ø → O/o (Nordic)
    - Æ/æ → AE/ae (Nordic)
    - ẞ/ß → SS/ss (German)
    - Œ/œ → OE/oe (French)
    - Plus NFD decomposition for accented characters (é→e, ñ→n, etc.)
    """
    if not name:
        return ""

    # Special character transliteration map (before NFD decomposition)
    transliteration_map = {
        'Đ': 'D', 'đ': 'd',  # Vietnamese D with stroke
        'Ð': 'D', 'ð': 'd',  # Icelandic eth
        'Ø': 'O', 'ø': 'o',  # Nordic O with stroke
        'Æ': 'AE', 'æ': 'ae',  # Nordic/Latin AE ligature
        'Œ': 'OE', 'œ': 'oe',  # Latin OE ligature
        'ẞ': 'SS', 'ß': 'ss',  # German sharp S
        'Þ': 'TH', 'þ': 'th',  # Icelandic thorn
        'Ł': 'L', 'ł': 'l',  # Polish L with stroke
    }

    # Step 1: Apply special transliterations
    result = []
    for char in name:
        if char in transliteration_map:
            result.append(transliteration_map[char])
        else:
            result.append(char)
    transliterated = ''.join(result)

    # Step 2: NFD decomposition (é → e + accent, ñ → n + tilde)
    nfd = unicodedata.normalize('NFD', transliterated)

    # Step 3: Remove combining marks and keep only valid characters
    normalized = []
    for char in nfd:
        # Skip combining marks (accents, diacritics)
        if unicodedata.category(char) == 'Mn':
            continue

        # Convert to lowercase
        char_lower = char.lower()
        c = ord(char_lower)

        # Keep only: a-z, 0-9, space, hyphen, underscore
        if ord('a') <= c <= ord('z'):
            normalized.append(char_lower)
        elif ord('0') <= c <= ord('9'):
            normalized.append(char_lower)
        elif char_lower in (' ', '-', '_'):
            normalized.append(char_lower)
        # Skip all other characters

    return ''.join(normalized)

def main():
    input_csv = "just-weather/cache/worldcities.csv"
    hot_cities_output = "just-weather/data/hot_cities.json"
    all_cities_output = "just-weather/data/all_cities.json"

    # Demo mode: 100 hot cities, 500 all cities
    HOT_CITIES_COUNT = 500
    ALL_CITIES_COUNT = 48000

    print(f"Reading from: {input_csv}")

    cities = []

    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Parse population (may be empty)
            try:
                population = int(float(row['population'])) if row['population'] else 0
            except (ValueError, KeyError):
                population = 0

            # Parse coordinates
            try:
                lat = float(row['lat'])
                lng = float(row['lng'])
            except (ValueError, KeyError):
                continue  # Skip cities without valid coordinates

            city = {
                "name": row['city'],
                "country": row['country'],
                "country_code": row['iso2'],
                "lat": lat,
                "lon": lng,
                "population": population
            }

            cities.append(city)

    print(f"Loaded {len(cities)} cities from CSV")

    # Sort all cities alphabetically by normalized name
    cities.sort(key=lambda x: normalize_city_name(x['name']))

    # Select top-N cities (already sorted alphabetically)
    hot_cities = cities[:HOT_CITIES_COUNT]
    all_cities = cities[:ALL_CITIES_COUNT]

    # Create hot_cities JSON
    hot_cities_data = {"cities": hot_cities}

    with open(hot_cities_output, 'w', encoding='utf-8') as f:
        json.dump(hot_cities_data, f, indent=2, ensure_ascii=False)

    print(f"Created {hot_cities_output} with {len(hot_cities)} cities (sorted alphabetically)")

    # Create all_cities JSON
    all_cities_data = {"cities": all_cities}

    with open(all_cities_output, 'w', encoding='utf-8') as f:
        json.dump(all_cities_data, f, indent=2, ensure_ascii=False)

    print(f"Created {all_cities_output} with {len(all_cities)} cities (sorted alphabetically)")

    # Show first 10 cities alphabetically
    print("\nFirst 10 cities alphabetically:")
    for i, city in enumerate(hot_cities[:10], 1):
        pop_m = city['population'] / 1_000_000
        normalized = normalize_city_name(city['name'])
        print(f"{i:2d}. {city['name']:<20} -> '{normalized}' ({city['country']:<20} {pop_m:>6.1f}M)")

if __name__ == "__main__":
    main()
