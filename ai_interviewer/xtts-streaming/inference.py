import torch
from TTS.api import TTS

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=True).to(device)
tts.tts_to_file("Explain your experience in SQL, building dashboards, data collection and transformation, statistical modeling, and visualization. Provide specific examples of projects or tasks where you applied these skills.", file_path="output.wav")
