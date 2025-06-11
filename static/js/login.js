import { SecureSession } from "./secure-transmit.js";

const form = document.getElementById("login-form");
const encryptField = document.getElementById("encrypted-data");

const session = new SecureSession();

async function init() {
    await session.generateKeyPair();

    const res = await fetch("/handshake/init-handshake");
    const { server_public_key }  = await res.json();

    const serverPubBytes = Uint8Array.from(atob(server_public_key), c => c.charCodeAt(0));

    await session.deriveSharedKey(serverPubBytes);

    const clientPubKey = await session.exportPublicKey();

    await fetch("/handshake/exchange", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ client_public_key: clientPubKey })
    });

    form.addEventListener("submit", async (e) =>{
        e.preventDefault();

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        const encrypt = await session.encrypt({
            username: username,
            password: password
        });

        encryptField.value = JSON.stringify(encrypt);


        document.getElementById("username").value = "";
        document.getElementById("password").value = "";

        form.submit();
    });
}

document.addEventListener("DOMContentLoaded", () => {
  init();
});