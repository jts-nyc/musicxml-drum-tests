# Percussion interchange test, run 01

2026-11-11 · MuseScore Studio 4.6.5 and REAPER 7.85 on macOS · stock 16-drum kit · 24 bars, 76 notes

MuseScore and REAPER are tested. Sibelius and Logic are not. Details of what was and was not covered are in [manifest.md](manifest.md); how to repeat it is in [METHOD.md](METHOD.md); every note is a row in [results/events.csv](results/events.csv).

## Results

| Test | Notes carried exactly | What happened to the rest |
|---|---|---|
| MuseScore MusicXML export, checked against the specification | 76 of 76 | n/a |
| MuseScore MIDI export, checked against the intended notes | 76 of 76 | n/a |
| MusicXML back into MuseScore, MIDI exported straight away | 76 of 76 | n/a |
| MusicXML back into MuseScore, saved, reopened, MIDI exported | 76 of 76 | n/a |
| Compressed `.mxl` back into MuseScore | 76 of 76 | n/a |
| Control: same file with an `<instrument-sound>` added per drum | 76 of 76 | n/a |
| **Control: same file with the per-note instrument references removed** | **0 of 76** | **All 76 played at the staff position read as a pitch** |
| **REAPER 7.85: the unmodified MusicXML export** | **0 of 76** | **All 76 at the staff position read as a pitch, on channel 1** |
| REAPER 7.85: the compressed `.mxl` | 0 of 76 | The same |
| REAPER 7.85: control with `<instrument-sound>` added | 0 of 76 | The same |
| REAPER 7.85: control with instrument references removed | 0 of 76 | The same notes, on channel 10 |
| REAPER 7.85: MuseScore's MIDI export of the same score | 76 of 76 | n/a |

## What the export contains

Every one of the 76 notes is written as `<unpitched>`, under a percussion clef, with a reference to one of 16 instruments. Every reference resolves. Every instrument is on channel 10 with `midi-unpitched` equal to the MIDI note plus one. That is what the MusicXML 4.0 pages for these elements describe.

It contains no `<instrument-sound>` on any drum.

The file was not validated against the MusicXML schema in this run; the schema files were not on the machine and nothing was downloaded.

## The failure, reproduced

REAPER 7.85 imports the unmodified export with every note at its staff position read as a pitch. MuseScore's own importer does exactly the same once the instrument references are removed from the file. Both produce this table, note for note:

| Drum | Correct note | Played instead | On a General MIDI kit that is |
|---|---|---|---|
| Bass Drum 2 | 35 | 64 | Low Conga |
| Bass Drum | 36 | 65 | High Timbale |
| Cross-stick | 37 | 72 | Long Whistle |
| Snare | 38 | 72 | Long Whistle |
| Floor Tom | 41 | 69 | Cabasa |
| Closed Hi-Hat | 42 | 79 | Open Cuica |
| Pedal Hi-Hat | 44 | 62 | Mute Hi Conga |
| Open Hi-Hat | 46 | 79 | Open Cuica |
| Low Tom | 47 | 74 | Long Güiro |
| Crash Cymbal | 49 | 81 | Open Triangle |
| High Tom | 50 | 76 | Hi Wood Block |
| Ride Cymbal | 51 | 77 | Low Wood Block |
| China Cymbal | 52 | 83 | (outside the General MIDI kit) |
| Ride Bell | 53 | 77 | Low Wood Block |
| Splash Cymbal | 55 | 84 | (outside the General MIDI kit) |
| Crash Cymbal 2 | 57 | 83 | (outside the General MIDI kit) |

Four pairs of different drums collapse onto one note: cross-stick and snare, closed and open hi-hat, ride and ride bell, china and second crash. A transpose cannot undo that, which matches the original reporter's "not just transposed".

## REAPER 7.85

- All 76 notes arrive at the right time and length. None has the right pitch.
- Every pitch equals the note's `display-step` and `display-octave` read as if they were a pitch. REAPER does not follow the note's `<instrument>` reference to its `midi-unpitched` value.
- Adding `<instrument-sound>` changes nothing.
- The notes land on channel 1 when the file has instrument references and on channel 10 when it has none. Why was not investigated.
- The track is named "Drum Kit", from the part name.
- The MIDI file exported from the same MuseScore score imports correctly: 76 of 76, channel 10. So the workaround in the issue (use MIDI) holds.
- REAPER showed its "MIDI File Import" dialog for each file. The defaults were accepted unchanged.

This confirms, with numbers and on REAPER's current release, what the contributor concluded from reading the file in May 2024.

## Smaller findings

1. **A notehead is lost in MuseScore's own round trip.** The China Cymbal uses a custom notehead. The export writes it as `<notehead smufl="noteheadHeavyXHat">other</notehead>`. After import and re-export it is `normal`. The sound is unaffected. Carried approximately. The same importer code is in v4.7.6 and on `main` (read on 2026-11-12, not run).
2. **`<instrument-sound>` made no difference to MuseScore's import** in this test, present or absent.
3. Staff positions, stems and voices of all 16 drums came back unchanged in the round-trip MusicXML.

## Limits of this run

- The notes were written into the score file by a script, on the kit's own default voices and stems, and not entered in the editor. The export code path is the same, but a hand-entered score is the stronger evidence for a public claim.
- 16 drums, not the 23 of the large kit named in the issue.
- The command line cannot show the known problem where sounds are wrong in the window until the score is saved and reopened (#20283). The two MIDI exports here agree, which says nothing about live playback.
- One version of each program, one machine. REAPER was tested through its Insert Media route, driven by a script; File › Open and drag-and-drop were not tried.

## Whose side, so far

| Question | Answer from this run |
|---|---|
| Is MuseScore 4.6.5's drum export correct? | Yes, on every point checked. |
| Does MuseScore read its own export correctly? | Yes for sound; one custom notehead is lost. |
| What does REAPER 7.85 do with it? | Ignores the instrument reference and plays the staff position as a pitch. 0 of 76 correct. |
| Whose side is the failure in #22702 on? | The importer's, on this evidence. The export gives the sound of every note in the way the specification's own percussion example does; REAPER does not read it. |
| Is the specification partly to blame? | It never states the rule in one place, and a reader that falls back to staff position contradicts only the phrase that display position does not imply pitch. That is a reading of the specification, not something this run measured. |
| What do Sibelius and Logic do? | Not tested. |
