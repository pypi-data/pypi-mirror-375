from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from .process import APIProcess, Config

class Backend:
    APP = Flask(__name__, static_folder="static", template_folder="templates")

    def __init__(self):
        CORS(self.APP)
        Config.load()

        # Add routes
        self.APP.add_url_rule('/', view_func=self.index)
        self.APP.add_url_rule('/generate', view_func=self.generate, methods=['POST'])
        self.APP.add_url_rule('/inbox', view_func=self.inbox, methods=['POST'])

        # Global error handler
        @self.APP.errorhandler(Exception)
        def handle_error(e):
            print(f"[ERROR] {type(e).__name__}: {e}", flush=True)
            return jsonify({"error": str(e)}), 500

    def index(self):
        return render_template("index.html"), 200

    def generate(self):
        try:
            # TEMP: Comment out actual email generation for debugging
            email = APIProcess.generate_email()
            _ret = {"email": email.EMAIL, "token": email.HASH}

            # Dummy response to test fetch
            # _ret = {"email": "test@example.com", "token": "12345"}
            print(f"[LOG] {_ret}", flush=True)
            return jsonify(_ret), 200

        except Exception as e:
            print(f"[EXCEPTION in /generate] {e}", flush=True)
            return jsonify({"error": str(e)}), 500

    def inbox(self):
        token = request.get_json() or {}
        print(f"[POST ReadInbox] {token}", flush=True)
        token = token.get('tk')
        if not token:
            return jsonify({"messages": []}), 404
        email = next((e for e in Config.Emails if e.HASH == token), None)
        if email is None:
            _ret = {"messages": []}
        else:
            _ret = {"messages": list(reversed(email.read_inbox()))}
        print(f"[LOG] {_ret}", flush=True)
        return jsonify(_ret), 200

    def run(self, debug, host, port):
        print(f"[STARTING BACKEND] http://{host}:{port}")
        self.APP.run(debug=debug, host=host, port=port)
