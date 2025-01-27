import gradio as gr
import torch
import soundfile as sf
from models import build_model
from kokoro import generate

# Constants
SAMPLE_RATE = 24000
MODEL_FILE = "models/kokoro-v0_19.pth"
DEFAULT_VOICE = "af_sky"
VOICES_DIR = "voices/"
OUTPUT_FILE = "output_hmb.wav"

def synthesize_voice(text, voice_name):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Running on device: {device}")

    # Load model
    model = build_model(MODEL_FILE, device)

    # Load voice pack
    try:
        voicepack = torch.load(f"{VOICES_DIR}/{voice_name}.pt", weights_only=True).to(device)
    except FileNotFoundError:
        return "Error: Voice pack not found!", None

    print(f"Loaded voice: {voice_name}")

    # Generate audio
    audio = []
    for chunk in text.split("."):
        if len(chunk.strip()) < 2:
            continue
        try:
            snippet, _ = generate(model, chunk.strip(), voicepack, lang=voice_name[0])
            audio.extend(snippet)
        except Exception as e:
            return f"Error generating audio: {e}", None

    # Save audio to file
    sf.write(OUTPUT_FILE, audio, SAMPLE_RATE)
    return "Audio generated successfully!", OUTPUT_FILE

# Define Gradio interface
def interface(text, voice):
    message, output_path = synthesize_voice(text, voice)
    if output_path:
        return message, output_path
    else:
        return message, None

# Available voices (list can be extended)
available_voices = ["af_sky", "af_ocean", "af_mountain"]  # Example voices

# Gradio app
demo = gr.Interface(
    fn=interface,
    inputs=[
        gr.Textbox(label="Input Text", placeholder="Enter text to synthesize..."),
        gr.Dropdown(choices=available_voices, value=DEFAULT_VOICE, label="Select Voice")
    ],
    outputs=[
        gr.Textbox(label="Status"),
        gr.Audio(label="Generated Audio")
    ],
    title="Voice Synthesis with Kokoro B-AI",
    description="Enter text and select a voice to generate synthesized speech."
)

if __name__ == "__main__":
    demo.launch()
