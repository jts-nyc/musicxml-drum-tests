# MusicXML drum import tests

Do drum parts survive the trip from one music program to another? This repository holds
a drum-kit score built to test that, the files each program produced, and a note-by-note
count of what arrived.

A MusicXML drum note has two parts. One is where it sits on the staff. The other is
which drum it is, given by the note's `<instrument>` reference, which points to a
`<midi-unpitched>` number. In this score, reading the staff position as a pitch gives the
wrong MIDI note for all 76 notes.

## Results so far

| Run | Programs | Result |
|---|---|---|
| [run-01](run-01/REPORT.md), 2026-11-11 | MuseScore Studio 4.6.5 → REAPER 7.85, macOS | MuseScore keeps all 76 MIDI note numbers when it re-imports its own export; one custom notehead is lost. REAPER gets 0 of 76 from MusicXML and 76 of 76 from the same score's MIDI export. REAPER imports every note at its staff position read as a pitch. |
| [run-02](run-02/REPORT.md), 2026-11-12 | MuseScore Studio 4.7.6 → REAPER 7.85, macOS | The same on every count. MuseScore: 76 of 76. REAPER: 0 of 76 from MusicXML, 76 of 76 from MIDI. The drum mapping in the 4.7.6 MusicXML export is unchanged; it differs from the 4.6.5 one in layout, metadata and part-name visibility. The MIDI export is byte-identical. |

Related: [musescore/MuseScore#22702](https://github.com/musescore/MuseScore/issues/22702).

## Layout

Each run folder has:

- `REPORT.md`: the results;
- `manifest.md`: the versions, the machine, and what was and wasn't tested (run-01; later runs point back to it);
- `METHOD.md`: how to repeat it, or test another program (run-01);
- `fixture/`: the score in every format, with `expected.csv` as the answer key;
- `results/`: every output file, plus `events.csv`, which has one row per note;
- `tools/`: the scripts, which need only the Python 3 standard library (plus a ReaScript for REAPER).

## Adding a program

Follow [run-01/METHOD.md](run-01/METHOD.md): import the fixture unchanged, export MIDI straight
away, and run `tools/analyze.py` on it. Results from Sibelius, Logic, Dorico, Cubase and
other programs are welcome, as an issue or a pull request. Give the program's version
and say whether the import showed any options.

## License

MIT; see [LICENSE](LICENSE).
