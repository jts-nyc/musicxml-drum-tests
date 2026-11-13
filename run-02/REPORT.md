# Run 02: repeated with MuseScore Studio 4.7.6

Date: 2026-11-12. Same score, tools and answer key as run 01, run from MuseScore's command line. The method is in [run-01/METHOD.md](../run-01/METHOD.md); versions and machine are as in [run-01/manifest.md](../run-01/manifest.md) apart from MuseScore. The installed version is now 4.7.6; run 01's files and hashes are kept.

## Result

Identical to run 01 on every count.

| Check | Correct MIDI note numbers |
|---|---|
| MusicXML export (unpitched, references resolve, channel 10, midi-unpitched = note + 1) | 76 of 76 |
| MIDI export | 76 of 76 |
| Re-import of the MusicXML, first import | 76 of 76 |
| Re-import, after save and reopen | 76 of 76 |
| Re-import from .mxl | 76 of 76 |
| Control with instrument-sound added | 76 of 76 |
| Control with instrument references removed | 0 of 76, every note at its staff position read as a pitch |

- The 4.7.6 MusicXML export differs from the 4.6.5 one only in layout numbers (measure widths, note positions, page margins), the software and date lines, and `print-object="no"` on the part name. The drum mapping is the same.
- The MIDI export is byte-identical to run 01's.
- The China Cymbal's `other`/`noteheadHeavyXHat` notehead is again exported correctly (3 notes) and missing after the round trip.
- Still no `<instrument-sound>` in the export.

## REAPER 7.85 on the 4.7.6 files

Rerun on 2026-11-12 with the run 01 protocol: `tools/reaper_import.lua` (the copy here differs from the one run only in how it finds its folder) passed to REAPER 7.85 (macOS arm64), one new project tab per file, Insert Media, import dialogs accepted unchanged, tabs closed without saving. Notes are in `results/reaper/*.csv`.

| File | Correct MIDI note numbers | What happened |
|---|---|---|
| MusicXML export, unmodified | 0 of 76 | Every note at its staff position read as a pitch, channel 1 |
| Compressed `.mxl` | 0 of 76 | The same |
| Control with `<instrument-sound>` added | 0 of 76 | The same |
| Control with instrument references removed | 0 of 76 | The same notes, channel 10 |
| MuseScore's MIDI export of the same score | 76 of 76 | Channel 10 |

All five result files are byte-identical to run 01's. Onsets are right in all five. The MusicXML imports also keep the notated lengths; the MIDI import's notes are about 0.002 quarter notes shorter (0.9979 for a quarter note) and have velocity 80, which may come from MuseScore's MIDI export (not checked).

REAPER showed its "MIDI File Import" dialog four times for the five files: for the four MusicXML files and not for the MIDI file.

## Limits

Same as run 01: a script-built score, the 16-drum kit, no schema validation, no listening check. REAPER was tested through Insert Media only; File › Open and drag-and-drop were not tried.

## Hashes (SHA-256)

    54befee2c50e6f48f51af7f74fca93e0bc962943dba4243bebfefd36bb6c6772  control-no-instrument-refs.musicxml
    e3a9c4c9a39a3f56e3a5aa6165b39ffc06e35a8649794627f7f07386192ff727  control-with-instrument-sound.musicxml
    b9f941f5a8b8aee4ea892abbc7dbb1dc953335cb679e1333b8f5e017d0de3cde  expected.csv
    fda28c2b61cf2c7ce701887626b55192f75e6cc15cb5f6e49a214ddb804b8caf  kit.csv
    7d0de934dce590e3757072fa3ffba5706f91cef22af0631267d6655ba14c9c64  percussion-fixture-01.mid
    2b3f12363f0d783de8e60c45057fb5dfb4cc461a0c62c4e545043781b590c1ca  percussion-fixture-01.mscx
    d9aa8ab836193e434fc67a5c112f594c25afff5eb54495ceead092d3dbbce3bb  percussion-fixture-01.mscz
    db86951b8ab87e3f919a8d7d9617be2736c280da15b666dd72a4aa3ea497c585  percussion-fixture-01.musicxml
    eca75f482561f5ef106282dd4fa0861f07b5f859384fa71387699aecc6ba53df  percussion-fixture-01.mxl

Corrected on 2026-11-12: the first version of this list repeated run 01's hashes for the files that differ between the runs.
