class ChaoticCipher {
    constructor(seed = 0.7, r = 3.99) {
        this.x = seed;
        this.r = r;
    }

    getStream(length) {
        const keyStream = new Uint8Array(length);
        for (let i = 0; i < length; i++) {
            this.x = this.r * this.x * (1 - this.x);
            keyStream[i] = Math.floor(this.x * 256) % 256;
        }
        return keyStream;
    }

    decrypt(data) {
        const stream = this.getStream(data.length);
        const decrypted = new Uint8Array(data.length);
        for (let i = 0; i < data.length; i++) {
            decrypted[i] = data[i] ^ stream[i];
        }
        return decrypted;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const videoElement = document.getElementById('video-id');
    if (!videoElement) return;

    // Initialize MediaSource
    const mediaSource = new MediaSource();
    videoElement.src = URL.createObjectURL(mediaSource);
    
    videoElement.addEventListener('error', () => {
        console.error('Video Error:', videoElement.error);
    });
    mediaSource.addEventListener('sourceopen', async () => {
        if (!MediaSource.isTypeSupported(mimeType)) {
            console.error("MIME type not supported:", mimeType);
            return;
        }
        const sourceBuffer = mediaSource.addSourceBuffer(mimeType);

        // Initialize ChaoticCipher with the seed from the server
        const cipher = new ChaoticCipher(chaoticSeed);

        // Fetch the encrypted stream
        const response = await fetch(`/stream/${videoId}`, {
            headers: {
                'Accept': mimeType
            },
            cache: 'no-store'
        });

        if (!response.ok) {
            console.error('Failed to fetch stream:', response.status);
            return;
        }

        const reader = response.body.getReader();

        // Read and process chunks
        async function processStream() {
            while (true) {
                const { done, value } = await reader.read();
                    if (done) {
                        if (!sourceBuffer.updating && mediaSource.readyState === 'open') {
                            mediaSource.endOfStream();
                        } else {
                            sourceBuffer.addEventListener('updateend', () => {
                                if (mediaSource.readyState === 'open') {
                                    mediaSource.endOfStream();
                                }
                            }, { once: true });
                        }
                        break;
                    }

                // Decrypt the chunk
                const decryptedChunk = cipher.decrypt(value);

                // Append decrypted chunk to SourceBuffer
                try {
                    if (sourceBuffer.updating) {
                        await new Promise(resolve => {
                            sourceBuffer.addEventListener('updateend', resolve, { once: true });
                        });
                    }
                    sourceBuffer.appendBuffer(decryptedChunk);
                } catch (e) {
                    console.error('Error appending buffer:', e);
                }
            }
        }

        processStream().catch(err => console.error('Stream processing error:', err));
    });
});