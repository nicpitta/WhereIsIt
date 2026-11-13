-- Where Is It: adds an encyclopedia-style "where is this usually found" line
-- to item tooltips. Deliberately vague: creature kinds and regions, never
-- coordinates, NPC names or drop percentages.
local ADDON, ns = ...

local DEFAULTS = {
    enabled = true,
    maxLines = 2,          -- 1..3 lines of hint text
    faction = "auto",      -- auto | alliance | horde | both
    showUnknown = false,   -- show a line for items with no record
    altHint = true,        -- faint "Alt-click to open the encyclopedia" line
    altClick = true,       -- Alt-click items/links opens the book
    color = { 0.80, 0.72, 0.52 },
    history = {},          -- recently consulted item IDs
    minimap = { angle = 200, hide = false },
}

local ICON = "|TInterface\\Icons\\INV_Misc_Book_11:12:12:0:0:64:64:5:59:5:59|t "

-- key binding (Bindings.xml); bind a controller button to it under Key Bindings > AddOns
BINDING_HEADER_WHEREISIT = "Where Is It"
BINDING_NAME_WHEREISIT_TOGGLE = "Open or close the encyclopedia"
function WhereIsIt_ToggleBook()
    if ns.Book then ns.Book:Toggle() end
end
local UNKNOWN_TEXT = "The archives hold no record of this item."

-- ---------------------------------------------------------------------------
-- Saved variables
-- ---------------------------------------------------------------------------
local db
local function InitDB()
    WhereIsItDB = WhereIsItDB or {}
    db = WhereIsItDB
    for k, v in pairs(DEFAULTS) do
        if db[k] == nil then
            if type(v) == "table" then
                local copy = {}
                for i, x in pairs(v) do copy[i] = x end
                db[k] = copy
            else
                db[k] = v
            end
        end
    end
    ns.db = db
end

-- Forever/Midnight clients can hand addons "secret" values that cannot be
-- compared or printed. Treat those as missing.
local function Plain(v)
    if type(issecretvalue) == "function" and issecretvalue(v) then
        return nil
    end
    return v
end

-- ---------------------------------------------------------------------------
-- Lookup
-- ---------------------------------------------------------------------------
local function PlayerFactionKey()
    local setting = db and db.faction or "auto"
    if setting == "alliance" then return "A" end
    if setting == "horde" then return "H" end
    if setting == "both" then return "both" end
    if type(UnitFactionGroup) == "function" then
        local ok, fac = pcall(UnitFactionGroup, "player")
        fac = ok and Plain(fac) or nil
        if fac == "Horde" then return "H" end
    end
    return "A"
end

-- Returns a list of hint lines for the item, or nil.
-- The encyclopedia's full accounts live in the load-on-demand sub-addon
-- WhereIsIt_Lore, so the tooltip never pays for them. Loaded the first time
-- the book asks.
local loreTried
function ns.LoadLore()
    if WhereIsIt_LoreData then return true end
    if loreTried then return false end
    loreTried = true
    local load = (C_AddOns and C_AddOns.LoadAddOn) or LoadAddOn
    if load then pcall(load, "WhereIsIt_Lore") end
    return WhereIsIt_LoreData ~= nil
end

