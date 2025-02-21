from flask import Flask,request # type: ignore
from _init_ import init,CANDIDATES
from _transaction_handler_ import TransactionHandler
from _tally_ import _tally


def initialize():
    print("Initializing...")
    print("This might take a few seconds...")
    init()

initialize()
app = Flask(__name__)

@app.route("/health")
def test():
    return "OK", 200

@app.route("/castVote", methods=["POST"])
def castVote():
    if request.method == "POST":
        if request.form["name"] in CANDIDATES:
            payload = {"Verb": "inc", "Name": request.form["name"], "Value": 1}
            handler = TransactionHandler(payload)
            response = handler._submit_batch()
            return TransactionHandler._check_status(response["link"])
        else:
            return "Invalid candidate name!", 400
    else:
        return "Invalid request method!", 400
    
@app.route("/tally")
def tally():
    return _tally()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)