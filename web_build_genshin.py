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
    return render_template(
        "detail.html",
        row= row,
        color = color,
        dark_color = dark_color
    )

if __name__ == "__main__":
    app.run(debug=True)


