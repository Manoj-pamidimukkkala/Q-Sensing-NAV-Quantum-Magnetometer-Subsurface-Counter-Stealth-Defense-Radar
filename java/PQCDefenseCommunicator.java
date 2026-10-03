package com.drdo.quantum.crypto;

import org.bouncycastle.pqc.jcajce.provider.BouncyCastlePQCProvider;
import org.bouncycastle.pqc.jcajce.spec.MLKEMParameterSpec;
import org.bouncycastle.pqc.jcajce.spec.MLDSAParameterSpec;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.*;
import java.security.spec.AlgorithmParameterSpec;
import java.util.Base64;

public class PQCDefenseCommunicator {

    static {
        // Register Bouncy Castle Post-Quantum Security Provider
        Security.addProvider(new BouncyCastlePQCProvider());
    }

    private static final int GCM_TAG_LENGTH = 128;
    private static final int GCM_NONCE_LENGTH = 12;

    public static KeyPair generateMLDSAKeyPair() throws Exception {
        KeyPairGenerator kpg = KeyPairGenerator.getInstance("ML-DSA", "BCPQC");
        kpg.initialize(MLDSAParameterSpec.ml_dsa_87, new SecureRandom());
        return kpg.generateKeyPair();
    }

    public static KeyPair generateMLKEMKeyPair() throws Exception {
        KeyPairGenerator kpg = KeyPairGenerator.getInstance("ML-KEM", "BCPQC");
        kpg.initialize(MLKEMParameterSpec.ml_kem_1024, new SecureRandom());
        return kpg.generateKeyPair();
    }

    public static byte[] signMessage(byte[] message, PrivateKey privateKey) throws Exception {
        Signature signer = Signature.getInstance("ML-DSA", "BCPQC");
        signer.initSign(privateKey);
        signer.update(message);
        return signer.sign();
    }

    public static boolean verifySignature(byte[] message, byte[] signature, PublicKey publicKey) throws Exception {
        Signature verifier = Signature.getInstance("ML-DSA", "BCPQC");
        verifier.initVerify(publicKey);
        verifier.update(message);
        return verifier.verify(signature);
    }

    public static byte[] encryptAESGCM(byte[] plaintext, byte[] sharedSecret, byte[] nonce) throws Exception {
        byte[] aesKeyBytes = new byte[32]; // 256-bit AES key
        System.arraycopy(sharedSecret, 0, aesKeyBytes, 0, 32);

        SecretKeySpec keySpec = new SecretKeySpec(aesKeyBytes, "AES");
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        GCMParameterSpec gcmSpec = new GCMParameterSpec(GCM_TAG_LENGTH, nonce);

        cipher.init(Cipher.ENCRYPT_MODE, keySpec, gcmSpec);
        return cipher.doFinal(plaintext);
    }

    public static byte[] decryptAESGCM(byte[] ciphertext, byte[] sharedSecret, byte[] nonce) throws Exception {
        byte[] aesKeyBytes = new byte[32];
        System.arraycopy(sharedSecret, 0, aesKeyBytes, 0, 32);

        SecretKeySpec keySpec = new SecretKeySpec(aesKeyBytes, "AES");
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        GCMParameterSpec gcmSpec = new GCMParameterSpec(GCM_TAG_LENGTH, nonce);

        cipher.init(Cipher.DECRYPT_MODE, keySpec, gcmSpec);
        return cipher.doFinal(ciphertext);
    }

    public static void main(String[] args) {
        try {
            System.out.println("[DRDO JAVA-PQC] Initializing ML-DSA-87 & ML-KEM-1024 Providers...");

            // 1. Generate Keypairs
            KeyPair dsaKeyPair = generateMLDSAKeyPair();
            KeyPair kemKeyPair = generateMLKEMKeyPair();

            byte[] tacticalMessage = "CONFIDENTIAL: Command Directive 09 - Engage Quantum Stealth Tracking.".getBytes();

            // 2. Sign Tactical Message
            byte[] signature = signMessage(tacticalMessage, dsaKeyPair.getPrivate());
            System.out.println("[SIGN] Digital Signature Length: " + signature.length + " bytes");

            // 3. Simulated Symmetric Key Derivation (GCM Nonce)
            byte[] nonce = new byte[GCM_NONCE_LENGTH];
            new SecureRandom().nextBytes(nonce);

            // Dummy 32-byte shared key representing PQC KEM exchanged secret
            byte[] simulatedSharedSecret = new byte[32];
            new SecureRandom().nextBytes(simulatedSharedSecret);

            // 4. Encrypt Message
            byte[] encryptedData = encryptAESGCM(tacticalMessage, simulatedSharedSecret, nonce);
            System.out.println("[ENC] Encrypted Payload (Base64): " + Base64.getEncoder().encodeToString(encryptedData));

            // 5. Decrypt and Verify
            byte[] decryptedData = decryptAESGCM(encryptedData, simulatedSharedSecret, nonce);
            boolean isValid = verifySignature(decryptedData, signature, dsaKeyPair.getPublic());

            System.out.println("[DEC] Decrypted: " + new String(decryptedData));
            System.out.println("[VERIFY] Signature Valid: " + isValid);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
