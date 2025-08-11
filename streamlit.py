import whisper
import streamlit as st
import tempfile
import os

@st.cache_resource
def load_model():
    return whisper.load_model('base')

model = load_model()

st.title('Whisper AI audio Transcription')

uploaded_file = st.file_uploader('Upload an audio file', type=['mp3', 'wav', 'm4a'])

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/mp3")
    if st.button('Transcribe'):
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        with st.spinner('Transcribing...'):
            result = model.transcribe(tmp_path)

        st.subheader('Transcription')
        st.write(result['text'])

        os.remove(tmp_path)

