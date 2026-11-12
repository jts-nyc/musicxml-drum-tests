#!/usr/bin/env python3
"""Compare a MusicXML file and/or a MIDI file with fixture/expected.csv.

  analyze.py xml  FILE.musicxml [label]   -> checks the file against the MusicXML rules for unpitched notes
  analyze.py midi FILE.mid      [label]   -> compares sounding notes with the answer key
  analyze.py csv  FILE.csv      [label]   -> the same, for a note list written by tools/reaper_import.lua
Appends rows to results/events.csv. Standard library only. 4/4 throughout.
"""
import sys, csv, struct, pathlib, collections
import xml.etree.ElementTree as ET
RUN = pathlib.Path(__file__).resolve().parent.parent
exp = [(int(r["bar"]), float(r["beat"]), int(r["midi_note"]), r["drum"]) for r in csv.DictReader(open(RUN/"fixture/expected.csv"))]
STEP = dict(C=0, D=2, E=4, F=5, G=7, A=9, B=11)

def xml_notes(path):
    root = ET.parse(path).getroot()
    inst = {}
    for si in root.iter("score-instrument"):
        inst[si.get("id")] = dict(name=si.findtext("instrument-name"), sound=si.findtext("instrument-sound"))
    for mi in root.iter("midi-instrument"):
        inst.setdefault(mi.get("id"), {}).update(channel=mi.findtext("midi-channel"), program=mi.findtext("midi-program"), unpitched=mi.findtext("midi-unpitched"))
    notes, info = [], dict(instruments=inst, clef=[c.findtext("sign") for c in root.iter("clef")])
    for part in root.findall("part"):
        for mi_, meas in enumerate(part.findall("measure"), 1):
            div = None; pos = 0; last = 0
            for el in meas:
                if el.tag == "attributes" and el.findtext("divisions"): xml_notes.div = int(el.findtext("divisions"))
                d = xml_notes.div
                if el.tag == "backup": pos -= int(el.findtext("duration"))
                elif el.tag == "forward": pos += int(el.findtext("duration"))
                elif el.tag == "note":
                    dur = int(el.findtext("duration") or 0)
                    start = last if el.find("chord") is not None else pos
                    if el.find("rest") is None:
                        u, p, i = el.find("unpitched"), el.find("pitch"), el.find("instrument")
                        n = dict(bar=mi_, beat=1 + start/d, kind="unpitched" if u is not None else "pitch",
                                 inst=i.get("id") if i is not None else None, head=el.findtext("notehead") or "normal",
                                 stem=el.findtext("stem"), voice=el.findtext("voice"))
                        src = u if u is not None else p
                        st = src.findtext("display-step") or src.findtext("step"); oc = src.findtext("display-octave") or src.findtext("octave")
                        n["display"] = f"{st}{oc}"; n["display_as_pitch"] = STEP[st] + 12*(int(oc)+1) if st else None
                        notes.append(n)
                    if el.find("chord") is None: last = pos; pos += dur
    return notes, info
xml_notes.div = 1

