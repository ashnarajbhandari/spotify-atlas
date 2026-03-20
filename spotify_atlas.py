import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import pandas as pd
import json

df = pd.read_csv("data/spotify-tracks-dataset.csv")

RADAR_FEATURES = ["danceability", "energy", "speechiness", "acousticness",
                  "instrumentalness", "liveness", "valence"]
SCATTER_FEATURES = RADAR_FEATURES + ["popularity", "tempo"]

genre_avgs = df.groupby("track_genre")[RADAR_FEATURES + ["popularity", "tempo", "loudness"]].mean().round(4).reset_index()

frames = []
for genre, grp in df.groupby("track_genre"):
    frames.append(grp.sample(min(80, len(grp)), random_state=42))
sample_tracks = pd.concat(frames)[
    ["track_name", "artists", "track_genre", "popularity",
     "danceability", "energy", "valence", "acousticness",
     "speechiness", "instrumentalness", "liveness", "tempo"]
].round(4).reset_index(drop=True)

top_frames = []
for genre, grp in df.groupby("track_genre"):
    top_frames.append(grp.nlargest(10, "popularity")[["track_name", "artists", "track_genre", "popularity"]])
top_tracks = pd.concat(top_frames).reset_index(drop=True)

ALL_GENRES = sorted(genre_avgs["track_genre"].tolist())

GENRE_COLORS = {
    "pop": "#FF6B9D",
    "sad": "#9775FA",
    "metal": "#FF4444",
    "classical": "#74C0FC",
    "afrobeat": "#FFD43B",
    "hip-hop": "#69DB7C",
    "jazz": "#FFA94D",
    "emo": "#DA77F2",
    "salsa": "#FF922B",
    "ambient": "#4DABF7",
    "indie": "#A9E34B",
    "dance": "#F783AC",
}
FALLBACK_COLORS = [
    "#E8C547", "#9AAFC8", "#74C0FC", "#FF6B9D", "#69DB7C",
    "#FFA94D", "#DA77F2", "#FF922B", "#4DABF7", "#A9E34B",
    "#9775FA", "#F783AC",
]

def get_color(genre, genre_list):
    if genre in GENRE_COLORS:
        return GENRE_COLORS[genre]
    idx = genre_list.index(genre) % len(FALLBACK_COLORS)
    return FALLBACK_COLORS[idx]

# Palette
BG       = "#050A1A"
CARD_BG  = "#0A1628"
BORDER   = "#4A6585"
GOLD     = "#E8C547"
TEXT     = "#E8E8F0"
SUBTEXT  = "#C8C8D8"
MUTED    = "#9AAFC8"
GRID     = "#1A2A3F"

# Top artist per genre
top_artist_per_genre = (
    df.groupby(["track_genre", "artists"])
    .size()
    .reset_index(name="count")
    .sort_values("count", ascending=False)
    .groupby("track_genre")
    .first()
    .reset_index()[["track_genre", "artists"]]
)

app = dash.Dash(__name__, title="Spotify · The Music Atlas")

def card_style():
    return {
        "backgroundColor": CARD_BG,
        "borderRadius": "4px",
        "border": f"1px solid {BORDER}",
        "padding": "24px 26px 18px",
        "transition": "border-color 0.2s ease",
    }

def chart_label(title, subtitle):
    return html.Div([
        html.Div(style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "4px"},
                 children=[
                     html.Div(style={"width": "24px", "height": "1px", "backgroundColor": GOLD}),
                     html.Span(title, style={"fontFamily": "Georgia, 'Times New Roman', serif",
                                             "fontSize": "14px", "fontWeight": "400",
                                             "color": TEXT, "letterSpacing": "0.05em"}),
                 ]),
        html.P(subtitle, style={"margin": "0 0 14px 34px", "fontSize": "11px",
                                 "color": MUTED, "letterSpacing": "0.04em"}),
    ])

