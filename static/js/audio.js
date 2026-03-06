// audio.js — Browser-side audio recording & speech-to-text (Web Speech API)

let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let recognition = null;
let transcriptText = "";

// ── Speech Recognition (Web Speech API) ──────────────────

function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        console.warn("[Audio] Speech Recognition not supported in this browser.");
        return null;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-IN";

    recognition.onresult = (event) => {
        let interim = "";
        let final = "";

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                final += transcript + " ";
            } else {
                interim += transcript;
            }
        }

        if (final) transcriptText += final;

        const liveEl = document.getElementById("liveTranscript");
        if (liveEl) {
            liveEl.textContent = (transcriptText + interim).trim();
        }
    };

    recognition.onerror = (event) => {
        console.error("[Audio] Speech recognition error:", event.error);
        if (event.error === "no-speech") {
            // Restart recognition silently
            if (isRecording && recognition) {
                try { recognition.start(); } catch (e) { }
            }
        }
    };

    recognition.onend = () => {
        // Auto-restart if still recording
        if (isRecording) {
            try { recognition.start(); } catch (e) { }
        }
    };

    return recognition;
}

// ── Recording control ─────────────────────────────────────

async function startRecording() {
    if (isRecording) return;

    try {
        let stream;
        // Try to reuse existing localStream from webrtc.js if available
        if (typeof localStream !== "undefined" && localStream && localStream.getAudioTracks().length > 0) {
            // Create a new stream with only the audio tracks to avoid MediaRecorder conflicts
            stream = new MediaStream(localStream.getAudioTracks());
            stream.isReused = true;
        } else {
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        }

        audioChunks = [];
        transcriptText = "";

        mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

        mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) audioChunks.push(event.data);
        };

        mediaRecorder.start(250); // collect chunks every 250ms
        isRecording = true;

        // Start speech recognition
        if (!recognition) initSpeechRecognition();
        if (recognition) {
            try { recognition.start(); } catch (e) { }
        }

        // Update UI
        const recBtn = document.getElementById("recordBtn");
        const stopBtn = document.getElementById("stopBtn");
        if (recBtn) { recBtn.disabled = true; recBtn.classList.add("recording"); }
        if (stopBtn) { stopBtn.disabled = false; }

        const liveEl = document.getElementById("liveTranscript");
        if (liveEl) { liveEl.textContent = ""; liveEl.style.display = "block"; }

        console.log("[Audio] Recording started");
    } catch (err) {
        console.error("[Audio] Start recording failed:", err);

        const html = `
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; width: 100%;">
                <span><strong>Microphone access denied.</strong> Click the lock/camera icon in your address bar to allow.</span>
                <button class="btn btn-ghost btn-sm" onclick="retryPermission()" style="border-color: currentColor; color: inherit; background: rgba(255,255,255,0.1);">Retry</button>
            </div>
        `;
        showStatusHTML(html, "error");
    }
}

async function stopRecording() {
    if (!isRecording) return;

    isRecording = false;

    if (recognition) {
        try { recognition.stop(); } catch (e) { }
    }

    return new Promise((resolve) => {
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
            const answer = transcriptText.trim() || "[No speech detected]";

            console.log("[Audio] Recorded answer:", answer);

            // Update UI
            const recBtn = document.getElementById("recordBtn");
            const stopBtn = document.getElementById("stopBtn");
            if (recBtn) { recBtn.disabled = false; recBtn.classList.remove("recording"); }
            if (stopBtn) { stopBtn.disabled = true; }

            // Send answer to AI interviewer
            await sendAnswer(answer);
            resolve(answer);
        };

        if (mediaRecorder && mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
            // Stop all tracks only if stream was not reused from global localStream
            if (!mediaRecorder.stream.isReused) {
                mediaRecorder.stream.getTracks().forEach(t => t.stop());
            }
        }
    });
}