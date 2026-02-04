import json, time
from collections import deque, Counter
import yaml
from flask import Flask, render_template, jsonify
from kafka import KafkaConsumer

CFG_PATH = "../config/config.yaml"

def load_cfg():
    cfg = yaml.safe_load(open(CFG_PATH))
    return cfg["kafka"]["bootstrap_servers"], cfg["kafka"]["topics"]

BOOTSTRAP, TOPICS = load_cfg()
TOP_EVENTS = TOPICS.get("final", "events_final")
TOP_ALERTS = TOPICS.get("alerts", "alerts")

app = Flask(__name__)

events_buf = deque(maxlen=300)
alerts_buf = deque(maxlen=300)

def make_consumer(topic, group_id):
    return KafkaConsumer(
        topic,
        bootstrap_servers=BOOTSTRAP,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id=group_id,
        consumer_timeout_ms=500,
    )

cons_events = make_consumer(TOP_EVENTS, "soc-flask-events")
cons_alerts = make_consumer(TOP_ALERTS, "soc-flask-alerts")

def pump(consumer, buf, limit=200):
    n = 0
    for msg in consumer:
        buf.append(msg.value)
        n += 1
        if n >= limit: break
    return n

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/state")
def api_state():
    pump(cons_events, events_buf)
    pump(cons_alerts, alerts_buf)

    events = list(events_buf)
    alerts = list(alerts_buf)

    sev = Counter([(a.get("severity") or "low") for a in alerts])
    mitre_ids = []
    for a in alerts:
        m = (a.get("raw_event") or {}).get("mitre") or {}
        if m.get("technique_id"):
            mitre_ids.append(m["technique_id"])
    mitre = Counter(mitre_ids).most_common(10)

    return jsonify({
        "now": time.strftime("%d/%m/%Y %H:%M:%S"),
        "kpi": {
            "events": len(events),
            "alerts": len(alerts),
            "high": sev.get("high",0),
            "medium": sev.get("medium",0),
            "low": sev.get("low",0),
        },
        "events_recent": events[-10:],
        "alerts_recent": alerts[-10:],
        "mitre_top": [{"technique_id": t, "count": c} for t,c in mitre],
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
