"""
Audio utility functions for transcoding and processing.
"""
import io
import av
from fastapi import UploadFile
import soundfile as sf
import librosa


async def convert(file: UploadFile, _filename: str) -> bytes:
    """
    Converts a file to FLAC format using librosa/soundfile.
    """
    # Read the content of the uploaded file
    file_content = await file.read()

    # Use librosa to load the audio data from the file content
    audio, sample_rate = librosa.load(io.BytesIO(file_content), sr=None)

    # Create an in-memory buffer to store the FLAC file
    flac_buffer = io.BytesIO()

    # Write the audio data to the buffer in FLAC format
    sf.write(flac_buffer, audio, sample_rate, format='FLAC')

    # Get the bytes from the buffer
    flac_data = flac_buffer.getvalue()

    return flac_data

def convert_to_opus(input_data: bytes) -> bytes:
    """
    Converts audio bytes (mp4a, webm, etc.) to OGG/Opus (16kHz, Mono, 24kbps).
    Uses PyAV for robust transcoding.
    """
    input_container = av.open(io.BytesIO(input_data))
    input_stream = input_container.streams.audio[0]

    output_buffer = io.BytesIO()
    output_container = av.open(output_buffer, mode='w', format='ogg')
    output_stream = output_container.add_stream('libopus', rate=16000)
    output_stream.options = {'b': '24000'} # 24kbps
    output_stream.layout = 'mono'

    # Resampler
    resampler = av.AudioResampler(
        format=av.AudioFormat('fltp'),
        layout='mono',
        rate=16000,
    )

    for frame in input_container.decode(input_stream):
        # We need to resample frames to match the output rate/layout
        resampled_frames = resampler.resample(frame) 
        for resampled_frame in resampled_frames:
            for packet in output_stream.encode(resampled_frame):
                output_container.mux(packet)

    # Flush
    for packet in output_stream.encode(None):
        output_container.mux(packet)

    output_container.close()
    return output_buffer.getvalue()