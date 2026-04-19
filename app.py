from flask import Flask, request, jsonify
import re
from datetime import datetime, timedelta
import os

app = Flask(__name__)

def calculate_date(text, anchor_str, status_str):
    days_map = {"mon":0, "tue":1, "wed":2, "thu":3, "fri":4, "sat":5, "sun":6}
    anchor = datetime.strptime(anchor_str, '%Y-%m-%d')
    status = datetime.strptime(status_str, '%Y-%m-%d')
    
    match = re.search(r'(this|next)?\s*(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', text.lower())
    if not match: return None
    
    keyword, target_day = match.group(1), match.group(2)[:3]
    target_idx, anchor_idx = days_map[target_day], anchor.weekday()

    days_ahead = (target_idx - anchor_idx) % 7
    if days_ahead == 0: days_ahead = 7
    
    viewing_date = anchor + timedelta(days=days_ahead)
    if keyword == "next" and days_ahead <= 3:
        viewing_date += timedelta(days=7)

    return viewing_date

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    res_date = calculate_date(data.get('text', ''), data.get('anchor'), data.get('status'))
    
    if not res_date: return jsonify({"error": "No date found"}), 400
    
    status_dt = datetime.strptime(data.get('status'), '%Y-%m-%d')
    if res_date < status_dt:
        return jsonify({"status": "DELETE"})

    return jsonify({"viewing_date": res_date.strftime('%d/%m/%Y'), "status": "LIVE"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)