app.layout = html.Div(
    style={"backgroundColor": BG, "minHeight": "100vh",
           "fontFamily": "Georgia, 'Times New Roman', serif", "color": TEXT},
    children=[

        # ── Header ────────────────────────────────────────────────────────────
        html.Div(
            style={"borderBottom": f"1px solid {BORDER}", "padding": "40px 48px 32px"},
            children=[
                html.Div(style={"display": "flex", "alignItems": "baseline", "gap": "16px", "marginBottom": "8px"},
                         children=[
                             html.H1("SPOTIFY", style={"margin": "0", "fontSize": "11px", "fontWeight": "400",
                                                        "letterSpacing": "0.3em", "color": GOLD,
                                                        "fontFamily": "Georgia, serif"}),
                             html.Div(style={"width": "1px", "height": "12px", "backgroundColor": BORDER}),
                             html.Span("THE MUSIC ATLAS", style={"fontSize": "11px", "letterSpacing": "0.3em",
                                                                   "color": MUTED, "fontWeight": "400"}),
                         ]),
                html.H2("Music by the Numbers", style={"margin": "0 0 8px", "fontSize": "38px",
                                                      "fontWeight": "400", "letterSpacing": "-0.01em",
                                                      "color": TEXT, "fontFamily": "Georgia, serif",
                                                      "fontStyle": "italic"}),
                html.P("An interactive atlas of 114,000 songs across 114 genres — mapped by the features that make them feel the way they do.",
                       style={"margin": "0 0 6px", "fontSize": "13px", "color": SUBTEXT, "letterSpacing": "0.02em"}),
                html.P("Every song is a coordinate. Every genre, a constellation.",
                       style={"margin": "0 0 20px", "fontSize": "15px", "color": SUBTEXT,
                              "fontStyle": "italic", "letterSpacing": "0.02em"}),

                # ── Curatorial note ───────────────────────────────────────────
                html.Div(
                    style={
                        "borderLeft": f"2px solid {GOLD}",
                        "paddingLeft": "16px",
                        "maxWidth": "580px",
                    },
                    children=[
                        html.P(
                            "I've always loved music. This project gave me a reason to look at it differently.",
                            style={"margin": "0", "fontSize": "12px", "color": MUTED,
                                   "fontStyle": "italic", "lineHeight": "1.7",
                                   "letterSpacing": "0.02em"}
                        ),
                    ]
                ),
            ]
        ),

        # ── Controls ──────────────────────────────────────────────────────────
        html.Div(
            style={"borderBottom": f"1px solid {BORDER}", "padding": "20px 48px",
                   "display": "flex", "alignItems": "center", "flexWrap": "wrap", "gap": "40px"},
            children=[
                html.Div([
                    html.Label("GENRES", style={"fontSize": "9px", "fontWeight": "400",
                                                 "letterSpacing": "0.25em", "color": GOLD,
                                                 "display": "block", "marginBottom": "8px",
                                                 "fontFamily": "Georgia, serif"}),
                    dcc.Dropdown(
                        id="genre-select",
                        options=[{"label": g.replace("-", " ").title(), "value": g} for g in ALL_GENRES],
                        value=["pop", "hip-hop", "jazz", "classical", "sad"],
                        multi=True,
                        placeholder="Select genres...",
                        style={"width": "480px", "fontSize": "12px"},
                    ),
                ]),
                html.Div([
                    html.Label("POPULARITY RANGE", style={"fontSize": "9px", "fontWeight": "400",
                                                           "letterSpacing": "0.25em", "color": GOLD,
                                                           "display": "block", "marginBottom": "8px",
                                                           "fontFamily": "Georgia, serif"}),
                    dcc.RangeSlider(
                        id="popularity-slider",
                        min=0, max=100, step=5, value=[0, 100],
                        marks={0: "0", 25: "25", 50: "50", 75: "75", 100: "100"},
                        tooltip={"placement": "bottom", "always_visible": False},
                        allowCross=False,
                    ),
                    html.Div(id="slider-display", style={"color": MUTED, "fontSize": "10px",
                                                          "marginTop": "4px", "letterSpacing": "0.1em"}),
                ], style={"width": "260px"}),

                html.Div([
                    html.Label("EXPLORE", style={"fontSize": "9px", "fontWeight": "400",
                                                  "letterSpacing": "0.25em", "color": GOLD,
                                                  "display": "block", "marginBottom": "8px",
                                                  "fontFamily": "Georgia, serif"}),
                    html.Button(
                        "✦ Surprise Me",
                        id="surprise-btn",
                        n_clicks=0,
                        style={
                            "backgroundColor": "transparent",
                            "border": f"1px solid {GOLD}",
                            "color": GOLD,
                            "borderRadius": "2px",
                            "padding": "8px 18px",
                            "fontSize": "11px",
                            "cursor": "none",
                            "fontFamily": "Georgia, serif",
                            "letterSpacing": "0.1em",
                            "transition": "all 0.2s ease",
                        }
                    ),
                ]),
            ],
        ),

        # ── Grid ──────────────────────────────────────────────────────────────
        html.Div(
            style={"padding": "32px 48px", "display": "grid",
                   "gridTemplateColumns": "1fr 1fr", "gap": "20px"},
            children=[

                # Radar
                html.Div(style=card_style(), className="dash-card", children=[
                    chart_label("Audio DNA",
                                "What a genre sounds like, distilled. Each axis reveals a different dimension of the music."),
                    dcc.Graph(id="radar-chart", config={"displayModeBar": False},
                              style={"height": "360px"}),
                ]),

                # Bar
                html.Div(style=card_style(), className="dash-card", children=[
                    html.Div(style={"display": "flex", "justifyContent": "space-between",
                                    "alignItems": "flex-start", "marginBottom": "4px"},
                             children=[
                                 chart_label("Feature Comparison",
                                             "Where genres diverge. Select any audio feature to see how each genre ranks on average."),
                                 dcc.Dropdown(
                                     id="bar-feature",
                                     options=[{"label": f.replace("_", " ").title(), "value": f}
                                              for f in SCATTER_FEATURES],
                                     value="danceability", clearable=False,
                                     style={"width": "150px", "fontSize": "11px"},
                                 ),
                             ]),
                    dcc.Graph(id="bar-chart", config={"displayModeBar": False},
                              style={"height": "340px"}),
                ]),

                # Scatter
                html.Div(style=card_style(), className="dash-card", children=[
                    html.Div(style={"display": "flex", "justifyContent": "space-between",
                                    "alignItems": "flex-start", "marginBottom": "4px"},
                             children=[
                                 chart_label("Constellation Map",
                                             "Every dot, a song. Plot any two features against each other to find patterns in the noise."),
                                 html.Div(style={"display": "flex", "gap": "8px", "alignItems": "center"},
                                          children=[
                                              dcc.Dropdown(id="scatter-x",
                                                           options=[{"label": f.replace("_", " ").title(), "value": f}
                                                                    for f in SCATTER_FEATURES],
                                                           value="energy", clearable=False,
                                                           style={"width": "120px", "fontSize": "11px"}),
                                              html.Span("×", style={"color": MUTED, "fontSize": "14px"}),
                                              dcc.Dropdown(id="scatter-y",
                                                           options=[{"label": f.replace("_", " ").title(), "value": f}
                                                                    for f in SCATTER_FEATURES],
                                                           value="valence", clearable=False,
                                                           style={"width": "120px", "fontSize": "11px"}),
                                          ]),
                             ]),
                    dcc.Graph(id="scatter-chart", config={"displayModeBar": False},
                              style={"height": "340px"}),
                ]),

                # Histogram
                html.Div(style=card_style(), className="dash-card", children=[
                    chart_label("Popularity Distribution",
                                "Fame is not evenly distributed. See how popularity spreads across tracks in each genre."),
                    dcc.Graph(id="hist-chart", config={"displayModeBar": False},
                              style={"height": "340px"}),
                ]),

                # Heatmap — full width
                html.Div(
                    style={**card_style(), "gridColumn": "1 / -1"},
                    className="dash-card",
                    children=[
                        html.Div(
                            style={"display": "flex", "justifyContent": "space-between",
                                   "alignItems": "flex-start", "marginBottom": "4px"},
                            children=[
                                chart_label("Feature Correlations",
                                            "How audio features relate to each other within a genre. Warmer cells mean stronger correlation."),
                                html.Div(style={"display": "flex", "alignItems": "center", "gap": "16px"},
                                         children=[
                                             html.Div(id="heatmap-artist-callout",
                                                      style={"fontSize": "11px", "color": MUTED,
                                                             "fontStyle": "italic"}),
                                             dcc.Dropdown(
                                                 id="heatmap-genre",
                                                 options=[{"label": g.replace("-", " ").title(), "value": g}
                                                          for g in ALL_GENRES],
                                                 value="pop",
                                                 clearable=False,
                                                 style={"width": "180px", "fontSize": "11px"},
                                             ),
                                         ]),
                            ],
                        ),
                        dcc.Graph(id="heatmap-chart", config={"displayModeBar": False},
                                  style={"height": "400px"}),
                    ],
                ),
            ],
        ),

        # ── Footer ────────────────────────────────────────────────────────────
        html.Div(
            style={
                "borderTop": f"1px solid {BORDER}",
                "padding": "24px 48px",
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
            },
            children=[
                html.P("Data sourced from Kaggle · Spotify Tracks Dataset",
                       style={"margin": "0", "fontSize": "11px", "color": MUTED,
                              "letterSpacing": "0.08em"}),
                html.A("kaggle.com/datasets/yashdev01/spotify-tracks-dataset",
                       href="https://www.kaggle.com/datasets/yashdev01/spotify-tracks-dataset",
                       target="_blank",
                       style={"fontSize": "11px", "color": GOLD, "letterSpacing": "0.05em",
                              "textDecoration": "none", "fontStyle": "italic"}),
                html.P("DSCI 410 · University of Oregon · Ashna Rajbhandari",
                       style={"margin": "0", "fontSize": "11px", "color": MUTED,
                              "letterSpacing": "0.08em"}),
            ],
        ),
    ],
)

