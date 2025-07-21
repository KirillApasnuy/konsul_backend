import hashlib
import json
from typing import List, Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from repositories.court_decision_repository import CourtDecisionRepository


class CourtIndexingService:
    def __init__(self, repository: CourtDecisionRepository):
        self.repo = repository

    async def create_es_index(self):
        if self.repo.create_index():
            return "Index created successful"

    def _extract_metadata(self, record: Dict[str, Any]) -> Dict[str, Any]:
        text = record.get("text_of_decision", "")
        date_str = record.get("date", "")
        enriched = {
            **record,
            "text_length": len(text),
            "text_hash": hashlib.md5(text.encode()).hexdigest(),
            "created_at": datetime.now().isoformat()
        }

        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y")
            enriched["year"] = date_obj.year
            enriched["month"] = date_obj.month
        except Exception:
            enriched["year"] = None
            enriched["month"] = None

        court = record.get("court", "")
        if "Москв" in court:
            enriched["court_region"] = "Москва"
        elif "Петербург" in court or "СПб" in court:
            enriched["court_region"] = "Санкт-Петербург"
        elif "област" in court:
            enriched["court_region"] = "Область"
        else:
            enriched["court_region"] = "Другой"

        case_number = record.get("case_number", "")
        if case_number.startswith("А"):
            enriched["case_category"] = "Арбитражный"
        elif case_number.startswith("К"):
            enriched["case_category"] = "Кассация"
        elif case_number.startswith("Г"):
            enriched["case_category"] = "Гражданский"
        else:
            enriched["case_category"] = "Другой"

        return enriched

    def bulk_index_jsonl(self, jsonl_file_path: str, chunk_size: int = 1000, max_workers: int = 4) -> bool:
        def process_chunk(chunk: List[Dict]):
            enriched = [self._extract_metadata(r) for r in chunk]
            return self.repo.bulk_index(enriched)

        with open(jsonl_file_path, 'r', encoding='utf-8') as f:
            chunk, futures = [], []
            executor = ThreadPoolExecutor(max_workers=max_workers)

            for line in f:
                if line.strip():
                    chunk.append(json.loads(line))
                    if len(chunk) >= chunk_size:
                        futures.append(executor.submit(process_chunk, chunk))
                        chunk = []

            if chunk:
                futures.append(executor.submit(process_chunk, chunk))

            return all(f.result() > 0 for f in futures)
