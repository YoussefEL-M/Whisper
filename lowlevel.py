import whisper

model = whisper.load_model('base')

# Trim lyd så det kun er 30sek
audio = whisper.load_audio('/home/Youssef/Desktop/Lydfil-01.mp3')
audio = whisper.pad_or_trim(audio)

# Laver log-mel spektogram og flytter det til samme enhed
mel = whisper.log_mel_spectrogram(audio).to(model.device)

# Bekræft sprog
_, probs = model.detect_language(mel)
print(f'Detected language: {max(probs, key=probs.get)}')

# Decode lydfilen
options = whisper.DecodingOptions()
result = whisper.decode(model, mel, options)

print(result.text)