app.index_string = f"""
<!DOCTYPE html>
<html>
<head>
{{%metas%}}
<title>{{%title%}}</title>
{{%favicon%}}
{{%css%}}
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; }}

  body {{
    margin: 0;
    background: {BG};
    cursor: none;
  }}

  body::after {{
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 9998;
    opacity: 0.035;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
    background-size: 200px 200px;
  }}

  #custom-cursor {{
    position: fixed;
    pointer-events: none;
    z-index: 99999;
    font-size: 14px;
    color: {GOLD};
    transform: translate(-50%, -50%);
    transition: opacity 0.2s ease;
    user-select: none;
    line-height: 1;
  }}

  #react-entry-point {{
    position: relative;
    z-index: 1;
  }}

  ::-webkit-scrollbar {{ width: 4px; }}
  ::-webkit-scrollbar-track {{ background: {BG}; }}
  ::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 2px; }}

  .dash-card {{
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
  }}
  .dash-card:hover {{
    border-color: {GOLD} !important;
    box-shadow: 0 0 20px rgba(232, 197, 71, 0.08) !important;
  }}

  #surprise-btn:hover {{
    background-color: {GOLD} !important;
    color: {BG} !important;
  }}

  .Select-control {{ background-color: {CARD_BG} !important; border: 1px solid {BORDER} !important; color: {TEXT} !important; border-radius: 2px !important; }}
  .Select-menu-outer {{ background-color: #0D1F35 !important; border: 1px solid {BORDER} !important; border-radius: 2px !important; }}
  .Select-option {{ background-color: #0D1F35 !important; color: {SUBTEXT} !important; font-size: 12px !important; }}
  .Select-option:hover, .Select-option.is-focused {{ background-color: #1A2A3F !important; color: {GOLD} !important; }}
  .Select-value-label {{ color: {TEXT} !important; font-size: 12px !important; }}
  .Select-placeholder {{ color: {MUTED} !important; font-size: 12px !important; }}
  .Select-multi-value-wrapper .Select-value {{ background-color: #1A2A3F !important; border-color: {BORDER} !important; color: {TEXT} !important; border-radius: 2px !important; }}
  .Select-value-icon {{ color: {MUTED} !important; border-right-color: {BORDER} !important; }}
  .Select-value-icon:hover {{ color: {GOLD} !important; background: transparent !important; }}
  .Select-arrow {{ border-top-color: {MUTED} !important; }}
  .Select-arrow-zone:hover .Select-arrow {{ border-top-color: {GOLD} !important; }}

  .rc-slider-track {{ background-color: {GOLD} !important; opacity: 0.7; }}
  .rc-slider-handle {{ border-color: {GOLD} !important; background-color: {BG} !important; width: 10px !important; height: 10px !important; }}
  .rc-slider-handle:hover {{ border-color: {GOLD} !important; box-shadow: 0 0 6px rgba(232,197,71,0.4) !important; }}
  .rc-slider-rail {{ background-color: {BORDER} !important; opacity: 0.4; }}
  .rc-slider-mark-text {{ color: {MUTED} !important; font-size: 10px !important; }}
</style>
</head>
<body>
<div id="custom-cursor">✦</div>
{{%app_entry%}}
<script>
  // ── Custom cursor ──
  const cursor = document.getElementById('custom-cursor');
  document.addEventListener('mousemove', e => {{
    cursor.style.left = e.clientX + 'px';
    cursor.style.top = e.clientY + 'px';
  }});
  document.addEventListener('mouseleave', () => cursor.style.opacity = '0');
  document.addEventListener('mouseenter', () => cursor.style.opacity = '1');

  // ── Starfield — create canvas dynamically ──
  const canvas = document.createElement('canvas');
  canvas.id = 'starfield';
  canvas.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:9997;';
  document.body.appendChild(canvas);
  const ctx = canvas.getContext('2d');

  function resize() {{
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }}
  resize();
  window.addEventListener('resize', resize);

  const STAR_COUNT = 250;
  const stars = Array.from({{ length: STAR_COUNT }}, () => ({{
    x: Math.random() * window.innerWidth,
    y: Math.random() * window.innerHeight,
    r: Math.random() * 1.4 + 0.3,
    alpha: Math.random() * 0.3 + 0.1,
    speed: Math.random() * 0.003 + 0.001,
    phase: Math.random() * Math.PI * 2,
  }}));

  let t = 0;
  function draw() {{
    t += 1;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    stars.forEach(s => {{
      const twinkle = s.alpha + Math.sin(t * s.speed + s.phase) * 0.2;
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(232, 232, 240, ${{Math.max(0, twinkle)}})`;
      ctx.fill();
    }});
    requestAnimationFrame(draw);
  }}

  draw();
</script>
<footer>
{{%config%}}
{{%scripts%}}
{{%renderer%}}
</footer>
</body>
</html>
"""

