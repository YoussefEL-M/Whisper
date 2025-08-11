import whisper

model = whisper.load_model('base')
result = model.transcribe('/home/Youssef/Desktop/Lydfil-01.mp3')
print(result['text'])