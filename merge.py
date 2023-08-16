import json
import glob

results = []
for fname in glob.glob('data/*.json'):
    data = json.load(open(fname, 'r', encoding='utf-8'))
    results.extend(data['reviews'])

print(f"got {len(results)} reviews in total")
json.dump(results, open('reviews.json', 'w'), indent=2)