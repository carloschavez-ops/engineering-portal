# Simple helper to print registered rules (for debugging)
# Run: python TMP_check_routes.py

from app import app

with app.test_request_context('/'):
    rules = []
    for rule in app.url_map.iter_rules():
        rules.append((str(rule), ','.join(sorted(rule.methods or [])), rule.endpoint))
    for r in sorted(rules):
        print(r)