def midi_notes(path):
    b = open(path, "rb").read(); assert b[:4] == b"MThd"
    fmt, ntr, div = struct.unpack(">HHH", b[8:14]); i = 14; out = []
    for _ in range(ntr):
        assert b[i:i+4] == b"MTrk"; ln = struct.unpack(">I", b[i+4:i+8])[0]; j = i+8; end = j+ln; t = 0; rs = 0
        while j < end:
            v = 0
            while True:
                c = b[j]; j += 1; v = (v << 7) | (c & 0x7F)
                if c < 0x80: break
            t += v; st = b[j]
            if st == 0xFF:
                l = 0; j += 2
                while True:
                    c = b[j]; j += 1; l = (l << 7) | (c & 0x7F)
                    if c < 0x80: break
                j += l; continue
            if st in (0xF0, 0xF7):
                j += 1; l = 0
                while True:
                    c = b[j]; j += 1; l = (l << 7) | (c & 0x7F)
                    if c < 0x80: break
                j += l; continue
            if st & 0x80: rs = st; j += 1
            st = rs; hi = st & 0xF0
            if hi in (0xC0, 0xD0): j += 1; continue
            d1, d2 = b[j], b[j+1]; j += 2
            if hi == 0x90 and d2 > 0:
                q = t / div; out.append((int(q // 4) + 1, round(q % 4 + 1, 3), d1, (st & 0x0F) + 1))
        i = end
    return sorted(out)

def classify(want, got, display_pitch=None):
    if got == want: return "exact", ""
    if got is None: return "not_carried", "silent or missing"
    if got == want + 1: return "not_carried", "off by one"
    if display_pitch is not None and got == display_pitch: return "not_carried", "position read as pitch"
    if (got - want) % 12 == 0: return "not_carried", "octave shift"
    return "not_carried", "other"

def write(rows):
    p = RUN/"results/events.csv"; new = not p.exists()
    with open(p, "a", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(["label", "bar", "beat", "drum", "expected_note", "got_note", "channel", "verdict", "failure_class", "detail"])
        w.writerows(rows)

mode, path = sys.argv[1], sys.argv[2]; label = sys.argv[3] if len(sys.argv) > 3 else pathlib.Path(path).name
if mode == "xml":
    notes, info = xml_notes(path); inst = info["instruments"]
    by = collections.defaultdict(list)
    for n in notes: by[(n["bar"], round(n["beat"], 3))].append(n)
    rows, bad = [], collections.Counter(); 
    used = collections.Counter()
    for bar, beat, want, drum in exp:
        cands = by.get((bar, beat), [])
        hit = None
        for n in cands:
            i = inst.get(n["inst"] or "", {})
            snd = int(i["unpitched"]) - 1 if i.get("unpitched") else None
            if snd == want and not n.get("_used"): hit = (n, i, snd); n["_used"] = True; break
        if hit:
            n, i, snd = hit
            ok = n["kind"] == "unpitched" and i.get("channel") == "10"
            rows.append([label, bar, beat, drum, want, snd, i.get("channel"), "exact" if ok else "approximate", "" if ok else "kind/channel", f'{n["kind"]} display={n["display"]} head={n["head"]} stem={n["stem"]} voice={n["voice"]} inst={n["inst"]}'])
        else:
            bad["no note with matching instrument"] += 1
            rows.append([label, bar, beat, drum, want, None, None, "not_carried", "no matching instrument reference", "; ".join(f'{c["kind"]} {c["display"]} inst={c["inst"]}' for c in cands)])
    write(rows)
    v = collections.Counter(r[7] for r in rows)
    print(f"[{label}] notes in file: {len(notes)}  expected: {len(exp)}  verdicts: {dict(v)}")
    print("  clef signs:", sorted(set(info["clef"])), " score-instruments:", len([k for k, x in inst.items() if 'name' in x]))
    print("  notes using <unpitched>:", sum(n["kind"] == "unpitched" for n in notes), " with <instrument> ref:", sum(n["inst"] is not None for n in notes), " unresolved refs:", sum(n["inst"] is not None and n["inst"] not in inst for n in notes))
    print("  channels:", sorted({x.get("channel") for x in inst.values()}), " programs:", sorted({x.get("program") for x in inst.values()}), " instrument-sound present on:", sum(1 for x in inst.values() if x.get("sound")))
    seen = {}
    for n in notes:
        i = inst.get(n["inst"] or "", {}); 
        if i.get("unpitched"): seen[int(i["unpitched"]) - 1] = (i.get("name"), i["unpitched"], n["display"], n["display_as_pitch"], n["head"], n["stem"], n["voice"])
    print("  GM note | name | midi-unpitched | display | display read as pitch | notehead | stem | voice")
    for k in sorted(seen): print("   ", k, "|", " | ".join(str(x) for x in seen[k]))
else:
    DISPLAY = {}
    for n in xml_notes(RUN/"fixture/percussion-fixture-01.musicxml")[0]:
        DISPLAY[int(n["inst"].split("-I")[1]) - 1] = n["display_as_pitch"]
    if mode == "csv":   # notes listed by tools/reaper_import.lua
        got = sorted((int(r["bar"]), round(float(r["beat"]), 3), int(r["pitch"]), int(r["channel"])) for r in csv.DictReader(open(path)))
    else:
        got = midi_notes(path)
    pool = collections.defaultdict(list)
    for bar, beat, note, ch in got: pool[(bar, beat)].append((note, ch))
    rows = []
    for bar, beat, want, drum in exp:
        c = pool.get((bar, beat), [])
        m = next((x for x in c if x[0] == want), None)
        if m: c.remove(m); rows.append([label, bar, beat, drum, want, m[0], m[1], "exact" if m[1] == 10 else "approximate", "" if m[1] == 10 else "not channel 10", ""])
        else: rows.append([label, bar, beat, drum, want, None, None, None, None, ""])
    for r in rows:   # second pass: pair leftovers at the same time
        if r[7] is None:
            c = pool.get((r[1], r[2]), [])
            if c:
                g = next((x for x in c if x[0] == DISPLAY.get(r[4])), c[0]); c.remove(g)
                r[5], r[6] = g; r[7], r[8] = classify(r[4], g[0], DISPLAY.get(r[4]))
            else: r[7], r[8] = "not_carried", "silent or missing"
    extra = sum(len(v) for v in pool.values())
    write(rows); v = collections.Counter((r[7], r[8]) for r in rows)
    print(f"[{label}] midi note-ons: {len(got)}  expected: {len(exp)}  unexpected extra: {extra}  channels: {sorted({g[3] for g in got})}")
    for k, n in v.items(): print("  ", k, n)
    wrong = collections.OrderedDict()
    for r in rows:
        if r[7] != "exact": wrong.setdefault((r[3], r[4]), set()).add(r[5])
    for (drum, want), g in wrong.items(): print(f"   {drum} ({want}) -> {sorted(x for x in g if x is not None) or 'nothing'}")
