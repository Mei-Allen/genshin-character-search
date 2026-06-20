from flask import Flask, request, render_template

app = Flask(__name__)

import os
import pandas as pd
BASE_DIR = os.path.dirname(__file__)
csv_path = os.path.join(
    BASE_DIR,
    "genshin_characters_v1.csv"
)
df = pd.read_csv(csv_path)

popular_characters = [
    {"name":"Venti","color":"#66cc99"},
    {"name":"Furina","color":"#4da6ff"},
    {"name":"Zhongli","color":"#c89b3c"},
    {"name":"Nahida","color":"#74b033"},
    {"name":"Hu Tao","color":"#ff6b6b"},
    {"name":"Kamisato Ayaka","color":"#8fe3ff"}
]

@app.route("/")
def home():
    return render_template(
        "home.html",
        popular_characters = popular_characters
    )

def get_character(name):
    result = df[df['character_name'].str.lower() == name.lower()]
    if result.empty:
        return None
    row = result.iloc[0]
    return row

def get_related_characters(region, current_name):
    result = df[
        (df["region"] == region)
        &
        (df["character_name"] != current_name)
    ]
    return result["character_name"].head(8).tolist()

def get_same_element_characters(vision, current_name):
    result = df[
        (df["vision"] == vision)
        &
        (df["character_name"] != current_name)
    ]
    return result["character_name"].head(8).tolist()

element_colors = {
    'Geo': "#eacd90",
    'Pyro': '#ff6b6b',
    'Hydro': "#62adf8",
    'Electro': "#b46dfb",
    'Cryo': '#8fe3ff',
    'Anemo': '#66cc99',
    'Dendro': "#74b033",
}

def darken(hex_color, factor=0.8):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2],16)
    g = int(hex_color[2:4],16)
    b = int(hex_color[4:6],16)
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


@app.route("/suggest")
def suggest():
    q = request.args.get("q", "")
    result = df[
        df["character_name"].str.contains(q, case=False,na=False)
    ]
    names = result["character_name"].tolist()
    return names[:5]

@app.route("/genshin")
def genshin():
    name = request.args.get("character_name")
    row = get_character(name)
    color = element_colors[row['vision']]
    dark_color = darken(color)
    if not row.empty:
        return render_template(
        "search_result.html",
        row = row,
        color = color,
        dark_color = dark_color
        )
    else:
        return '<h1>Name not found</h1>'
  

@app.route("/genshin/<name>")
def detail(name):
    row = get_character(name)
    color = element_colors[row['vision']]
    dark_color = darken(color)
    related_characters = get_related_characters(
        row["region"],
        row["character_name"]
    )
    element_characters = get_same_element_characters(
    row["vision"],
    row["character_name"]
    )
    affiliation = row["affiliation"]
    
    levels = [20,40,50,60,70,80,90]
    hp_growth = [
        int(row[f"hp_{lv}_{lv}"])
        for lv in levels
    ]
    atk_growth = [
        int(row[f"atk_{lv}_{lv}"])
        for lv in levels
    ]
    def_growth = [
        int(row[f"def_{lv}_{lv}"])
        for lv in levels
    ]
    
    rarity = row["star_rarity"]
    same_rarity = df[
        df["star_rarity"] == rarity
    ]
    avg_hp_growth = []
    for lv in levels:
        avg_hp_growth.append(
            float(same_rarity[f"hp_{lv}_{lv}"].mean())
        )
    avg_atk_growth = []
    for lv in levels:
        avg_atk_growth.append(
            float(same_rarity[f"atk_{lv}_{lv}"].mean())
        )
    avg_def_growth = []
    for lv in levels:
        avg_def_growth.append(
            float(same_rarity[f"def_{lv}_{lv}"].mean())
        )
        
    return render_template(
        "detail.html",
        row= row,
        color = color,
        dark_color = dark_color,
        related_characters = related_characters,
        element_characters = element_characters,
        affiliation = affiliation,
        hp_growth=hp_growth,
        atk_growth=atk_growth,
        def_growth=def_growth,
        avg_hp_growth=avg_hp_growth,
        avg_atk_growth=avg_atk_growth,
        avg_def_growth=avg_def_growth
    )

if __name__ == "__main__":
    app.run(debug=True)


