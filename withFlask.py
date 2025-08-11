from flask import Flask, request, jsonify, render_template_string, send_file
import whisper
import tempfile
import os
import shutil

app = Flask(__name__)

model = whisper.load_model('base')

UPLOAD_FOLDER = tempfile.mkdtemp()

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title> Whisper Transpcription </title>
</head>
<body>
    <h1> Upload Audio for Transcription </h1>
    <form action="/transcribe" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept=".mp3,.wav,.m4a" required>
        <button type="submit">Transcribe</button>
    </form>

    <h2>Or record audio</h2>
    <button id="recordBtn">Start Recording</button>
    <button id="stopBtn" disabled>Stop Recording</button>
    <audio id="playback" controls style="display:none;"></audio>
    <p id="status"></p>

    <script>
        let mediaRecorder;
        let audioChunks = [];

        const recordBtn = document.getElementById("recordBtn");
        const stopBtn = document.getElementById("stopBtn");
        const playback = document.getElementById("playback");
        const status = document.getElementById("status");

        recordBtn.addEventListener("click", async () => {
            const stream = await navigator.mediaDevice.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.addEventListener("dataavailable", event => {
                audioChunks.push(event.data);
            });

            mediaRecorder.addEvenListener("stop", () => {
                const audioBlob = new Blob(audioChunks, { type: "audio/webm"});
                const audioUrl = URL.createObjectURL(audioBlob);
                playback.src = audioUrl;
                playback.style.display = "block";

                //Upload to server
                const formData = new FormData();
                formData.append("file", audioblob, "recording.webm");

                status.innerText = "Uploading and transcribing...";
                fetch("/transcribe", { method: "POST", body: formData })
                    .then(res => res.text())
                    .then(html => {
                        document.open();
                        document.write(html);
                        document.close();
                    });
            });

            mediaRecorder.start();
            recordBtn.disabled = true;
            stopBtn.disabled = false;
            status.innerText = "Recording...";
        });

        stopBtn.addEvenListener("click", () => {
            mediaRecorder.stop();
            recordBtn.disabled = false;
            stopBtn.disabled = true;
        });

    </script>

    {% if audio_filename %}
        <h2>Uploaded/Recorded audio: </h2>
        <audio controls>
            <source src="/play/{{ audio_filename }}" type="audio/mpeg">
            Your browser does not support the audio format.
        </audio>
        <p>{{ text }}</p>
    {% endif %}

    {% if text %}
        <h2>Transcription:</h2>
        <p>{{ text }}</p>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=['GET'])
def index():
    return render_template_string(HTML_PAGE)

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    #gem file til playback
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    #Kør
    result = model.transcribe(save_path)

    return render_template_string(
        HTML_PAGE, 
        text=result['text'],
        audio_filename=file.filename
    )

@app.route("/play/<filename>")
def play_audio(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)