import json
import random

def hex_to_rgba(hex_color, opacity=0.13):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{opacity})"


@app.callback(
    Output("slider-display", "children"),
    Input("popularity-slider", "value")
)
def show_slider_value(pop_range):
    return f"{pop_range[0]} — {pop_range[1]}"


@app.callback(
    Output("genre-select", "value"),
    Input("surprise-btn", "n_clicks"),
    prevent_initial_call=True,
)
def surprise_me(n_clicks):
    return random.sample(ALL_GENRES, 5)


@app.callback(
    Output("radar-chart", "figure"),
    Input("genre-select", "value"),
)
def update_radar(genres):
    if not genres:
        return go.Figure()

    categories = [f.replace("_", " ").title() for f in RADAR_FEATURES]
    cats_closed = categories + [categories[0]]

    fig = go.Figure()
    for genre in genres:
        color = get_color(genre, genres)
        row = genre_avgs[genre_avgs["track_genre"] == genre]
        if row.empty:
            continue
        vals = [float(row[f].iloc[0]) for f in RADAR_FEATURES]
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]], theta=cats_closed,
            name=genre.replace("-", " ").title(),
            fill="toself",
            fillcolor=hex_to_rgba(color, 0.1),
            line=dict(color=color, width=1.5),
        ))

    fig.update_layout(
        paper_bgcolor="#0A1628",
        plot_bgcolor="#0A1628",
        font=dict(color="#9AAFC8", family="Georgia, serif"),
        margin=dict(l=10, r=10, t=10, b=40),
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10, color="#C8C8D8"),
                    orientation="h", y=-0.15, x=0.5, xanchor="center"),
        polar=dict(
            bgcolor="#0A1628",
            radialaxis=dict(visible=True, range=[0, 1],
                            gridcolor="#1A2A3F", linecolor="#4A6585",
                            tickfont=dict(size=8, color="#9AAFC8")),
            angularaxis=dict(gridcolor="#1A2A3F", linecolor="#4A6585",
                             tickfont=dict(size=10, color="#C8C8D8")),
        ),
        transition={"duration": 400, "easing": "cubic-in-out"},
    )
    return fig


