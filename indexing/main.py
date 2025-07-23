from court_decision_search_engine import CourtDecisionSearchEngine


# Пример использования
def main():
    jsonl_path = "/data/baza350kcases.jsonl"
    search_engine = CourtDecisionSearchEngine()

    if search_engine.create_index():
        print("Индекс создан успешно")
    search_engine.bulk_index_jsonl(jsonl_path)


if __name__ == "__main__":
    main()
