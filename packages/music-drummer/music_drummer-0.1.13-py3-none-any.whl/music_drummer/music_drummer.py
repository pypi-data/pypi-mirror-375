from music21 import stream, note, tempo, meter, instrument
from music21 import duration as m21duration
from requests import patch

class Drummer:
    STRAIGHT = 50

    def __init__(self, file='Drummer.mid', bpm=120, volume=100, accent=20, signature='4/4', bars=4):
        self.file = file
        self.volume = volume
        self.bars = bars
        self.counter = 0
        self.accent = accent
        self.signature = signature
        self.bpm = bpm
        self.kit = {
            'kick': { 'instrument': 'kick1', 'part': stream.Part() },
            'snare': { 'instrument': 'snare1', 'part': stream.Part() },
            'hihat': { 'instrument': 'hihat1', 'part': stream.Part() },
        }
        self.score = stream.Score()

    def sync_parts(self):
        for part in self.kit.values():
            part['part'].append(instrument.Woodblock())
            self.score.insert(0, part['part'])

    def set_ts(self, ts=None):
        if not ts:
            ts = self.signature
        else:
            self.signature = ts
        ts = meter.TimeSignature(ts)
        self.beats = ts.numerator
        self.divisions = ts.denominator
        for part in self.kit.values():
            part['part'].timeSignature = ts

    def set_bpm(self, bpm=None):
        if not bpm:
            bpm = self.bpm
        else:
            self.bpm = bpm
        self.score.append(tempo.MetronomeMark(number=bpm))

    def set_instrument(self, name, patch):
        if patch in self.kit:
            self.kit[name]['instrument'] = patch
        else:
            self.kit[name] = { 'instrument': patch, 'part': stream.Part() }

    def rest(self, name, duration=1.0):
        n = note.Rest()
        n.duration = m21duration.Duration(duration)
        patch = self.instrument_map(self.kit[name]['instrument'])
        self.kit[name]['part'].append(n)
        if duration:
            self.counter += duration

    def note(self, name, duration=1.0, volume=None, flam=0):
        patch = self.instrument_map(self.kit[name]['instrument'])
        if volume is None:
            volume = self.volume
        if flam > 0:
            grace = note.Note(patch['num'])
            grace.duration = m21duration.Duration(flam)
            self.kit[name]['part'].append(grace)
        n = note.Note(patch['num'])
        n.volume.velocity = volume
        n.duration = m21duration.Duration(duration - flam)
        if name:
            self.kit[name]['part'].append(n)
        else:
            self.score.append(n)
        if duration:
            self.counter += duration

    def accent_note(self, name, duration=1.0, volume=None, accent=None):
        if volume is None:
            volume = self.volume
        if accent is None:
            accent = self.accent
        self.note(name, duration=duration, volume=volume + accent)

    def duck_note(self, name, duration=1.0, volume=None, accent=None):
        if volume is None:
            volume = self.volume
        if accent is None:
            accent = self.accent
        self.note(name, duration=duration, volume=volume - accent)

    def count_in(self, patch='hihat', bars=1):
        for _ in range(bars):
            self.accent_note(patch)
            for i in range(self.beats - 1):
                self.note(patch)

    def pattern(self, patterns=None, duration=1/4, vary=None):
        if not patterns:
            return

        if vary is None:
            vary = {
                '0': lambda self, **args: self.rest(args['patch'], duration=args['duration']),
                '1': lambda self, **args: self.note(args['patch'], duration=args['duration']),
            }

        for inst in self.kit.keys():
            if inst in patterns:
                for pattern_str in patterns[inst]:
                    for bit in pattern_str:
                        vary[bit](self, patch=inst, duration=duration)

    def roll(self, name, duration=1, subdivisions=4, crescendo=[]):
        if not crescendo:
            factor = 0
            volume = self.volume
        else:
            factor = round((crescendo[1] - crescendo[0]) / (subdivisions - 1))
            volume = crescendo[0]
        for _ in range(subdivisions):
            self.note(name, duration=duration/subdivisions, volume=int(volume))
            volume += factor

    def instrument_map(self, key=None):
        kit = {
            'kick1': { 'num': 35, 'type': 'drums', 'name': 'Acoustic Bass Drum', 'obj': instrument.BassDrum() },
            'kick2': { 'num': 36, 'type': 'drums', 'name': 'Bass Drum 1', 'obj': instrument.BassDrum() },
            'snare1': { 'num': 38, 'type': 'drums', 'name': 'Acoustic Snare', 'obj': instrument.SnareDrum() },
            'snare2': { 'num': 40, 'type': 'drums', 'name': 'Electric Snare', 'obj': instrument.SnareDrum() },
            'sidestick': { 'num': 37, 'type': 'drums', 'name': 'Side Stick', 'obj': instrument.SnareDrum() },
            'clap': { 'num': 39, 'type': 'percussion', 'name': 'Hand Clap', 'obj': instrument.Percussion() },
            'hihat1': { 'num': 42, 'type': 'cymbals', 'name': 'Closed High Hat', 'obj': instrument.HiHatCymbal() },
            'hihat2': { 'num': 46, 'type': 'cymbals', 'name': 'Open High Hat', 'obj': instrument.HiHatCymbal() },
            'hihat3': { 'num': 44, 'type': 'cymbals', 'name': 'Pedal High Hat', 'obj': instrument.HiHatCymbal() },
            'crash1': { 'num': 49, 'type': 'cymbals', 'name': 'Crash Cymbal 1', 'obj': instrument.CrashCymbals() },
            'crash2': { 'num': 57, 'type': 'cymbals', 'name': 'Crash Cymbal 2', 'obj': instrument.CrashCymbals() },
            'china': { 'num': 52, 'type': 'cymbals', 'name': 'Chinese Cymbal', 'obj': instrument.CrashCymbals() },
            'splash': { 'num': 55, 'type': 'cymbals', 'name': 'Splash Cymbal', 'obj': instrument.CrashCymbals() },
            'ride1': { 'num': 51, 'type': 'cymbals', 'name': 'Ride Cymbal 1', 'obj': instrument.RideCymbals() },
            'ride2': { 'num': 59, 'type': 'cymbals', 'name': 'Ride Cymbal 2', 'obj': instrument.RideCymbals() },
            'ridebell': { 'num': 53, 'type': 'cymbals', 'name': 'Ride Bell', 'obj': instrument.RideCymbals() },
            'tom1': { 'num': 50, 'type': 'drums', 'name': 'High Tom', 'obj': instrument.TomTom },
            'tom2': { 'num': 48, 'type': 'drums', 'name': 'High Mid Tom', 'obj': instrument.TomTom },
            'tom3': { 'num': 47, 'type': 'drums', 'name': 'Low Mid Tom', 'obj': instrument.TomTom },
            'tom4': { 'num': 45, 'type': 'drums', 'name': 'Low Tom', 'obj': instrument.TomTom },
            'tom5': { 'num': 43, 'type': 'drums', 'name': 'High Floor Tom', 'obj': instrument.TomTom },
            'tom6': { 'num': 41, 'type': 'drums', 'name': 'Low Floor Tom', 'obj': instrument.TomTom },
            'cowbell': { 'num': 56, 'type': 'percussion', 'name': 'Cowbell', 'obj': instrument.Cowbell() },
            'bongo1': { 'num': 60, 'type': 'percussion', 'name': 'High Bongo', 'obj': instrument.BongoDrums() },
            'bongo2': { 'num': 61, 'type': 'percussion', 'name': 'Low Bongo', 'obj': instrument.BongoDrums() },
            'conga1': { 'num': 63, 'type': 'percussion', 'name': 'Open High Conga', 'obj': instrument.CongaDrum() },
            'conga2': { 'num': 62, 'type': 'percussion', 'name': 'Mute High Conga', 'obj': instrument.CongaDrum() },
            'conga3': { 'num': 64, 'type': 'percussion', 'name': 'Low Conga', 'obj': instrument.CongaDrum() },
            'timbale1': { 'num': 65, 'type': 'percussion', 'name': 'High Timbale', 'obj': instrument.Timbales() },
            'timbale2': { 'num': 66, 'type': 'percussion', 'name': 'Low Timbale', 'obj': instrument.Timbales() },
            'tambourine': { 'num': 54, 'type': 'percussion', 'name': 'Tambourine', 'obj': instrument.Tambourine() },
            'shaker': { 'num': 70, 'type': 'percussion', 'name': 'Maracas', 'obj': instrument.Maracas() },
            'cabasa': { 'num': 69, 'type': 'percussion', 'name': 'Cabasa', 'obj': instrument.Percussion() },
            'claves': { 'num': 75, 'type': 'percussion', 'name': 'Claves', 'obj': instrument.Percussion() },
            'woodblock1': { 'num': 76, 'type': 'percussion', 'name': 'High Wood Block', 'obj': instrument.Woodblock() },
            'woodblock2': { 'num': 77, 'type': 'percussion', 'name': 'Low Wood Block', 'obj': instrument.Woodblock() },
            'triangle1': { 'num': 81, 'type': 'percussion', 'name': 'Open Triangle', 'obj': instrument.Triangle() },
            'triangle2': { 'num': 82, 'type': 'percussion', 'name': 'Mute Triangle', 'obj': instrument.Triangle() },
        }
        if key:
            return kit.get(key)
        else:
            return kit