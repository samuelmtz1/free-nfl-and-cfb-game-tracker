"""
Team Colors Registry.
Provides official primary and secondary brand colors for all 32 NFL teams and major College Football programs.
"""

from typing import Dict, Tuple

# Official NFL Team Primary Colors
NFL_TEAM_COLORS: Dict[str, str] = {
    "arizona cardinals": "#97233F",
    "cardinals": "#97233F",
    "atlanta falcons": "#A71930",
    "falcons": "#A71930",
    "baltimore ravens": "#241773",
    "ravens": "#241773",
    "buffalo bills": "#00338D",
    "bills": "#00338D",
    "carolina panthers": "#0085CA",
    "panthers": "#0085CA",
    "chicago bears": "#0B162A",
    "bears": "#0B162A",
    "cincinnati bengals": "#FB4F14",
    "bengals": "#FB4F14",
    "cleveland browns": "#311D00",
    "browns": "#311D00",
    "dallas cowboys": "#003594",
    "cowboys": "#003594",
    "denver broncos": "#FB4F14",
    "broncos": "#FB4F14",
    "detroit lions": "#0076B6",
    "lions": "#0076B6",
    "green bay packers": "#203731",
    "packers": "#203731",
    "houston texans": "#03202F",
    "texans": "#03202F",
    "indianapolis colts": "#002C5F",
    "colts": "#002C5F",
    "jacksonville jaguars": "#006778",
    "jaguars": "#006778",
    "kansas city chiefs": "#E31837",
    "chiefs": "#E31837",
    "las vegas raiders": "#A5ACAF",
    "raiders": "#A5ACAF",
    "los angeles chargers": "#0080C6",
    "chargers": "#0080C6",
    "los angeles rams": "#003594",
    "rams": "#003594",
    "miami dolphins": "#008E97",
    "dolphins": "#008E97",
    "minnesota vikings": "#4F2683",
    "vikings": "#4F2683",
    "new england patriots": "#002244",
    "patriots": "#002244",
    "new orleans saints": "#D3BC8D",
    "saints": "#D3BC8D",
    "new york giants": "#0B2265",
    "giants": "#0B2265",
    "new york jets": "#125740",
    "jets": "#125740",
    "philadelphia eagles": "#004C54",
    "eagles": "#004C54",
    "pittsburgh steelers": "#FFB612",
    "steelers": "#FFB612",
    "san francisco 49ers": "#AA0000",
    "49ers": "#AA0000",
    "seattle seahawks": "#002244",
    "seahawks": "#002244",
    "tampa bay buccaneers": "#D50A0A",
    "buccaneers": "#D50A0A",
    "tennessee titans": "#0C2340",
    "titans": "#0C2340",
    "washington commanders": "#5A1414",
    "commanders": "#5A1414",
}

# Major College Football (CFB) Team Primary Colors
CFB_TEAM_COLORS: Dict[str, str] = {
    "alabama": "#9E1B32",
    "crimson tide": "#9E1B32",
    "georgia": "#BA0C2F",
    "bulldogs": "#BA0C2F",
    "ohio state": "#BB0000",
    "buckeyes": "#BB0000",
    "texas": "#BF5700",
    "longhorns": "#BF5700",
    "michigan": "#00274C",
    "wolverines": "#00274C",
    "oregon": "#154733",
    "ducks": "#154733",
    "penn state": "#041E42",
    "nittany lions": "#041E42",
    "notre dame": "#0C2340",
    "fighting irish": "#0C2340",
    "lsu": "#461D7C",
    "tigers": "#461D7C",
    "clemson": "#F56600",
    "florida state": "#782F40",
    "seminoles": "#782F40",
    "tennessee": "#FF8200",
    "volunteers": "#FF8200",
    "ole miss": "#13294B",
    "rebels": "#13294B",
    "oklahoma": "#841617",
    "sooners": "#841617",
    "usc": "#990000",
    "trojans": "#990000",
    "texas a&m": "#500000",
    "aggies": "#500000",
    "miami": "#F47321",
    "hurricanes": "#F47321",
    "utah": "#CC0000",
    "utes": "#CC0000",
    "washington": "#4B2E83",
    "huskies": "#4B2E83",
    "colorado": "#CFB87C",
    "buffaloes": "#CFB87C",
    "auburn": "#0C2340",
    "florida": "#0021A5",
    "gators": "#0021A5",
    "wisconsin": "#C5050C",
    "badgers": "#C5050C",
    "nebraska": "#E41C38",
    "cornhuskers": "#E41C38",
}

DEFAULT_NFL_COLOR = "#38bdf8"  # Cyan
DEFAULT_CFB_COLOR = "#f97316"  # Vibrant Orange


def get_team_color(team_name: str, sport: str = "NFL") -> str:
    """
    Looks up the team primary color by full name or keyword.
    
    Args:
        team_name: Team name (e.g. 'Kansas City Chiefs', '#1 Georgia', 'Cowboys').
        sport: 'NFL' or 'CFB'.
        
    Returns:
        Hex color code (e.g. '#E31837').
    """
    clean_name = team_name.lower().strip()
    # Strip ranking prefixes like '#1 ', '#14 '
    if clean_name.startswith("#"):
        parts = clean_name.split(" ", 1)
        if len(parts) > 1:
            clean_name = parts[1].strip()

    color_dict = NFL_TEAM_COLORS if sport.upper() == "NFL" else CFB_TEAM_COLORS

    # Direct match
    if clean_name in color_dict:
        return color_dict[clean_name]

    # Partial match
    for key, color in color_dict.items():
        if key in clean_name or clean_name in key:
            return color

    return DEFAULT_NFL_COLOR if sport.upper() == "NFL" else DEFAULT_CFB_COLOR