@app.callback(
    Output("bar-chart", "figure"),
    Input("genre-select", "value"),
    Input("bar-feature", "value"),
)
def update_bar(genres, feature):
    if not genres or not feature:
        return go.Figure()
    rows = genre_avgs[genre_avgs["track_genre"].isin(genres)].sort_values(feature)
    fig = go.Figure()
    for _, row in rows.iterrows():
        genre = row["track_genre"]
        color = get_color(genre, genres)
        fig.add_trace(go.Bar(
            x=[row[feature]], y=[genre.replace("-", " ").title()],
            orientation="h", showlegend=False,
            marker=dict(color=color, opacity=0.75),
            hovertemplate=f"<b>{genre}</b><br>{feature}: %{{x:.3f}}<extra></extra>",
        ))
    fig.update_layout(
        paper_bgcolor="#0A1628",
        plot_bgcolor="#0A1628",
        font=dict(color="#9AAFC8", family="Georgia, serif"),
        margin=dict(l=110, r=10, t=10, b=40),
        xaxis=dict(title=dict(text=feature.replace("_", " ").title(), font=dict(size=10, color="#9AAFC8")),
                   gridcolor="#1A2A3F", zerolinecolor="#4A6585",
                   tickfont=dict(size=10, color="#9AAFC8")),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=11, color="#C8C8D8")),
        transition={"duration": 400, "easing": "cubic-in-out"},
    )
    return fig


