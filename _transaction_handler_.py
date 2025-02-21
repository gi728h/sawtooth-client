import time
import json
import cbor  # type: ignore
import urllib.request
from urllib.error import HTTPError
from hashlib import sha512
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader, Transaction # type: ignore
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader, Batch, BatchList # type: ignore
from sawtooth_signing import create_context # type: ignore
from sawtooth_signing import CryptoFactory # type: ignore


class TransactionHandler:
    def __init__(self, payload):
        self.payload_bytes = cbor.dumps(payload)

    def _create_signer(self):
        context = create_context("secp256k1")
        private_key = context.new_random_private_key()
        self.signer = CryptoFactory(context).new_signer(private_key)

    def _create_transaction_header(self):
        self._create_signer()
        self.txn_header_bytes = TransactionHeader(
            family_name="intkey",
            family_version="1.0",
            inputs=[
                "1cf1266e282c41be5e4254d8820772c5518a2c5a8c0c7f7eda19594a7eb539453e1ed7"
            ],
            outputs=[
                "1cf1266e282c41be5e4254d8820772c5518a2c5a8c0c7f7eda19594a7eb539453e1ed7"
            ],
            signer_public_key=self.signer.get_public_key().as_hex(),
            batcher_public_key=self.signer.get_public_key().as_hex(),
            dependencies=[],
            payload_sha512=sha512(self.payload_bytes).hexdigest(),
        ).SerializeToString()

    def _create_transaction(self):
        self._create_transaction_header()
        self.signature = self.signer.sign(self.txn_header_bytes)
        self.txn = Transaction(
            header=self.txn_header_bytes,
            header_signature=self.signature,
            payload=self.payload_bytes,
        )

    def _create_batch_header(self):
        self._create_transaction()
        self.txns = [self.txn]
        self.batch_header_bytes = BatchHeader(
            signer_public_key=self.signer.get_public_key().as_hex(),
            transaction_ids=[txn.header_signature for txn in self.txns],
        ).SerializeToString()

    def _create_batch(self):
        self._create_batch_header()
        self.signature = self.signer.sign(self.batch_header_bytes)
        self.batch = Batch(
            header=self.batch_header_bytes,
            header_signature=self.signature,
            transactions=self.txns
        )
    
    def _encode_batch(self):
        self._create_batch()
        self.batch_list_bytes = BatchList(batches=[self.batch]).SerializeToString()

    def _submit_batch(self):
        self._encode_batch()
        try:
            request = urllib.request.Request(
                'http://localhost:8008/batches',
                self.batch_list_bytes,
                method='POST',
                headers={'Content-Type': 'application/octet-stream'}
            )
            response = urllib.request.urlopen(request).read().decode()
        except HTTPError as e:
            response = e.file.read().decode()
        print(response)
        return json.loads(response)
    
    @staticmethod
    def _check_status(status_url):
        timeout = 500
        while timeout > 0:
            try:
                response = urllib.request.urlopen(status_url)
                status_data = json.loads(response.read().decode())
                if status_data["data"][0]["status"] == "COMMITTED":
                    print(f"Transaction with batch committed successfully!")
                    message = "Transaction with batch committed successfully!"
                    break
                else:
                    print(f"Transaction still pending. Checking again...")
                    timeout -= 2
                    time.sleep(2)  # Wait for 2 seconds before rechecking
            except HTTPError as e:
                print(f"Error checking batch status: {e.read().decode()}")
                message = f"Error checking batch status: {e.read().decode()}"
                break
        if timeout == 0:
            message = "Transaction timed out. Please check the transaction status manually here: " + status_url
            print("Transaction timed out. Please check the transaction status manually here:", status_url)
        return message

if __name__ == "__main__":
    context = create_context("secp256k1")
    print("Context created:", context)
    payload = {"Verb": "inc", "Name": "Subodh", "Value": 1}
    handler = TransactionHandler(payload)
    response = handler._submit_batch()
    TransactionHandler._check_status(response["link"])
    