-- Paragraphs of the account for an item, with shared passages expanded.
function ns.GetLore(itemID, facKey)
    if not ns.LoadLore() then return nil end
    local entry = WhereIsIt_LoreData[itemID]
    if not entry then return nil end
    local text = type(entry) == "table" and (entry[facKey] or entry.A or entry.H) or entry
    if type(text) ~= "string" then return nil end
    local shared = WhereIsIt_LoreShared or {}
    text = text:gsub("{(%w+)|([^}]+)}", function(kind, key)
        local t = shared[kind]
        return t and t[key] or ""
    end)
    local paras = {}
    for p in text:gmatch("[^\n]+") do paras[#paras + 1] = p end
    return paras
end

function ns.GetHint(itemID, facKey)
    local entry = ns.Data and ns.Data[itemID]
    if not entry then return nil end
    facKey = facKey or PlayerFactionKey()
    local text
    if type(entry) == "string" then
        text = entry
    elseif facKey == "both" then
        local a, h = entry.A or "", entry.H or ""
        text = "|cff7fb2ffAlliance:|r " .. a:gsub("\n", "\n") .. "\n|cffff7f7fHorde:|r " .. h
        local lines = {}
        for line in text:gmatch("[^\n]+") do lines[#lines + 1] = line end
        return lines
    else
        text = entry[facKey] or entry.A or entry.H
    end
    if not text then return nil end
    local lines = {}
    for line in text:gmatch("[^\n]+") do lines[#lines + 1] = line end
    return lines
end

-- ---------------------------------------------------------------------------
-- Tooltip handling
-- ---------------------------------------------------------------------------
local function TooltipItemID(tooltip, data)
    if type(data) == "table" then
        local id = Plain(data.id)
        if type(id) == "number" then return id end
    end
    if tooltip and tooltip.GetItem then
        local ok, _, link = pcall(tooltip.GetItem, tooltip)
        link = ok and Plain(link) or nil
        if type(link) == "string" then
            local id = link:match("item:(%d+)")
            if id then return tonumber(id) end
        end
    end
    return nil
end

local function AddHint(tooltip, data)
    if not db or not db.enabled then return end
    local itemID = TooltipItemID(tooltip, data)
    if not itemID then return end
    -- the client can announce the same item twice for one tooltip
    if tooltip.wiiShownFor == itemID then return end
    tooltip.wiiShownFor = itemID

    local lines = ns.GetHint(itemID)
    local r, g, b = db.color[1], db.color[2], db.color[3]
    if not lines then
        if db.showUnknown then
            tooltip:AddLine(ICON .. UNKNOWN_TEXT, 0.6, 0.6, 0.6, true)
        end
        return
    end
    local max = (db.faction == "both") and #lines or (db.maxLines or 2)
    for i = 1, math.min(max, #lines) do
        local prefix = (i == 1) and ICON or "    "
        tooltip:AddLine(prefix .. lines[i], r, g, b, true)
    end
    if db.altHint and ns.Book and #lines > 0 then
        local more = #lines > max and (" (" .. (#lines - max) .. " more)") or ""
        tooltip:AddLine("    |cff8a7a5cAlt-click to open the encyclopedia" .. more .. "|r", 0.54, 0.48, 0.36)
    end
    if tooltip.Show then tooltip:Show() end
end

local function SafeAddHint(tooltip, data)
    pcall(AddHint, tooltip, data)
end

local function ClearTooltip(tooltip)
    tooltip.wiiShownFor = nil
end

local hooked = false
local function InstallHooks()
    if hooked then return end
    hooked = true
    local tooltips = { GameTooltip, ItemRefTooltip, ShoppingTooltip1, ShoppingTooltip2,
                       ItemRefShoppingTooltip1, ItemRefShoppingTooltip2 }

    -- Newer clients announce tooltip items through TooltipDataProcessor;
    -- classic-style clients fire OnTooltipSetItem. Use whichever exists.
    local viaProcessor = false
    if TooltipDataProcessor and TooltipDataProcessor.AddTooltipPostCall
        and Enum and Enum.TooltipDataType and Enum.TooltipDataType.Item then
        viaProcessor = pcall(TooltipDataProcessor.AddTooltipPostCall, Enum.TooltipDataType.Item, SafeAddHint)
    end
    for _, tip in ipairs(tooltips) do
        if tip and tip.HookScript then
            if not viaProcessor then
                pcall(tip.HookScript, tip, "OnTooltipSetItem", function(self) SafeAddHint(self) end)
            end
            pcall(tip.HookScript, tip, "OnTooltipCleared", function(self) ClearTooltip(self) end)
            pcall(tip.HookScript, tip, "OnHide", function(self) ClearTooltip(self) end)
        end
    end
end

-- ---------------------------------------------------------------------------
-- Options panel (plain frames so it works on Forever, Classic and Retail)
-- ---------------------------------------------------------------------------
local function BuildOptionsPanel()
    local panel = CreateFrame("Frame", "WhereIsItOptionsPanel", UIParent)
    panel.name = "Where Is It"
    panel:Hide()

    local title = panel:CreateFontString(nil, "ARTWORK", "GameFontNormalLarge")
    title:SetPoint("TOPLEFT", 16, -16)
    title:SetText("Where Is It")

    local sub = panel:CreateFontString(nil, "ARTWORK", "GameFontHighlightSmall")
    sub:SetPoint("TOPLEFT", title, "BOTTOMLEFT", 0, -6)
    sub:SetWidth(560)
    sub:SetJustifyH("LEFT")
    sub:SetText("Item tooltips gain a short note on where an item is usually found: the kind of creature, merchant or craft, and the one or two regions where it is most plentiful for your faction. No coordinates, no names.\n\nData: " .. tostring(ns.DataVersion or "?") .. " (vmangos + pfQuest). Slash command: /wii")

    local function Check(label, key, anchor, dy)
        local cb = CreateFrame("CheckButton", nil, panel, "InterfaceOptionsCheckButtonTemplate")
        cb:SetPoint("TOPLEFT", anchor, "BOTTOMLEFT", 0, dy or -8)
        local text = cb.Text or _G[cb:GetName() and (cb:GetName() .. "Text")]
        if not text then
            text = cb:CreateFontString(nil, "ARTWORK", "GameFontHighlight")
            text:SetPoint("LEFT", cb, "RIGHT", 4, 0)
        end
        text:SetText(label)
        cb:SetScript("OnShow", function(self) self:SetChecked(db[key] and true or false) end)
        cb:SetScript("OnClick", function(self) db[key] = self:GetChecked() and true or false end)
        return cb
    end

    local enabled = Check("Show hints on item tooltips", "enabled", sub, -16)
    local unknown = Check("Mention items that have no record", "showUnknown", enabled)
    local althint = Check("Add the faint 'Alt-click to open the encyclopedia' line", "altHint", unknown)
    unknown = Check("Alt-clicking an item or item link opens the encyclopedia", "altClick", althint)

    -- lines 1..3
    local linesLabel = panel:CreateFontString(nil, "ARTWORK", "GameFontNormal")
    linesLabel:SetPoint("TOPLEFT", unknown, "BOTTOMLEFT", 0, -16)
    linesLabel:SetText("Lines of hint text")
    local lineButtons = {}
    local function RefreshLines()
        for n, b in pairs(lineButtons) do b:SetChecked(db.maxLines == n) end
    end
    local prev = linesLabel
    for n = 1, 3 do
        local b = CreateFrame("CheckButton", nil, panel, "UIRadioButtonTemplate")
        b:SetPoint("TOPLEFT", prev, "BOTTOMLEFT", n == 1 and 0 or 0, n == 1 and -6 or -4)
        local t = b:CreateFontString(nil, "ARTWORK", "GameFontHighlightSmall")
        t:SetPoint("LEFT", b, "RIGHT", 4, 0)
        t:SetText(n == 1 and "One line (the most useful source only)" or n == 2 and "Two lines" or "Three lines")
        b:SetScript("OnClick", function() db.maxLines = n; RefreshLines() end)
        lineButtons[n] = b
        prev = b
    end

    local facLabel = panel:CreateFontString(nil, "ARTWORK", "GameFontNormal")
    facLabel:SetPoint("TOPLEFT", prev, "BOTTOMLEFT", 0, -16)
    facLabel:SetText("Regions shown for")
    local facButtons = {}
    local function RefreshFac()
        for k, b in pairs(facButtons) do b:SetChecked(db.faction == k) end
    end
    prev = facLabel
    for _, opt in ipairs({ { "auto", "My character's faction" }, { "alliance", "Alliance" }, { "horde", "Horde" }, { "both", "Both (two sets of lines)" } }) do
        local b = CreateFrame("CheckButton", nil, panel, "UIRadioButtonTemplate")
        b:SetPoint("TOPLEFT", prev, "BOTTOMLEFT", 0, prev == facLabel and -6 or -4)
        local t = b:CreateFontString(nil, "ARTWORK", "GameFontHighlightSmall")
        t:SetPoint("LEFT", b, "RIGHT", 4, 0)
        t:SetText(opt[2])
        b:SetScript("OnClick", function() db.faction = opt[1]; RefreshFac() end)
        facButtons[opt[1]] = b
        prev = b
    end

    panel:SetScript("OnShow", function() RefreshLines(); RefreshFac() end)

    if Settings and Settings.RegisterCanvasLayoutCategory and Settings.RegisterAddOnCategory then
        local category = Settings.RegisterCanvasLayoutCategory(panel, panel.name)
        Settings.RegisterAddOnCategory(category)
        ns.settingsCategory = category
    elseif InterfaceOptions_AddCategory then
        InterfaceOptions_AddCategory(panel)
    end
    ns.optionsPanel = panel
end

local function OpenOptions()
    if ns.settingsCategory and Settings and Settings.OpenToCategory then
        local id = ns.settingsCategory.GetID and ns.settingsCategory:GetID() or ns.settingsCategory.ID
        local ok = pcall(Settings.OpenToCategory, id)
        if not ok then pcall(Settings.OpenToCategory, ns.settingsCategory) end
    elseif InterfaceOptionsFrame_OpenToCategory and ns.optionsPanel then
        InterfaceOptionsFrame_OpenToCategory(ns.optionsPanel)
        InterfaceOptionsFrame_OpenToCategory(ns.optionsPanel)
    end
end
ns.OpenOptions = OpenOptions

-- ---------------------------------------------------------------------------
-- Slash commands
-- ---------------------------------------------------------------------------
local function Print(msg)
    (DEFAULT_CHAT_FRAME or ChatFrame1):AddMessage("|cffd8b36aWhere Is It:|r " .. tostring(msg))
end

SLASH_WHEREISIT1 = "/whereisit"
SLASH_WHEREISIT2 = "/wii"
SlashCmdList.WHEREISIT = function(msg)
    msg = (msg or ""):lower():gsub("^%s+", ""):gsub("%s+$", "")
    local cmd, arg = msg:match("^(%S+)%s*(.*)$")
    cmd = cmd or ""
    arg = arg or ""
    if cmd == "toggle" or cmd == "on" or cmd == "off" then
        if cmd == "toggle" then db.enabled = not db.enabled else db.enabled = (cmd == "on") end
        Print(db.enabled and "hints enabled." or "hints disabled.")
    elseif cmd == "lines" and tonumber(arg) then
        db.maxLines = math.max(1, math.min(3, math.floor(tonumber(arg))))
        Print("showing up to " .. db.maxLines .. " line(s).")
    elseif cmd == "faction" and (arg == "auto" or arg == "alliance" or arg == "horde" or arg == "both") then
        db.faction = arg
        Print("regions shown for: " .. arg)
    elseif cmd == "unknown" then
        db.showUnknown = not db.showUnknown
        Print(db.showUnknown and "items without a record will say so." or "items without a record stay silent.")
    elseif cmd == "find" and tonumber(arg) then
        local lines = ns.GetHint(tonumber(arg))
        if lines then for _, l in ipairs(lines) do Print(l) end else Print(UNKNOWN_TEXT) end
    elseif cmd == "althint" then
        db.altHint = not db.altHint
        Print(db.altHint and "the Alt-click reminder is shown on tooltips." or "the Alt-click reminder is hidden.")
    elseif cmd == "altclick" then
        db.altClick = not db.altClick
        Print(db.altClick and "Alt-click opens the encyclopedia." or "Alt-click does nothing.")
    elseif (cmd == "search" or cmd == "look" or cmd == "lookup") and ns.Book then
        if tonumber(arg) then ns.Book:Show(tonumber(arg)) else ns.Book:Search(arg) end
    elseif cmd == "book" and ns.Book then
        ns.Book:Toggle()
    elseif cmd == "minimap" then
        db.minimap = db.minimap or { angle = 200 }
        db.minimap.hide = not db.minimap.hide
        if ns.Book and ns.Book.UpdateMinimapButton then ns.Book:UpdateMinimapButton() end
        Print(db.minimap.hide and "minimap button hidden." or "minimap button shown.")
    elseif cmd == "gamepad" then
        db.gamepad = not (db.gamepad ~= false)
        Print(db.gamepad ~= false and "controller navigation enabled (reopen the book)." or "controller navigation disabled.")
    elseif cmd == "debug" then
        if ns.Book and ns.Book.DebugReport then ns.Book:DebugReport(Print) else Print("the book file did not load (ns.Book is nil).") end
        if ns.Gamepad and ns.Gamepad.Report then ns.Gamepad:Report(Print)
            Print("lore: " .. (WhereIsIt_LoreData and ("loaded, " .. (WhereIsIt_LoreVersion or "?")) or "not loaded (opens with the book)")) else Print("gamepad module not loaded.") end
    elseif cmd == "config" or cmd == "options" then
        OpenOptions()
    elseif cmd == "" and ns.Book then
        ns.Book:Toggle()
    else
        Print("commands: /wii (open the book) | search <name or itemID> | toggle | lines 1-3 | faction auto/alliance/horde/both | unknown | althint | altclick | minimap | gamepad | find <itemID> | config")
    end
end

-- ---------------------------------------------------------------------------
-- Boot
-- ---------------------------------------------------------------------------
local loader = CreateFrame("Frame")
loader:RegisterEvent("ADDON_LOADED")
loader:RegisterEvent("PLAYER_LOGIN")
loader:SetScript("OnEvent", function(self, event, name)
    if event == "ADDON_LOADED" and name == ADDON then
        InitDB()
        InstallHooks()
        pcall(BuildOptionsPanel)
        self:UnregisterEvent("ADDON_LOADED")
    elseif event == "PLAYER_LOGIN" then
        if not db then InitDB(); InstallHooks() end
        if ns.Book and ns.Book.CreateMinimapButton then pcall(ns.Book.CreateMinimapButton, ns.Book) end
    end
end)
