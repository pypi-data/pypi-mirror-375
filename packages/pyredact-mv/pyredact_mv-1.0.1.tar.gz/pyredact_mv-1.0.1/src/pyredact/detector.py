import re
from pyredact.regex_patterns import REGEX_PATTERNS

def find_pii(text: str, types_to_scan: list[str] | None = None) -> list:
    all_matches = []
    
    patterns_to_use = REGEX_PATTERNS
    if types_to_scan:
        patterns_to_use = {key: REGEX_PATTERNS[key] for key in types_to_scan if key in REGEX_PATTERNS}

    for pii_type, pattern in patterns_to_use.items():
        for match in re.finditer(pattern, text):
            all_matches.append({'type': pii_type, 'value': match.group(0), 'start': match.start(), 'end': match.end()})

    if not all_matches:
        return []

    all_matches.sort(key=lambda x: (x['start'], -(x['end'] - x['start'])))

    final_results = []
    last_end = -1
    for match in all_matches:
        if match['start'] >= last_end:
            final_results.append(match)
            last_end = match['end']
    
    return [{'type': p['type'], 'value': p['value']} for p in final_results]