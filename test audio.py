__author__ = 'cook'

from pydub import AudioSegment
from pydub.playback import play

sound1 = AudioSegment.from_wav("loops/bassdrum.1.wav")
sound2 = AudioSegment.from_wav("loops/bongo.high.wav")
sound3 = AudioSegment.from_wav("loops/cowbell.wav")

# mix sound2 with sound1, starting at 5000ms into sound1)
sound10 = sound1.overlay(sound2)
sound11 = sound10.overlay(sound3)
#play(sound1)
#play(sound2)
#play(sound10)
for i in range(10):
    play(sound3)
    play(sound11)

# save the result
# sound10.export("mixed_sounds.mp3", format="wav")
