import re


def parse_query(query: str):
    """
    Если запрос содержит слова в кавычках — выделяем точные фразы для match_phrase,
    остальное — match.
    """
    # Найдём все фразы в кавычках
    phrases = re.findall(r'"([^"]+)"', query)
    # Уберём фразы из запроса
    query_cleaned = re.sub(r'"[^"]+"', '', query).strip()
    return phrases, query_cleaned
