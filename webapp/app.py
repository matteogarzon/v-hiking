import json
from pathlib import Path

from flask import Flask, render_template, request

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SORTABLE = ["name", "source", "difficulty", "length_km", "elevation_gain_m", "rating"]
NUMERIC = {"length_km", "elevation_gain_m", "rating"}
PER_PAGE = 50

app = Flask(__name__)

def load_trails():
    """Read every data/<spider>.jsonl file into one list of dicts."""
    trails = []
    for path in sorted(DATA_DIR.glob("*.jsonl")):
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    trails.append(json.loads(line))

    return trails

def to_number(value):
    """Spiders may store numbers as strings; convert for sorting (None if impossible)."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

@app.route("/")
def index(): 
    trails = load_trails()

    # read the filters from the URL (?q=...&source=...&difficulty=...)
    q = request.args.get("q", "").strip().lower()
    source = request.args.get("source", "")
    difficulty = request.args.get("difficulty", "")
    # type=float returns None for empty / invalid input
    min_len = request.args.get("min_len", type=float)
    max_len = request.args.get("max_len", type=float)
    sort = request.args.get("sort", "name")
    order = request.args.get("order", "asc")
    page = request.args.get("page", 1, type=int)

    # We could hard-code the values ["Komoot", "myswitzerland", ...] but this is more mantainable
    sources = sorted({t.get("source") for t in trails if t.get("source")})

    # ---- filter ----
    if q:
        trails = [
            t for t in trails
            if q in " ".join(str(t.get(k) or "") for k in ("name", "start", "via", "end", "description")).lower()
        ]
    if source:
        trails = [t for t in trails if t.get("source") == source]
    if difficulty:
        trails = [t for t in trails if t.get("difficulty") == difficulty]
    if min_len is not None or max_len is not None:
        # if bound is set -> exclude trails with no length
        def in_range(t):
            length = to_number(t.get("length_km"))
            if length is None:
                return False
            if min_len is not None and length < min_len:
                return False
            if max_len is not None and length > max_len:
                return False
            return True

        trails = [t for t in trails if in_range(t)]


    # ---- sort (missing values always go last) ----
    if sort not in SORTABLE:
        sort = "name" #fallback

    def value(t):
        if sort in NUMERIC:
            return to_number(t.get(sort))
        return (t.get(sort) or "").lower() or None

    with_value = [t for t in trails if value(t) is not None]
    without = [t for t in trails if value(t) is None]
    with_value.sort(key=value, reverse=(order == "desc"))
    trails = with_value + without

    # ---- paginate ----
    total = len(trails)
    pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    page = min(max(page, 1), pages)
    trails = trails[(page - 1) * PER_PAGE : page * PER_PAGE]

    return render_template(
        "results.html",
        trails=trails, total=total, page=page, pages=pages,
        sources=sources, q=q, source=source, difficulty=difficulty,
        min_len=min_len, max_len=max_len,
        sort=sort, order=order,
    )

if __name__ == "__main__":
    app.run(debug=True)