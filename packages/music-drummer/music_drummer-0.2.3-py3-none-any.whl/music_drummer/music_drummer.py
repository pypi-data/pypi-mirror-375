from music21 import stream, note, tempo, meter, instrument
from music21 import duration as m21duration

class Drummer:
    def __init__(self, bpm=120, volume=100, accent=20, signature='4/4'):
        self.volume = volume
        self.counter = 0
        self.accent = accent
        self.signature = signature
        self.bpm = bpm
        self.kit = {
            'kick': { 'instrument': 'kick1', 'part': stream.Part(), 'counter': 0 },
            'snare': { 'instrument': 'snare1', 'part': stream.Part(), 'counter': 0 },
            'hihat': { 'instrument': 'hihat1', 'part': stream.Part(), 'counter': 0 },
        }
        self.score = stream.Score()

    def sync_parts(self):
        for part in self.kit.values():
            patch = self.instrument_map(part['instrument'])
            self.score.insert(0, part['part'])
            part['part'].insert(0, patch['obj'])

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

    def set_bpm(self, bpm):
        self.bpm = bpm
        self.score.append(tempo.MetronomeMark(number=bpm))

    def set_instrument(self, name, patch):
        if patch in self.kit:
            self.kit[name]['instrument'] = patch
        else:
            self.kit[name] = { 'instrument': patch, 'part': stream.Part(), 'counter': 0 }

    def rest(self, name, duration=1.0):
        if isinstance(name, list):
            for item in name:
                if item == 'closed':
                    item = 'hihat'
                elif item == 'open':
                    item = 'hihat'
                elif item == 'pedal':
                    item = 'hihat'
                n = note.Rest()
                n.duration = m21duration.Duration(duration)
                self.kit[item]['part'].append(n)
                if duration:
                    self.kit[item]['counter'] += duration
        else:
            if name == 'closed':
                name = 'hihat'
            elif name == 'open':
                name = 'hihat'
            elif name == 'pedal':
                name = 'hihat'
            n = note.Rest()
            n.duration = m21duration.Duration(duration)
            self.kit[name]['part'].append(n)
            if duration:
                self.kit[name]['counter'] += duration

    def note(self, name, duration=1.0, volume=None, flam=0):
        if name == 'hihat' or name == 'closed':
            patch = self.instrument_map('hihat1')
            name = 'hihat'
        elif name == 'open':
            patch = self.instrument_map('hihat2')
            name = 'hihat'
        elif name == 'pedal':
            patch = self.instrument_map('hihat3')
            name = 'hihat'
        else:
            patch = self.instrument_map(self.kit[name]['instrument'])
        if volume is None:
            volume = self.volume
        if flam > 0:
            grace = note.Note(patch['num'])
            grace.volume.velocity = volume
            grace.duration = m21duration.Duration(flam)
            self.kit[name]['part'].append(grace)
        n = note.Note(patch['num'])
        n.volume.velocity = volume
        n.duration = m21duration.Duration(duration - flam)
        self.kit[name]['part'].append(n)
        if duration:
            self.kit[name]['counter'] += duration

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

    def pattern(self, patterns=None, duration=1/4):
        if not patterns:
            return
        for inst in self.kit.keys():
            if inst in patterns:
                for pattern_str in patterns[inst]:
                    for bit in pattern_str:
                        if bit == '0':
                            self.rest(inst, duration=duration)
                        else:
                            self.note(inst, duration=duration)

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
            'kick1': { 'num': 35, 'name': 'Acoustic Bass Drum', 'obj': instrument.BassDrum() },
            'kick2': { 'num': 36, 'name': 'Bass Drum 1', 'obj': instrument.BassDrum() },
            'snare1': { 'num': 38, 'name': 'Acoustic Snare', 'obj': instrument.SnareDrum() },
            'snare2': { 'num': 40, 'name': 'Electric Snare', 'obj': instrument.SnareDrum() },
            'sidestick': { 'num': 37, 'name': 'Side Stick', 'obj': instrument.SnareDrum() },
            'clap': { 'num': 39, 'name': 'Hand Clap', 'obj': instrument.Percussion() },
            'hihat1': { 'num': 42, 'name': 'Closed High Hat', 'obj': instrument.HiHatCymbal() },
            'hihat2': { 'num': 46, 'name': 'Open High Hat', 'obj': instrument.HiHatCymbal() },
            'hihat3': { 'num': 44, 'name': 'Pedal High Hat', 'obj': instrument.HiHatCymbal() },
            'crash1': { 'num': 49, 'name': 'Crash Cymbal 1', 'obj': instrument.CrashCymbals() },
            'crash2': { 'num': 57, 'name': 'Crash Cymbal 2', 'obj': instrument.CrashCymbals() },
            'china': { 'num': 52, 'name': 'Chinese Cymbal', 'obj': instrument.CrashCymbals() },
            'splash': { 'num': 55, 'name': 'Splash Cymbal', 'obj': instrument.CrashCymbals() },
            'ride1': { 'num': 51, 'name': 'Ride Cymbal 1', 'obj': instrument.RideCymbals() },
            'ride2': { 'num': 59, 'name': 'Ride Cymbal 2', 'obj': instrument.RideCymbals() },
            'ridebell': { 'num': 53, 'name': 'Ride Bell', 'obj': instrument.RideCymbals() },
            'tom1': { 'num': 50, 'name': 'High Tom', 'obj': instrument.TomTom() },
            'tom2': { 'num': 48, 'name': 'High Mid Tom', 'obj': instrument.TomTom() },
            'tom3': { 'num': 47, 'name': 'Low Mid Tom', 'obj': instrument.TomTom() },
            'tom4': { 'num': 45, 'name': 'Low Tom', 'obj': instrument.TomTom() },
            'tom5': { 'num': 43, 'name': 'High Floor Tom', 'obj': instrument.TomTom() },
            'tom6': { 'num': 41, 'name': 'Low Floor Tom', 'obj': instrument.TomTom() },
            'cowbell': { 'num': 56, 'name': 'Cowbell', 'obj': instrument.Cowbell() },
            'bongo1': { 'num': 60, 'name': 'High Bongo', 'obj': instrument.BongoDrums() },
            'bongo2': { 'num': 61, 'name': 'Low Bongo', 'obj': instrument.BongoDrums() },
            'conga1': { 'num': 63, 'name': 'Open High Conga', 'obj': instrument.CongaDrum() },
            'conga2': { 'num': 62, 'name': 'Mute High Conga', 'obj': instrument.CongaDrum() },
            'conga3': { 'num': 64, 'name': 'Low Conga', 'obj': instrument.CongaDrum() },
            'timbale1': { 'num': 65, 'name': 'High Timbale', 'obj': instrument.Timbales() },
            'timbale2': { 'num': 66, 'name': 'Low Timbale', 'obj': instrument.Timbales() },
            'tambourine': { 'num': 54, 'name': 'Tambourine', 'obj': instrument.Tambourine() },
            'shaker': { 'num': 70, 'name': 'Maracas', 'obj': instrument.Maracas() },
            'cabasa': { 'num': 69, 'name': 'Cabasa', 'obj': instrument.Percussion() },
            'claves': { 'num': 75, 'name': 'Claves', 'obj': instrument.Percussion() },
            'woodblock1': { 'num': 76, 'name': 'High Wood Block', 'obj': instrument.Woodblock() },
            'woodblock2': { 'num': 77, 'name': 'Low Wood Block', 'obj': instrument.Woodblock() },
            'triangle1': { 'num': 81, 'name': 'Open Triangle', 'obj': instrument.Triangle() },
            'triangle2': { 'num': 82, 'name': 'Mute Triangle', 'obj': instrument.Triangle() },
        }
        if key:
            return kit.get(key)
        else:
            return kit