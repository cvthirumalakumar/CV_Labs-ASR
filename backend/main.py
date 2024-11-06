# backend/main.py

from fastapi import FastAPI, UploadFile, File
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch
import torchaudio
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

# Load Wav2Vec2 model and processor
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

@app.post("/api/upload-audio")
async def upload_audio(audio: UploadFile = File(...)):
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"uploaded_audio/{timestamp}.opus"
        
        # Save the uploaded audio file to a specific location
        with open(f"{filename}", "wb") as file_object:
            file_object.write(await audio.read())

        # Run ffmpeg command to convert opus to wav format
        ffmpeg_command = f"ffmpeg -i {filename} {filename[:-5]}.wav"
        os.system(ffmpeg_command)
        

        waveform, sample_rate = torchaudio.load(f"{filename[:-5]}.wav")
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
            waveform = resampler(waveform)
        print(waveform)
        input_values = processor(waveform.squeeze().numpy(), sampling_rate=16000, return_tensors="pt").input_values

        # delete audios 
        # os.remove(f"{filename[:-5]}.wav")
        # os.remove(f"{filename}")
        
        
        
        # Perform inference
        with torch.no_grad():
            logits = model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.decode(predicted_ids[0])

        return {"transcription": transcription}

    except Exception as e:
        print(e)
        return {"error": str(e)}
