from rtlsdr import RtlSdr
import numpy as np
import matplotlib.pyplot as plt
import subprocess 
import asyncio
from scipy.signal import correlate
import aiofiles



def initSDR():
    global sdr
    sdr = RtlSdr()
    sdr.sample_rate = 2.048e6 # Hz
    sdr.center_freq = 100e6   # Hz
    sdr.freq_correction = 60  # PPM
    print(sdr.valid_gains_db)
    sdr.gain = 49.6
    print(sdr.gain)


def processNoise(noise):
    i_mean = np.average(noise.real)
    q_mean = np.average(noise.imag)

    #generate iq bits comparing each compnent to the average
    i_bits = np.real(noise) > i_mean
    q_bits = np.imag(noise) > q_mean
    

     # Interleave I and Q bits
    bits = np.empty((i_bits.size + q_bits.size,), dtype=np.int32)
    bits[0::2] = i_bits
    bits[1::2] = q_bits
    

async def transmitFM(soundFile):
    print('transmitting fm. . . ')
    cmd = ["./fm_transmitter", "-f", "100", "-r", soundFile]
    subprocess.run(cmd)

async def readFM(transmitFMData):

    async for samples in sdr.stream():
        # do something with samples
        # ...
        # Calculate cross-correlation for I (In-phase) component
        correlation_i = correlate(samples.real, transmitFMData.real, mode='full')

        # Calculate cross-correlation for Q (Quadrature) component
        correlation_q = correlate(samples.imag, transmitFMData.imag, mode='full')

        # Sum the correlations to find the overall delay
        correlation = correlation_i + correlation_q

        
        delay = correlation.argmax() - (len(transmitFMData) - 1)

          # Align the transmitted data based on the delay
        if delay > 0:
            transmit_aligned = transmitFMData[delay:delay + len(samples)]
        else:
            transmit_aligned = transmitFMData[:len(samples)]


        # Remove the extra transmitted data from the end of the array
        min_length = min(len(samples_aligned), len(transmit_aligned))
        samples_aligned = samples_aligned[:min_length]
        transmit_aligned = transmit_aligned[:min_length]

        # Cancel out the transmitted signal from the sample to extract only the noise
        noise = samples_aligned + transmit_aligned * -1

        bits = processNoise(noise)

         # Save the bits to a file with pipes
        async with aiofiles.open('noise_bits.txt', 'w') as f:
            for bit in bits:
                await f.write(f'{bit}|')

    # to stop streaming:
    await sdr.stop()

    # done
    sdr.close()


async def main():

    originalSoundFile = np.open('sinWave.npy')
    await initSDR()
    print('sdr has been init')
    await asyncio.gather(readFM(originalSoundFile), transmitFM())



if __name__ == "__main__":
    asyncio.run(main())