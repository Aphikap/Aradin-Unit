from flask import Flask, jsonify, render_template, request
from prometheus_client import Counter
from prometheus_flask_exporter import PrometheusMetrics

from conversions import CATEGORIES, ConversionError, convert, units_for

app = Flask(__name__)

metrics = PrometheusMetrics(app)
metrics.info("aradin_converter_info", "Aradin Converter app info", version="1.0.1")

# Manual counter so the README's PromQL `http_requests_total{status=~"5.."}` works.
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)


@app.after_request
def _record_request(response):
    http_requests_total.labels(
        method=request.method,
        endpoint=request.endpoint or "unknown",
        status=str(response.status_code),
    ).inc()
    return response


@app.route("/")
def index():
    return render_template(
        "index.html",
        categories=CATEGORIES,
        units={c: units_for(c) for c in CATEGORIES},
    )


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/convert", methods=["POST"])
def convert_endpoint():
    payload = request.get_json(silent=True) or {}
    try:
        category = payload["category"]
        src = payload["from"]
        dst = payload["to"]
        value = float(payload["value"])
    except (KeyError, TypeError, ValueError):
        return jsonify(error="invalid payload"), 400

    try:
        result = convert(category, src, dst, value)
    except ConversionError as exc:
        return jsonify(error=str(exc)), 400

    return jsonify(result=result, category=category, **{"from": src, "to": dst, "value": value})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
