from itemadapter import ItemAdapter

# One shared scale for all sources: easy / medium / hard.
# SchweizMobil uses the Swiss hiking scale (T1-T6), komoot uses Easy/Moderate/Difficult,
# Switzerland Tourism uses English labels (Italian ones kept just in case).
DIFFICULTY_MAP = {
    "t1": "easy", "t2": "medium", "t3": "hard", "t4": "hard", "t5": "hard", "t6": "hard",
    "easy": "easy", "facile": "easy",
    "moderate": "medium", "medium": "medium", "medio": "medium",
    "difficult": "hard", "hard": "hard", "difficile": "hard",
}


class NormalizePipeline:
    """Pipeline to normalize and clean scraped items."""

    def process_item(self, item, spider=None):
        """Map every source's difficulty label onto easy / medium / hard."""
        adapter = ItemAdapter(item)
        d = (adapter.get("difficulty") or "").strip().lower()
        adapter["difficulty"] = DIFFICULTY_MAP.get(d, d or None)
        return item