@app.callback(
    Output("scatter-chart", "figure"),
    Input("genre-select", "value"),
    Input("scatter-x", "value"),
    Input("scatter-y", "value"),
    Input("popularity-slider", "value"),
)
def update_scatter(genres, x_feat, y_feat, pop_range):
    if not genres or not x_feat or not y_feat:
        return go.Figure()
    min_pop, max_pop = pop_range
    filtered = sample_tracks[
        (sample_tracks["track_genre"].isin(genres)) &
        (sample_tracks["popularity"] >= min_pop) &
        (sample_tracks["popularity"] <= max_pop)
    ]
    fig = go.Figure()
    for genre in genres:
        sub = filtered[filtered["track_genre"] == genre]
        color = get_color(genre, genres)
        fig.add_trace(go.Scatter(
            x=sub[x_feat], y=sub[y_feat], mode="markers",
            name=genre.replace("-", " ").title(),
            marker=dict(color=color, size=4, opacity=0.6, line=dict(width=0)),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                f"{x_feat}: %{{x:.2f}}<br>{y_feat}: %{{y:.2f}}<br>"
                "Popularity: %{customdata[1]}<extra></extra>"
            ),
            customdata=sub[["track_name", "popularity"]].values,
        ))
    fig.update_layout(
        paper_bgcolor="#0A1628",
        plot_bgcolor="#0A1628",
        font=dict(color="#9AAFC8", family="Georgia, serif"),
        margin=dict(l=50, r=10, t=10, b=60),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10, color="#C8C8D8"),
                    orientation="h", y=-0.28, x=0.5, xanchor="center"),
        xaxis=dict(title=dict(text=x_feat.replace("_", " ").title(), font=dict(size=10, color="#9AAFC8")),
                   gridcolor="#1A2A3F", zerolinecolor="#4A6585",
                   tickfont=dict(size=10, color="#9AAFC8")),
        yaxis=dict(title=dict(text=y_feat.replace("_", " ").title(), font=dict(size=10, color="#9AAFC8")),
                   gridcolor="#1A2A3F", zerolinecolor="#4A6585",
                   tickfont=dict(size=10, color="#9AAFC8")),
        transition={"duration": 400, "easing": "cubic-in-out"},
    )
    return fig


