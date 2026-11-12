#!/usr/bin/env python3
"""Build percussion-fixture-01.mscx from MuseScore's own Rock Band template.

Keeps only the template's stock Drum Kit part (instrument id drum-kit-5, 16 drums),
then writes: one bar per drum, a four-bar groove, and four collision bars.
Also writes fixture/expected.csv, the answer key (bar, beat, MIDI note).
Standard library only. Reads the template; writes only inside this run folder.
"""
import re, csv, sys, pathlib
TEMPLATE = pathlib.Path("/Applications/MuseScore 4.app/Contents/Resources/templates/06-Popular/01-Rock_Band/01-Rock_Band.mscx")
OUT = pathlib.Path(__file__).resolve().parent.parent / "fixture"
src = TEMPLATE.read_text(encoding="utf-8")

# --- header up to the first <Part>, the drum <Part>, nothing else -------------
head = src[:src.index("    <Part>")]
parts = re.findall(r"    <Part>.*?    </Part>\n", src, re.S)
drum_part = next(p for p in parts if "<useDrumset>1</useDrumset>" in p)
drum_part = drum_part.replace('<Staff id="6">', '<Staff id="1">')
head = head.replace("<text>Rock Band</text>", "<text>percussion-fixture-01</text>")

kit = []
for m in re.finditer(r'<Drum pitch="(\d+)">(.*?)</Drum>', drum_part, re.S):
    f = dict(re.findall(r"<(\w+)>([^<]*)</\1>", m.group(2)))
    kit.append(dict(pitch=int(m.group(1)), head=f["head"], line=int(f["line"]),
                    voice=int(f["voice"]), stem=int(f.get("stem", 0)), name=f["name"]))
K = {d["pitch"]: d for d in kit}
TPC = {0:14,1:21,2:16,3:11,4:18,5:13,6:20,7:15,8:10,9:17,10:12,11:19}
DUR = {"quarter":1.0, "eighth":0.5, "half":2.0}

def chord(pitches, dur):
    stem = {1:"up", 2:"down"}.get(K[pitches[0]]["stem"])
    s = f"          <Chord>\n            <durationType>{dur}</durationType>\n"
    if stem: s += f"            <StemDirection>{stem}</StemDirection>\n"
    for p in pitches:
        s += f"            <Note>\n              <pitch>{p}</pitch>\n              <tpc>{TPC[p%12]}</tpc>\n              </Note>\n"
    return s + "            </Chord>\n"
def rest(dur):
    if dur == "measure":
        return "          <Rest>\n            <durationType>measure</durationType>\n            <duration>4/4</duration>\n            </Rest>\n"
    return f"          <Rest>\n            <durationType>{dur}</durationType>\n            </Rest>\n"

expected = []   # (bar, beat, pitch)
def voice(events, bar):
    """events: list of (pitches|None, dur)."""
    out, beat = "", 1.0
    for pitches, dur in events:
        if pitches:
            out += chord(pitches, dur)
            expected.extend((bar, beat, p) for p in pitches)
        else:
            out += rest(dur)
        beat += DUR.get(dur, 4.0)
    return out
def measure(bar, v1, v2=None, first=False):
    s = "      <Measure>\n        <voice>\n"
    if first: s += "          <TimeSig>\n            <sigN>4</sigN>\n            <sigD>4</sigD>\n            </TimeSig>\n"
    s += voice(v1, bar) + "          </voice>\n"
    if v2: s += "        <voice>\n" + voice(v2, bar) + "          </voice>\n"
    return s + "        </Measure>\n"

R = [(None, "measure")]
bars, n = [], 0
# System 1: one drum per bar, ascending MIDI order, in the kit's own default voice
for d in kit:
    n += 1
    ev = [([d["pitch"]], "quarter"), (None, "quarter"), (None, "half")]
    bars.append(measure(n, R, ev, n == 1) if d["voice"] == 1 else measure(n, ev, None, n == 1))
# System 2: a groove
hh = lambda extra=(): [42, *extra]
n += 1; bars.append(measure(n, [([49],"eighth"),([42],"eighth"),(hh([38]),"eighth"),([42],"eighth"),([42],"eighth"),([42],"eighth"),(hh([38]),"eighth"),([42],"eighth")],
                            [([36],"quarter"),(None,"quarter"),([36],"quarter"),(None,"quarter")]))
n += 1; bars.append(measure(n, [([42],"eighth"),([42],"eighth"),(hh([38]),"eighth"),([42],"eighth"),([42],"eighth"),([42],"eighth"),(hh([38]),"eighth"),([46],"eighth")],
                            [([36],"quarter"),(None,"quarter"),([36],"quarter"),(None,"quarter")]))
n += 1; bars.append(measure(n, [([51],"quarter"),([51,38],"quarter"),([51],"quarter"),([51,38],"quarter")],
                            [([36],"quarter"),([44],"quarter"),([36],"quarter"),([44],"quarter")]))
n += 1; bars.append(measure(n, [([38],"eighth"),([38],"eighth"),([50],"eighth"),([50],"eighth"),([47],"eighth"),([47],"eighth"),([41],"eighth"),([41],"eighth")],
                            [([36],"quarter"),(None,"quarter"),([36],"quarter"),(None,"quarter")]))
# System 3: drums that share a staff position
for group in ([38,37,38,37], [42,46,42,46], [50,51,53,50], [52,57,52,57]):
    n += 1; bars.append(measure(n, [([p], "quarter") for p in group]))

body = '    <Staff id="1">\n      <VBox>\n        <height>10</height>\n        <Text>\n          <style>title</style>\n          <text>percussion-fixture-01</text>\n          </Text>\n        </VBox>\n' + "".join(bars) + "      </Staff>\n    </Score>\n  </museScore>\n"
OUT.mkdir(exist_ok=True)
(OUT / "percussion-fixture-01.mscx").write_text(head + drum_part + body, encoding="utf-8")
with open(OUT / "expected.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["bar", "beat", "midi_note", "drum"])
    for bar, beat, p in sorted(expected): w.writerow([bar, beat, p, K[p]["name"]])
with open(OUT / "kit.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["midi_note", "name", "line", "head", "voice", "stem"])
    for d in kit: w.writerow([d["pitch"], d["name"], d["line"], d["head"], d["voice"] + 1, {1:"up",2:"down"}.get(d["stem"], "auto")])
print(f"{len(kit)} drums, {n} bars, {len(expected)} notes")
