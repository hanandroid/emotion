import pyaudio
import numpy
import matplotlib.pyplot as plt
import math

chunk = 1024
FORMAT = pyaudio.paInt16

CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 3

def checkDB(data):
    result = numpy.frombuffer(data,dtype="int16")
    rms = (max(result))
    db = 20 * math.log10(rms)
    print("RMS=", rms, f" ：{format(db, '3.1f')}[dB]")

    if db > 60:
        flg = 1
    else:
        flg = 0
    return flg


p = pyaudio.PyAudio()

stream = p.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
                input = True,
                frames_per_buffer = chunk)

#レコード開始
print("Now Recording...")
frames = []
for i in range(0, int(RATE / chunk * RECORD_SECONDS)):
    data = stream.read(chunk)
    if checkDB(data) > 0:
        frames.append(data)
        print(".")

stream.close()
p.terminate()

data = b''.join(frames)

#録音したデータを配列に変換
result = numpy.frombuffer(data,dtype="int16")


plt.plot(result)
plt.show()
