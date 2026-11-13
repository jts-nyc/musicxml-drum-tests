# How to repeat or extend this run

Everything uses Python 3's standard library and MuseScore's own command line. Nothing is installed.

## Rebuild the fixture and the MuseScore results

```bash
python3 tools/build_fixture.py
```

Then, with `M="/Applications/MuseScore 4.app/Contents/MacOS/mscore"`, export each format with `"$M" -o fixture/percussion-fixture-01.EXT fixture/percussion-fixture-01.mscx` for `mscz`, `musicxml`, `mxl`, `mid` and `pdf`. MuseScore prints crash-reporter warnings when run this way; the files are still written.

`fixture/expected.csv` is the answer key: bar, beat and MIDI note for all 76 notes.

## Test another program

1. Open `fixture/percussion-fixture-01.musicxml` in the program as a new document. Change nothing.
2. Note what you see before touching anything: is it a drum staff, are the noteheads right, does playback sound like a kit.
3. Export a MIDI file straight away, to `results/<program>/import.mid`.
4. Run:

```bash
python3 tools/analyze.py midi results/<program>/import.mid "<Program and version> import"
```

It prints how many of the 76 notes have the expected onset and MIDI note number, and for the rest, which note each drum became and whether that matches the staff-position signature, an off-by-one, or an octave shift. Rows are appended to `results/events.csv`.

Folders are ready for `results/sibelius/` and `results/logic/`. For REAPER, also note its version and whether the import offered any options.

## REAPER

With REAPER open, run `tools/reaper_import.lua` (Actions › Show action list › New action › Load ReaScript, or pass the file to REAPER on the command line with `-nonewinst`). It opens one new project tab per fixture file, inserts the file, and writes every note it finds to `results/reaper/*.csv`. Accept each import dialog unchanged. Then:

```bash
python3 tools/analyze.py csv results/reaper/unmodified.csv "REAPER <version> import: unmodified MusicXML"
```

Close the tabs without saving.

## The two controls

- `fixture/control-no-instrument-refs.musicxml`: per-note instrument references removed. Shows what a program falls back to.
- `fixture/control-with-instrument-sound.musicxml`: a sound id added to each drum. Tests whether adding it changes the imported notes.

## Checking a MusicXML file

```bash
python3 tools/analyze.py xml path/to/file.musicxml "label"
```
