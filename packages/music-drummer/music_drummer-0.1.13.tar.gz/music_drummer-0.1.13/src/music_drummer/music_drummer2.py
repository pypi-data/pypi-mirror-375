from typing import List, Dict, Callable, Optional, Any
from music21 import stream, note, tempo, meter, midi, instrument
from music21 import duration as m21duration

class MIDIDrummerTiny:
    STRAIGHT = 50  # Swing percent

    def __init__(self,
                 file: str = 'MIDI-Drummer.mid',
                 bpm: int = 120,
                 volume: int = 100,
                 signature: str = '4/4',
                 beats: int = 4,
                 bars: int = 4,
                 reverb: int = 15,
                 soundfont: Optional[str] = None,
                 kick: int = 35,
                 snare: int = 38,
                 setup: bool = True,
                 verbose: bool = False):
        self.file = file
        self.bpm = bpm
        self.volume = volume
        self.signature = signature
        self.beats = beats
        self.bars = bars
        self.reverb = reverb
        self.soundfont = soundfont
        self.kick = kick
        self.snare = snare
        self.setup = setup
        self.verbose = verbose

        self.counter = 0
        self.score = stream.Score()
        self.part = stream.Part()
        self.score.append(self.part)
        self._init_score()

    def _init_score(self):
        ts = meter.TimeSignature(self.signature)
        self.part.append(ts)
        mm = tempo.MetronomeMark(number=self.bpm)
        self.part.append(mm)
        # Volume/reverb not directly supported in music21, but can be set in MIDI later

    def set_bpm(self, bpm: int):
        self.bpm = bpm
        mm = tempo.MetronomeMark(number=bpm)
        self.part.append(mm)

    def set_time_sig(self, signature: str):
        self.signature = signature
        ts = meter.TimeSignature(signature)
        self.part.append(ts)

    def note(self, duration: str, *patches: int):
        dur = self._duration_from_string(duration)
        for patch in patches:
            n = note.Note()
            n.duration = dur
            n.volume.velocity = self.volume
            n.pitch.midi = patch
            n.storedInstrument = instrument.Percussion()
            self.part.append(n)
            self.counter += dur.quarterLength

    def accent_note(self, accent: int, duration: str, patch: int):
        dur = self._duration_from_string(duration)
        n = note.Note()
        n.duration = dur
        n.volume.velocity = accent
        n.pitch.midi = patch
        n.storedInstrument = instrument.Percussion()
        self.part.append(n)
        self.counter += dur.quarterLength

    def rest(self, duration: str):
        dur = self._duration_from_string(duration)
        r = note.Rest()
        r.duration = dur
        self.part.append(r)
        self.counter += dur.quarterLength

    def count_in(self, bars: Optional[int] = None, patch: Optional[int] = None, accent: Optional[int] = None):
        bars = bars if bars is not None else self.bars
        patch = patch if patch is not None else self.kick
        accent = accent if accent is not None else self.snare
        beats = meter.TimeSignature(self.signature).numerator
        for i in range(beats * bars):
            if i % beats == 0:
                self.accent_note(127, 'quarter', accent)
            else:
                self.note('quarter', patch)

    def metronome4(self, bars: Optional[int] = None, cymbal: Optional[int] = None, tempo_str: str = 'quarter', swing: int = STRAIGHT):
        bars = bars if bars is not None else self.bars
        cymbal = cymbal if cymbal is not None else self.kick
        for _ in range(bars):
            self.note(tempo_str, cymbal, self.kick)
            self.note(tempo_str, cymbal)
            self.note(tempo_str, cymbal, self.snare)
            self.note(tempo_str, cymbal)

    def write(self):
        mf = midi.translate.streamToMidiFile(self.score)
        mf.open(self.file, 'wb')
        mf.write()
        mf.close()

    def _duration_from_string(self, duration: str):
        # Map string like 'quarter', 'eighth', etc. to music21 duration
        mapping = {
            'whole': 4.0,
            'half': 2.0,
            'quarter': 1.0,
            'eighth': 0.5,
            'sixteenth': 0.25,
            'thirtysecond': 0.125,
            'sixtyfourth': 0.0625,
        }
        if duration in mapping:
            return m21duration.Duration(mapping[duration])
        elif duration.endswith('n'):
            # e.g. 'qn', 'en'
            code = duration[:-1]
            code_map = {
                'w': 4.0, 'h': 2.0, 'q': 1.0, 'e': 0.5, 's': 0.25, 'x': 0.125, 'y': 0.0625, 'z': 0.03125
            }
            return m21duration.Duration(code_map.get(code, 1.0))
        else:
            # fallback: try to parse as float
            try:
                return m21duration.Duration(float(duration))
            except Exception:
                return m21duration.Duration(1.0)
