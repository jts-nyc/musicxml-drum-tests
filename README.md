# MusicXML drum import tests

Do drum parts survive the trip from one music program to another? This repository holds
a drum-kit score built to test that, the files each program produced, and a note-by-note
count of what arrived.

A MusicXML drum note has two parts. One is where it sits on the staff. The other is
which drum it is, given by the note's `<instrument>` reference, which points to a
`<midi-unpitched>` number. A program that reads the staff position as a pitch plays the
wrong drum on every note.

## Results so far

| Run | Programs | Result |
|---|---|---|
| [run-01](run-01/REPORT.md), 2026-11-11 | MuseScore Studio 4.6.5 → REAPER 7.85, macOS | MuseScore reads its own export correctly: 76 of 76 notes. REAPER gets 0 of 76 from MusicXML and 76 of 76 from the same score's MIDI export. REAPER plays every note at its staff position read as a pitch. |

Related: [musescore/MuseScore#22702](https://github.com/musescore/MuseScore/issues/22702).

## Layout

Each run folder has:

- `REPORT.md`: the results;
- `manifest.md`: the versions, the machine, and what was and wasn't tested;
- `METHOD.md`: how to repeat it, or test another program;
- `fixture/`: the score in every format, with `expected.csv` as the answer key;
- `results/`: every output file, plus `events.csv`, which has one row per note;
- `tools/`: the scripts, which need only the Python 3 standard library (plus a ReaScript for REAPER).

## Adding a program

Follow `METHOD.md` in the latest run: import the fixture unchanged, export MIDI straight
away, and run `tools/analyze.py` on it. Results from Sibelius, Logic, Dorico, Cubase and
other programs are welcome, as an issue or a pull request. Give the program's version
and say whether the import showed any options.

## License

MIT; see [LICENSE](LICENSE).
