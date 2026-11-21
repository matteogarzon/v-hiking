from itemadapter import ItemAdapter

DIFFICULTY_MAP = {"t1": "easy", "facile": "easy", "t2": "medium", "medio": "medium",
                  "t3": "hard", "difficile": "hard"}


class NormalizePipeline:
    def process_item(self, item):
        adapter = ItemAdapter(item)
        d = (adapter.get("difficulty") or "").lower()
        adapter["difficulty"] = DIFFICULTY_MAP.get(d, d or None)
        return item