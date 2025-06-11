export class SecureSession {
  constructor() {
    this.ecdhKeyPair = null;
    this.sharedAESKey = null;
  }

  // Tạo ECDH key pair
  async generateKeyPair() {
    this.ecdhKeyPair = await window.crypto.subtle.generateKey(
      {
        name: "ECDH",
        namedCurve: "P-256",
      },
      true,
      ["deriveKey"]
    );
  }

  async exportPublicKey() {
    if (!this.ecdhKeyPair) throw new Error("Key pair chưa được tạo");
    const rawKey = await window.crypto.subtle.exportKey("raw", this.ecdhKeyPair.publicKey);

    const bytes = new Uint8Array(rawKey);

    return btoa(String.fromCharCode(...bytes)); // gửi lên server
  }

  // Nhập public key từ server và tạo AES key
  async deriveSharedKey(serverPublicKey) {
    const importedKey = await window.crypto.subtle.importKey(
      "raw",
      serverPublicKey,
      { name: "ECDH", namedCurve: "P-256" },
      false,
      []
    );

    this.sharedAESKey = await window.crypto.subtle.deriveKey(
      {
        name: "ECDH",
        public: importedKey,
      },
      this.ecdhKeyPair.privateKey,
      { name: "AES-GCM", length: 256 },
      true,
      ["encrypt", "decrypt"]
    );

    const rawKey = await window.crypto.subtle.exportKey("raw", this.sharedAESKey);
  }

  // Mã hóa dữ liệu bất kỳ (Object hoặc String)
  async encrypt(data) {
    if (!this.sharedAESKey) throw new Error("AES key chưa được sinh");

    const iv = window.crypto.getRandomValues(new Uint8Array(12));
    const encoded = new TextEncoder().encode(
      typeof data === "string" ? data : JSON.stringify(data)
    );

    const ciphertextBuffer = await window.crypto.subtle.encrypt(
      {
        name: "AES-GCM",
        iv: iv,
      },
      this.sharedAESKey,
      encoded
    );

    return {
      data: {
        iv: Array.from(iv),
        ciphertext: Array.from(new Uint8Array(ciphertextBuffer)),
      },
    };
  }

  // Giải mã
  async decrypt({ iv, ciphertext }) {
    if (!this.sharedAESKey) throw new Error("AES key chưa được sinh");

    const ivUint8 = new Uint8Array(iv);
    const ciphertextUint8 = new Uint8Array(ciphertext);

    const decryptedBuffer = await window.crypto.subtle.decrypt(
      {
        name: "AES-GCM",
        iv: ivUint8,
      },
      this.sharedAESKey,
      ciphertextUint8
    );

    const decoded = new TextDecoder().decode(decryptedBuffer);

    try {
      return JSON.parse(decoded); // Nếu là JSON
    } catch {
      return decoded; // Nếu là string thường
    }
  }
}
