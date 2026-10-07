import http.server
import socketserver
import json
import os
import uuid
from datetime import datetime

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
ORDERS_FILE = os.path.join(DIRECTORY, "orders.json")

# Ensure orders file exists
if not os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        if self.path == "/api/order":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode("utf-8"))
                order_id = "ORD-" + str(uuid.uuid4())[:8].upper()
                order_record = {
                    "order_id": order_id,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "name": data.get("name", ""),
                    "phone": data.get("phone", ""),
                    "address": data.get("address", ""),
                    "landmark": data.get("landmark", ""),
                    "payment_method": data.get("payment_method", "upi"),
                    "upi_id": "8102899986@ybl",
                    "items": data.get("items", []),
                    "total_amount": data.get("total_amount", 0),
                    "status": "PAID" if data.get("payment_method") == "upi" else "CONFIRMED"
                }

                # Save order to local orders.json
                orders = []
                if os.path.exists(ORDERS_FILE):
                    try:
                        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                            orders = json.load(f)
                    except Exception:
                        orders = []
                orders.append(order_record)
                with open(ORDERS_FILE, "w", encoding="utf-8") as f:
                    json.dump(orders, f, ensure_ascii=False, indent=2)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                response = {
                    "success": True,
                    "order": order_record,
                    "message": "ऑर्डर सफलतापूर्वक स्वीकार कर लिया गया है!"
                }
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
            return

        super().do_POST()

    def do_GET(self):
        if self.path == "/api/orders":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            orders = []
            if os.path.exists(ORDERS_FILE):
                try:
                    with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                        orders = json.load(f)
                except Exception:
                    orders = []
            self.wfile.write(json.dumps(orders, ensure_ascii=False, indent=2).encode("utf-8"))
            return
        super().do_GET()

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Backend Server running at http://localhost:{PORT}")
        httpd.serve_forever()
