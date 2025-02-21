from _transaction_handler_ import TransactionHandler
import json

with open("candidate.json", "r") as f:
    BALLOTS = json.load(f)

CANDIDATES = [x["Name"] for x in BALLOTS["Candidates"]]

def init():
    # for ballot in BALLOTS["Candidates"]:
    #     payload = {"Verb": "set", "Name": ballot["Name"], "Value": 0}
    #     handler = TransactionHandler(payload)
    #     response = handler._submit_batch()
    #     TransactionHandler._check_status(response["link"])
    pass