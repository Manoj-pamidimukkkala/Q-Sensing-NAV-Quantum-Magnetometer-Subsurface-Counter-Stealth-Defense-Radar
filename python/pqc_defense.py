import os
import base64
import oqs
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class PQCDefenseCommunicator:
    """
    Implements NIST FIPS 203 (ML-KEM-1024) and FIPS 204 (ML-DSA-87)
    for secure defense-grade key encapsulation and digital signatures.
    """

    def __init__(self):
        self.kem_alg = "Kyber1024"  # FIPS 203 ML-KEM-1024
        self.dsa_alg = "Dilithium5" # FIPS 204 ML-DSA-87

    def generate_dsa_keypair(self) -> tuple[bytes, bytes]:
        """Generates ML-DSA-87 (Dilithium-5) signing keypair."""
        with oqs.Signature(self.dsa_alg) as signer:
            public_key = signer.generate_keypair()
            secret_key = signer.export_secret_key()
            return public_key, secret_key

    def sign_tactical_message(self, message: bytes, secret_key: bytes) -> bytes:
        """Signs tactical telemetry using ML-DSA-87."""
        with oqs.Signature(self.dsa_alg, secret_key) as signer:
            signature = signer.sign(message)
            return signature

    def verify_tactical_message(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """Verifies ML-DSA-87 signature for authenticity."""
        with oqs.Signature(self.dsa_alg) as verifier:
            return verifier.verify(message, signature, public_key)

    def encapsulate_key(self, recipient_kem_public_key: bytes) -> tuple[bytes, bytes]:
        """
        Sender side: Encapsulates a shared secret using recipient's ML-KEM-1024 public key.
        Returns (ciphertext, shared_secret).
        """
        with oqs.KeyEncapsulation(self.kem_alg) as client:
            ciphertext, shared_secret = client.encap_secret(recipient_kem_public_key)
            return ciphertext, shared_secret

    def decapsulate_key(self, ciphertext: bytes, secret_key: bytes) -> bytes:
        """
        Recipient side: Decapsulates ciphertext to recover the ML-KEM shared secret.
        """
        with oqs.KeyEncapsulation(self.kem_alg, secret_key) as server:
            shared_secret = server.decap_secret(ciphertext)
            return shared_secret

    @staticmethod
    def encrypt_aes_gcm(plaintext: bytes, shared_secret: bytes) -> tuple[bytes, bytes, bytes]:
        """Encrypts message payload using AES-256-GCM authenticated encryption."""
        # Derive 256-bit symmetric key from PQC shared secret
        aes_key = shared_secret[:32]
        cipher = AES.new(aes_key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        return ciphertext, cipher.nonce, tag

    @staticmethod
    def decrypt_aes_gcm(ciphertext: bytes, nonce: bytes, tag: bytes, shared_secret: bytes) -> bytes:
        """Decrypts AES-256-GCM message payload."""
        aes_key = shared_secret[:32]
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)


if __name__ == "__main__":
    # Tactical Telemetry Communication Simulation
    communicator = PQCDefenseCommunicator()
    
    print("[DRDO PQC-NODE] Generating Dilithium-5 & Kyber-1024 Keypairs...")
    signer_pub, signer_priv = communicator.generate_dsa_keypair()
    
    with oqs.KeyEncapsulation("Kyber1024") as kem_server:
        receiver_kem_pub = kem_server.generate_keypair()
        receiver_kem_priv = kem_server.export_secret_key()

    # Tactical Payload
    tactical_data = b"CONFIDENTIAL: DRDO Q-NAV Node 07 Coordinates: 17.3850 N, 78.4867 E. Anomaly Confirmed."
    
    # 1. Sign Message
    signature = communicator.sign_tactical_message(tactical_data, signer_priv)
    print(f"[SIGN] ML-DSA-87 Signature Generated ({len(signature)} bytes)")

    # 2. Key Encapsulation (PQC Key Exchange)
    kem_ciphertext, sender_shared_secret = communicator.encapsulate_key(receiver_kem_pub)
    print(f"[ENCAP] ML-KEM-1024 Ciphertext Generated ({len(kem_ciphertext)} bytes)")

    # 3. Encrypt Payload using Derived AES-GCM Key
    enc_payload, nonce, tag = communicator.encrypt_aes_gcm(tactical_data, sender_shared_secret)

    # 4. Decapsulate at Receiver Node
    receiver_shared_secret = communicator.decapsulate_key(kem_ciphertext, receiver_kem_priv)
    assert sender_shared_secret == receiver_shared_secret, "Shared secrets do not match!"

    # 5. Decrypt Payload
    decrypted_data = communicator.decrypt_aes_gcm(enc_payload, nonce, tag, receiver_shared_secret)
    is_valid = communicator.verify_tactical_message(decrypted_data, signature, signer_pub)

    print(f"[RECV] Decrypted Payload: {decrypted_data.decode('utf-8')}")
    print(f"[VERIFY] Signature Valid: {is_valid}")
