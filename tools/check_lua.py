#!/usr/bin/env python3
"""Smoke test: compile the addon's Lua files with a real Lua 5.1 (via lupa),
load the data file, and run the tooltip lookup with a few stubbed WoW APIs.

Usage: python -I check_lua.py <addon dir> [itemID ...]
"""
import os
import sys

from lupa import lua51

STUBS = r"""
-- minimal WoW API stubs so the addon's load-time code can run
local function stubFrame()
    local f = {}
    local scripts = {}
    local shown = true
    local text = ""
    setmetatable(f, { __index = function(t, k)
        if type(k) ~= "string" or not k:match("^%u") then return nil end  -- plain fields stay nil
        if k == "SetScript" then return function(self, name, fn) scripts[name] = fn end end
        if k == "GetScript" then return function(self, name) return scripts[name] end end
        if k == "HookScript" then return function(self, name, fn) scripts[name] = fn end end
        if k == "CreateFontString" or k == "CreateTexture" then return function() return stubFrame() end end
        if k == "GetName" then return function() return nil end end
        if k == "GetChecked" then return function() return true end end
        if k == "AddLine" then return function(self, text) ADDED[#ADDED + 1] = text end end
        if k == "GetItem" then return function(self) return nil, CURRENT_LINK end end
        if k == "GetFont" then return function() return "Fonts\\FRIZQT__.TTF", 12, "" end end
        if k == "SetText" then return function(self, v) text = v or "" end end
        if k == "GetText" then return function() return text end end
        if k == "Show" then return function() shown = true end end
        if k == "Hide" then return function() shown = false end end
        if k == "SetShown" then return function(self, v) shown = v and true or false end end
        if k == "IsShown" then return function() return shown end end
        if k == "GetStringHeight" then return function() return 14 * math.max(1, math.ceil(#text / 60)) end end
        if k:sub(1, 3) == "Get" then return function() return 100 end end
        return function() end
    end })
    return f
end
ADDED = {}
FRAMES = {}
CreateFrame = function(kind, name) local f = stubFrame(); FRAMES[#FRAMES + 1] = f; if name then _G[name] = f end; return f end
UIParent = stubFrame()
GameTooltip = stubFrame()
ItemRefTooltip = stubFrame()
SlashCmdList = {}
DEFAULT_CHAT_FRAME = { AddMessage = function(self, m) PRINTED[#PRINTED + 1] = m end }
PRINTED = {}
UnitFactionGroup = function() return FACTION end
FACTION = "Alliance"
Settings = nil
InterfaceOptions_AddCategory = function() end
UISpecialFrames = {}
HOOKS = {}
hooksecurefunc = function(a, b, c)
    if type(a) == "table" then
        local orig = a[b]
        a[b] = function(...) local r = { orig(...) }; c(...); return unpack(r) end
    else
        HOOKS[a] = b
    end
end
InCombatLockdown = function() return false end
wipe = function(t) for k in pairs(t) do t[k] = nil end return t end
C_GamePad = { IsEnabled = function() return true end }
InputUtil = { IsGamepadUIEnabled = function() return true end }
HandleModifiedItemClick = function() end
LoadAddOn = function(name) return true end
SetItemRef = function() end
IsAltKeyDown = function() return true end
CreateColor = function(r, g, b, a) return { r = r, g = g, b = b, a = a } end
ITEM_QUALITY_COLORS = { [0] = { r = 0.6, g = 0.6, b = 0.6 }, { r = 1, g = 1, b = 1 }, { r = 0.1, g = 1, b = 0 }, { r = 0, g = 0.4, b = 0.9 }, { r = 0.6, g = 0.2, b = 0.9 }, { r = 1, g = 0.5, b = 0 } }
GetItemInfo = function(id) if id == 6889 then return "Small Egg", "|Hitem:6889|h[Small Egg]|h", 1, 5, 0, "Trade Goods", "Meat", 20, "", 134033 end end
C_Map = {
    GetMapInfo = function(id) if id == 1437 then return { name = "Westfall", mapType = 3 } elseif id == 1412 then return { name = "Mulgore", mapType = 3 } end end,
    GetMapArtLayers = function(id) return { { layerWidth = 1002, layerHeight = 668, tileWidth = 256, tileHeight = 256 } } end,
    GetMapArtLayerTextures = function(id) return { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 } end,
}
"""


