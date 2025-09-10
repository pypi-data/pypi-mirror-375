# Music Drummer
Glorified Metronome

The methods of this package depend upon `music21`.

For this package (and `music21` too), a `duration` of `1` is a
quarter-note. So, `1/2` would be an eighth-note, etc.

## SYNOPSIS
```python
from music_drummer import Drummer

# Ex 1 - basic 4/4 metronome groove:
d = Drummer()
d.set_bpm(60) # set the beats per minute
d.set_ts() # set the default time signature of 4/4
# add a 16-beat phrase for 64 measures
for _ in range(64):
    d.pattern(
        patterns={
            'kick':  '1000000010000000',
            'snare': '0000100000001000',
            'hihat': '1010101010101010',
        },
    )
d.sync_parts() # make the parts play simultaneously
d.score.show('midi') # or nothing, text, etc. see music21 docs

# Ex 2 - 5/8 groove with intro:
d = Drummer()

d.set_instrument('kick', 'kick2') # change to the electric kick
d.set_instrument('snare', 'snare2') # change to the electric snare
d.set_instrument('crash', 'crash1') # add a crash
# print(d.instrument_map()) # full list of known instruments

d.set_bpm(99) # change the beats per minute from 120
d.set_ts('5/8') # change the time signature from 4/4

d.count_in(2) # count-in on the hi-hats for 2 measures
d.rest('kick', duration=10)
d.rest('snare', duration=10)
d.rest('crash', duration=10)

# 3 hi-hat states: closed, open, pedal
d.note('closed', duration=1/2)
d.note('open', duration=1/2)
d.note('pedal', duration=1/2)
d.note('closed', duration=1/2)
d.rest(['snare', 'kick', 'crash'], duration=2)

# add a eighth-note snare flam to the score
d.note('snare', duration=1/2, flam=1/16)
d.rest(['kick', 'hihat', 'crash'], duration=1/2)

# add a 5-note snare roll for an eighth-note, increasing in volume
d.roll('snare', duration=1/2, subdivisions=5, crescendo=[100, 127])
d.rest(['kick', 'hihat', 'crash'], duration=1/2)

# crash and kick!
d.note('kick', duration=1/2)
d.note('crash', duration=1/2)
d.rest(['snare', 'hihat'], duration=1/2)

# add a 4-part, 4-bar, eighth-note phrase to the score
for _ in range(8):
    d.pattern(
        patterns={
            'kick':  '1000000010',
            'snare': '0000001000',
            'hihat': '0111111111',
            'crash': '1000000000',
        },
        duration=1/2
    )

d.sync_parts() # make the parts play simultaneously

d.score.show() # or text, midi, etc. see music21 docs
```