@app.callback(
    Output("hist-chart", "figure"),
    Input("genre-select", "value"),
    Input("popularity-slider", "value"),
)
def update_hist(genres, pop_range):
    if not genres:
        return go.Figure()
    min_pop, max_pop = pop_range
    fig = go.Figure()
    for genre in genres:
        sub = sample_tracks[
            (sample_tracks["track_genre"] == genre) &
            (sample_tracks["popularity"] >= min_pop) &
            (sample_tracks["popularity"] <= max_pop)
        ]
        color = get_color(genre, genres)
        fig.add_trace(go.Histogram(
            x=sub["popularity"], name=genre.replace("-", " ").title(),
            marker_color=color, opacity=0.6, nbinsx=20,
        ))
    fig.update_layout(
        paper_bgcolor="#0A1628",
        plot_bgcolor="#0A1628",
        font=dict(color="#9AAFC8", family="Georgia, serif"),
        margin=dict(l=50, r=10, t=10, b=60),
        barmode="overlay",
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10, color="#C8C8D8"),
                    orientation="h", y=-0.28, x=0.5, xanchor="center"),
        xaxis=dict(title=dict(text="Popularity Score", font=dict(size=10, color="#9AAFC8")),
                   gridcolor="#1A2A3F", zerolinecolor="#4A6585",
                   tickfont=dict(size=10, color="#9AAFC8")),
        yaxis=dict(title=dict(text="Track Count", font=dict(size=10, color="#9AAFC8")),
                   gridcolor="#1A2A3F", zerolinecolor="#4A6585",
                   tickfont=dict(size=10, color="#9AAFC8")),
        transition={"duration": 400, "easing": "cubic-in-out"},
    )
    return fig


@app.callback(
    Output("heatmap-chart", "figure"),
    Output("heatmap-artist-callout", "children"),
    Input("heatmap-genre", "value"),
)
def update_heatmap(genre):
    if not genre:
        return go.Figure(), ""

    sub = df[df["track_genre"] == genre][RADAR_FEATURES].corr().round(2)
    labels = [f.replace("_", " ").title() for f in RADAR_FEATURES]

    artist_row = top_artist_per_genre[top_artist_per_genre["track_genre"] == genre]
    artist_text = ""
    if not artist_row.empty:
        artist = artist_row["artists"].iloc[0]
        artist_text = f"Most represented: {artist}"

    fig = go.Figure(go.Heatmap(
        z=sub.values,
        x=labels,
        y=labels,
        colorscale=[
            [0.0,  "#050A1A"],
            [0.25, "#1A2A3F"],
            [0.5,  "#4A6585"],
            [0.75, "#9AAFC8"],
            [1.0,  "#E8C547"],
        ],
        zmin=-1, zmax=1,
        text=sub.values,
        texttemplate="%{text}",
        textfont=dict(size=10, color="#E8E8F0"),
        hoverongaps=False,
        hovertemplate="<b>%{x} × %{y}</b><br>Correlation: %{z}<extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor="#0A1628",
        plot_bgcolor="#0A1628",
        font=dict(color="#9AAFC8", family="Georgia, serif"),
        margin=dict(l=120, r=20, t=20, b=100),
        xaxis=dict(tickfont=dict(size=11, color="#C8C8D8"),
                   tickangle=-35, gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(tickfont=dict(size=11, color="#C8C8D8"),
                   gridcolor="rgba(0,0,0,0)"),
        transition={"duration": 400, "easing": "cubic-in-out"},
    )
    return fig, artist_text


server = app.server

if __name__ == "__main__":
    app.run(debug=False, port=8051, dev_tools_ui=False)
