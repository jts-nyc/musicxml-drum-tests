-- Imports each fixture file into a NEW project tab in REAPER, changes nothing,
-- and writes every MIDI note it finds to results/reaper/<name>.csv.
-- Leaves the tabs open; close them without saving.
local script = select(2, reaper.get_action_context())
local run = script:match("^(.*[/\\])tools[/\\]")
local files = {
  {"percussion-fixture-01.musicxml", "unmodified"},
  {"percussion-fixture-01.mxl", "compressed"},
  {"control-no-instrument-refs.musicxml", "control-no-refs"},
  {"control-with-instrument-sound.musicxml", "control-with-sound"},
  {"percussion-fixture-01.mid", "midi"},
}
local log = io.open(run .. "results/reaper/log.txt", "w")
log:write("REAPER " .. reaper.GetAppVersion() .. "\n")
for _, f in ipairs(files) do
  reaper.Main_OnCommand(40859, 0)            -- New project tab
  reaper.SetEditCurPos(0, false, false)
  local ok = reaper.InsertMedia(run .. "fixture/" .. f[1], 1)   -- 1 = add as new track
  local out = io.open(run .. "results/reaper/" .. f[2] .. ".csv", "w")
  out:write("track,track_name,take_name,qn,bar,beat,pitch,channel,velocity,length_qn\n")
  local nt, ni, nn = reaper.CountTracks(0), reaper.CountMediaItems(0), 0
  for i = 0, ni - 1 do
    local item = reaper.GetMediaItem(0, i)
    local tr = reaper.GetMediaItemTrack(item)
    local _, trname = reaper.GetTrackName(tr)
    local trnum = math.floor(reaper.GetMediaTrackInfo_Value(tr, "IP_TRACKNUMBER"))
    for t = 0, reaper.CountTakes(item) - 1 do
      local take = reaper.GetTake(item, t)
      if take and reaper.TakeIsMIDI(take) then
        local _, cnt = reaper.MIDI_CountEvts(take)
        for n = 0, cnt - 1 do
          local _, _, _, s, e, ch, pitch, vel = reaper.MIDI_GetNote(take, n)
          local qs, qe = reaper.MIDI_GetProjQNFromPPQPos(take, s), reaper.MIDI_GetProjQNFromPPQPos(take, e)
          out:write(string.format("%d,%s,%s,%.4f,%d,%.3f,%d,%d,%d,%.4f\n", trnum, trname:gsub(",", " "), reaper.GetTakeName(take):gsub(",", " "),
            qs, math.floor(qs / 4 + 1e-6) + 1, (qs + 1e-6) % 4 + 1, pitch, ch + 1, vel, qe - qs))
          nn = nn + 1
        end
      end
    end
  end
  out:close()
  log:write(string.format("%s: InsertMedia=%s tracks=%d items=%d notes=%d\n", f[1], tostring(ok), nt, ni, nn))
end
log:write("done\n"); log:close()
