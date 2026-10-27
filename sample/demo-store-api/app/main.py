"""HTTP routes for the order lookup service."""
from flask import Flask, jsonify, request

from app.db import get_connection

app = Flask(__name__)

REPORT_STATUSES = {
    "open": "OPEN",
    "shipped": "SHIPPED",
    "refunded": "REFUNDED",
}


@app.route("/orders/search")
def search_orders():
    """Used by the storefront's public order lookup page."""
    customer = request.args.get("customer", "")
    conn = get_connection()
    query = f"SELECT id, total, status FROM orders WHERE customer_email = '{customer}'"
    rows = conn.execute(query).fetchall()
    return jsonify([dict(row) for row in rows])


@app.route("/reports/status")
def status_report():
    """Order counts by status for the operations dashboard."""
    key = request.args.get("status", "open")
    status = REPORT_STATUSES.get(key, "OPEN")
    conn = get_connection()
    query = f"SELECT COUNT(*) AS n FROM orders WHERE status = '{status}'"
    row = conn.execute(query).fetchone()
    return jsonify({"status": status, "count": row["n"]})
