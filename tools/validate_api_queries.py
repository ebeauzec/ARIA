"""
Validate every query and mutation in api_queries.json against the public Active IQ GraphQL schema reference (the queries are written against it).

The schema is read from the public Apollo GraphOS Studio variant
https://studio.apollographql.com/public/ActiveIQ-Graph-Prd-API/variant/current/schema/reference
Needs: pip install graphql-core.  Run from the project folder:  python tools/validate_api_queries.py
"""
import json
import sys
import urllib.request
from pathlib import Path

from graphql import GraphQLError, build_schema, parse, validate

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server as S

GRAPH, VARIANT = "ActiveIQ-Graph-Prd-API", "current"
Q = 'query { graph(id:"%s") { variant(name:"%s") { latestPublication { publishedAt schema { document } } } } }' % (GRAPH, VARIANT)
req = urllib.request.Request("https://graphql.api.apollographql.com/api/graphql", json.dumps({"query": Q}).encode(),
                             {"content-type": "application/json", "origin": "https://studio.apollographql.com"})
pub = json.load(urllib.request.urlopen(req, timeout=60))["data"]["graph"]["variant"]["latestPublication"]
schema = build_schema(pub["schema"]["document"])
print("schema published", pub["publishedAt"])

A = S._A
vals = dict(after=A("after", "x"), scope=A("scope", "W"), product_types=A("product_types", "FILER"), nested_after=A("nested_after", "5"),
            watchlist_id="W", customer_id="C", nagp_id="N", serial="S", versions='["9.1"]', risk_ids='["R1"]', call=A("sustainability_call_scoped", "W"))
# field lists that ARIA sends inside systems_page (the others belong to other queries)
FIELD_LISTS = ["SYSTEMS_FIELDS_TAM", "SYSTEMS_FIELDS_EFFICIENCY", "SYSTEMS_FIELDS_MINIMAL", "ESERIES_CAP_FIELDS", "ONTAP_EXTRA2_FIELDS",
               "LUN_VOLUME_FIELDS", "SHELVES_SUMMARY_FIELDS", "OTHER_PRODUCT_FIELDS", "REPLACEMENT_FIELDS", "MONTHLY_STATS_FIELDS", "CAPACITY_ENERGY_FIELDS"]
bad = 0
for name in S._api_cfg()["graphql"]:
    texts = {name: S._Q(name, **vals)}
    if name == "systems_page":
        texts = {f"{name}[{f}]": S._Q(name, fields=S._frag(f), **{k: v for k, v in vals.items()}) for f in FIELD_LISTS}
    for label, text in texts.items():
        try:
            errs = [e.message for e in validate(schema, parse(text))]
        except GraphQLError as e:
            errs = ["PARSE: " + e.message]
        if errs:
            bad += 1
            print("FAIL", label, "|", errs[0][:150])
        else:
            print("ok  ", label)
sys.exit(1 if bad else 0)