def main():
    addon_dir = sys.argv[1]
    items = [int(x) for x in sys.argv[2:]] or [4470, 6889, 2589, 18816]
    L = lua51.LuaRuntime(unpack_returned_tuples=True)
    L.execute(STUBS)
    g = L.globals()
    ns = L.table()

    for fname in ("WhereIsIt_Data.lua", "WhereIsIt.lua", "WhereIsIt_Book.lua", "WhereIsIt_Gamepad.lua"):
        path = os.path.join(addon_dir, fname)
        with open(path, "rb") as f:
            src = f.read()
        fn = L.eval("function(src, name) local f, err = loadstring(src, '@' .. name); if not f then error(err) end; return f end")(src, fname)
        fn("WhereIsIt", ns)
        print(f"{fname}: loaded OK ({os.path.getsize(path)/1e6:.2f} MB)")

    count = L.eval("function(t) local n = 0 for _ in pairs(t) do n = n + 1 end return n end")(ns.Data)
    print(f"data entries: {count}, version {ns.DataVersion}")
    lore = os.path.join(addon_dir, "WhereIsIt_Lore", "WhereIsIt_Lore.lua")
    if not os.path.exists(lore):
        lore = os.path.join(os.path.dirname(os.path.abspath(addon_dir)), "WhereIsIt_Lore", "WhereIsIt_Lore.lua")
    if os.path.exists(lore):
        with open(lore, "rb") as f:
            src = f.read()
        L.eval("function(src) local f, err = loadstring(src, '@WhereIsIt_Lore.lua'); if not f then error(err) end; return f end")(src)()
        n = L.eval("function(t) local n = 0 for _ in pairs(t) do n = n + 1 end return n end")(g.WhereIsIt_LoreData)
        print(f"lore entries: {n}, version {g.WhereIsIt_LoreVersion} ({os.path.getsize(lore)/1e6:.1f} MB)")

    # fire ADDON_LOADED on the loader frame so InitDB/InstallHooks/options run
    fired = L.eval("""function()
        local n = 0
        for _, f in ipairs(FRAMES) do
            local h = f:GetScript("OnEvent")
            if h then h(f, "ADDON_LOADED", "WhereIsIt"); h(f, "PLAYER_LOGIN"); n = n + 1 end
        end
        return n
    end""")()
    print(f"boot handlers fired: {fired}; db keys: {sorted(dict(g.WhereIsItDB).keys())}")
    # simulate a tooltip for item 6889 through the hooked OnTooltipSetItem
    L.execute("CURRENT_LINK = '|cffffffff|Hitem:6889::::::::60:::::|h[Small Egg]|h|r'")
    L.eval("function() local h = GameTooltip:GetScript('OnTooltipSetItem'); if h then h(GameTooltip) end end")()
    print("tooltip lines added:", list(g.ADDED.values()))
    for fac in ("Alliance", "Horde"):
        g.FACTION = fac
        for item in items:
            lines = ns.GetHint(item, "H" if fac == "Horde" else "A")
            print(f"  [{fac}] {item}: " + (" | ".join(lines.values()) if lines else "(no record)"))
    # slash command sanity
    g.SlashCmdList.WHEREISIT("help")
    print("slash output:", list(g.PRINTED.values())[-1])

    # encyclopedia: open, render an entry for both factions, search, alt-click hook
    book = ns.Book
    book.Show(book, 6889)
    print("book opened for item 6889; title:", g.WhereIsItBook.L.title.GetText(g.WhereIsItBook.L.title))
    for fac in ("A", "H"):
        fr = g.WhereIsItBook
        fr.facOverride = fac
        book.Render(book)
        print(f"  [{fac}] caption: {fr.R.caption.GetText(fr.R.caption)}")
        print(f"  [{fac}] rows: " + " | ".join(r.text.GetText(r.text) for r in fr.L.rows.values() if r.text.IsShown(r.text)))
        print(f"  [{fac}] uses: {fr.L.uses.GetText(fr.L.uses)}")
    fr = g.WhereIsItBook
    paras = ns.GetLore(6889, "A")
    print("  lore paragraphs for 6889:", len(paras) if paras else 0, "| first 90 chars:", (paras[1][:90] if paras else None))
    fr.facOverride = None
    book.Render(book)
    print(f"  leaf {fr.leaf or 1} of {fr.leafCount}; account head shown: {fr.L.accountHead.IsShown(fr.L.accountHead)}; page button: {fr.leafBtn.label.GetText(fr.leafBtn.label) if fr.leafBtn.IsShown(fr.leafBtn) else None}")
    book.TurnLeaf(book, 1)
    print(f"  after turn: leaf {fr.leaf}; title shown: {fr.L.title.IsShown(fr.L.title)}; head: {fr.L.accountHead.GetText(fr.L.accountHead)}; para1: {fr.L.account[1].GetText(fr.L.account[1])[:60]}")
    book.TurnLeaf(book, -1)
    book.Show(book, 2589)
    print(f"  item 2589: leaf {fr.leaf} of {fr.leafCount}; shown on leaf 1: {sum(1 for a in fr.L.account.values() if a.IsShown(a))} para(s); page button: {fr.leafBtn.label.GetText(fr.leafBtn.label) if fr.leafBtn.IsShown(fr.leafBtn) else None}")
    book.TurnLeaf(book, 1)
    print(f"  after turn: leaf {fr.leaf}; title shown: {fr.L.title.IsShown(fr.L.title)}; head: {fr.L.accountHead.GetText(fr.L.accountHead)}; page button: {fr.leafBtn.label.GetText(fr.leafBtn.label)}; para: {fr.L.account[1].GetText(fr.L.account[1])[:50]}")
    book.Show(book, 6889)
    fr.search.SetText(fr.search, "egg")
    book.UpdateIndex(book)
    print("  search 'egg':", fr.R.indexNote.GetText(fr.R.indexNote), "| first:", fr.results[1].name.GetText(fr.results[1].name))
    g.HOOKS["HandleModifiedItemClick"]("|Hitem:2589::::::::60:::::|h[Linen Cloth]|h")
    print("  alt-click opened item:", fr.itemID, "history:", list(g.WhereIsItDB.history.values()))

    # gamepad: find the catcher (last frame with OnGamePadButtonDown) and press some buttons
    L.execute("""
        for _, f in ipairs(FRAMES) do
            local h = f:GetScript("OnGamePadButtonDown")
            if h then PAD_CATCHER = f end
        end
    """)
    pad = ns.Gamepad
    print("  gamepad active:", pad.active, "catcher found:", g.PAD_CATCHER is not None)
    for key in ("PADDDOWN", "PADDDOWN", "PADDLEFT", "PAD3", "PADRTRIGGER", "PADLSHOULDER", "PAD1"):
        down = g.PAD_CATCHER.GetScript(g.PAD_CATCHER, "OnGamePadButtonDown")
        up = g.PAD_CATCHER.GetScript(g.PAD_CATCHER, "OnGamePadButtonUp")
        down(g.PAD_CATCHER, key); up(g.PAD_CATCHER, key)
    print(f"  gamepad presses: {pad.presses}, last: {pad.lastKey}, book item now: {fr.itemID}, faction: {fr.currentFac}")
    print("  legend:", fr.R.legend.GetText(fr.R.legend))


if __name__ == "__main__":
    main()
