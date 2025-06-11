from flask import session, Blueprint, request, jsonify
from utils.ECDH import ECDH
from cryptography.hazmat.primitives import serialization, hashes
from base64 import b64encode, b64decode

from utils.crypto_utils import serialize_private_key, deserialize_private_key


handshake_bp = Blueprint('handshake', __name__)

@handshake_bp.route('/init-handshake', methods=['GET'])
def handshake():
    ecdh = ECDH()

    session["private_key"] = serialize_private_key(ecdh.private_key)

    return jsonify({
        "server_public_key": b64encode(ecdh.get_public_bytes()).decode(),
    })

@handshake_bp.route('/exchange', methods=['POST'])
def exchange():
    client_pub_b64 = request.json.get('client_public_key')

    client_pub_bytes = b64decode(client_pub_b64)

    private_key = deserialize_private_key(session["private_key"])
    ecdh = ECDH()

    ecdh.private_key = private_key
    ecdh.public_key = private_key.public_key()

    shared_key = ecdh.generate_shared_key(client_pub_bytes)
    shared_keyb64 = b64encode(shared_key).decode()
    session["shared_key"] = shared_keyb64

    return jsonify({
        "status": "ok",
    })
