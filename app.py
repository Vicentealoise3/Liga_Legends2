# app.py
from flask import Flask, render_template, jsonify
from datetime import datetime
import time

# Importa tu script tal cual (debe estar en la misma carpeta)
from standings_cascade_points_desc import (
    compute_team_record_for_user,
    LEAGUE_ORDER,
)

app = Flask(__name__)

# Cache simple para no recalcular en cada request
CACHE_TTL = 120  # segundos
_cache = {"ts": 0, "rows": [], "notes": []}


def build_rows():
    """Replica la parte de tu main(): recorre LEAGUE_ORDER,
    llama compute_team_record_for_user por cada equipo y ordena los resultados.
    """
    rows = []
    for (user, team) in LEAGUE_ORDER:
        rows.append(compute_team_record_for_user(user, team))

    # Orden final: puntos desc, W desc, L asc
    rows.sort(key=lambda r: (-r["points"], -r["wins"], r["losses"]))

    # Notas de ajustes de puntos (si las hay)
    notes = [r for r in rows if r.get("points_extra")]
    return rows, notes


def get_rows_cached():
    now = time.time()
    if now - _cache["ts"] > CACHE_TTL:
        rows, notes = build_rows()
        _cache.update(ts=now, rows=rows, notes=notes)
    return _cache["rows"], _cache["notes"]


@app.route("/")
def index():
    rows, notes = get_rows_cached()
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template("index.html", rows=rows, notes=notes, last_updated=last_updated)


@app.route("/json")
def json_view():
    rows, notes = get_rows_cached()
    return jsonify({
        "rows": rows,
        "notes": notes,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    })

@app.get("/health")
def health():
    # respuesta mínima y rápida
    return {"ok": True}

@app.get("/")
def home():
    return render_template("tabla_posiciones.html")





if __name__ == "__main__":
    # Para pruebas locales
    app.run(host="0.0.0.0", port=5000, debug=True)
