import numpy as np
import scipy.io.wavfile as wavfile

def wav_to_iq(wav_filename, iq_filename):
    # Read the WAV file
    sample_rate, audio_data = wavfile.read(wav_filename)

    # Ensure the audio data is in the correct format
    if audio_data.ndim == 1:
            # Mono audio
            I = audio_data
            Q = np.zeros_like(audio_data)
    elif audio_data.ndim == 2:
            # Stereo audio
            if audio_data.shape[1] != 2:
                raise ValueError("Stereo audio should have exactly 2 channels")
            I, Q = audio_data[:, 0], audio_data[:, 1]
    else:
            raise ValueError("Audio data has an unexpected number of dimensions")


    # Normalize the audio data
    max_val = max(np.abs(I).max(), np.abs(Q).max())
    if max_val != 0:
        I = I / max_val
        Q = Q / max_val

    # Create complex IQ data
    iq_data = I + 1j * Q

    # Save the IQ data to a .iq file
    iq_data.tofile(iq_filename)
    print(f"Converted {wav_filename} to {iq_filename} successfully.")

# Example usage
wav_filename = '1000hz.wav'
iq_filename = 'sinWave.npy'
wav_to_iq(wav_filename, iq_filename)