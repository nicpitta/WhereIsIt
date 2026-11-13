-- Where Is It: controller navigation for the encyclopedia (WoW: Forever gamepad).
--
-- While the book is open an invisible catcher frame at the top strata receives
-- gamepad button presses. Buttons the book uses are consumed (so the game's own
-- controller cursor does not also react); everything else reaches the game.
-- Blizzard's controller frameworks (FrameControlsManager, SmartNavigation) are
-- never called: doing so from an addon taints the player's bindings.
--
--   D-pad / left stick   move the highlight          PAD1 (A / cross)    open the highlighted entry
--   PAD2 (B / circle)    close the book              PAD3 (X / square)   show the other faction
--   PAD4 (Y / triangle)  clear the search            LB / RB             previous / next consulted entry
--   LT / RT              previous / next page of search results
local ADDON, ns = ...
local Book = ns.Book
if not Book then return end

local GOLD = { 0.62, 0.42, 0.10 }
local REPEAT_DELAY, REPEAT_RATE = 0.35, 0.10
local REPEAT_KEYS = { PADDUP = true, PADDDOWN = true, PADDLEFT = true, PADDRIGHT = true }

local Pad = { lastKey = nil, presses = 0 }
ns.Gamepad = Pad

local function Plain(v)
    if type(issecretvalue) == "function" and issecretvalue(v) then return nil end
    return v
end

local function GamepadEnabled()
    if ns.db and ns.db.gamepad == false then return false end
    if InputUtil and InputUtil.IsGamepadUIEnabled then
        local ok, v = pcall(InputUtil.IsGamepadUIEnabled)
        if ok and Plain(v) then return true end
    end
    if C_GamePad and C_GamePad.IsEnabled then
        local ok, v = pcall(C_GamePad.IsEnabled)
        if ok and Plain(v) then return true end
    end
    return false
end

-- ---------------------------------------------------------------------------
-- Button glyphs: Blizzard's own input-prompt atlases, picked by the active
-- controller's label style, with letter fallbacks.
-- ---------------------------------------------------------------------------
local ATLAS = {
    xbox = { PAD1 = "gamepad-xbox1-buttona-normal", PAD2 = "gamepad-xbox1-buttonb-normal", PAD3 = "gamepad-xbox1-buttonx-normal",
             PAD4 = "gamepad-xbox1-buttony-normal", PADLSHOULDER = "gamepad-xbox1-trigger-lb-normal", PADRSHOULDER = "gamepad-xbox1-trigger-rb-normal",
             PADLTRIGGER = "gamepad-xbox1-trigger-lt-normal", PADRTRIGGER = "gamepad-xbox1-trigger-rt-normal", DPAD = "gamepad-xbox1-dpadall-normal" },
    ps = { PAD1 = "gamepad-ps-buttoncrox-normal", PAD2 = "gamepad-ps-buttoncircle-normal", PAD3 = "gamepad-ps-buttonsquare-normal",
           PAD4 = "gamepad-ps-buttontriangle-normal", PADLSHOULDER = "gamepad-ps-triggerl1-normal", PADRSHOULDER = "gamepad-ps-triggerr1-normal",
           PADLTRIGGER = "gamepad-ps-triggerl2-normal", PADRTRIGGER = "gamepad-ps-triggerr2-normal", DPAD = "gamepad-ps-dpadall-normal" },
    switch = { PAD1 = "gamepad-switch-128x-face-b-normal", PAD2 = "gamepad-switch-128x-face-a-normal", PAD3 = "gamepad-switch-128x-face-y-normal",
               PAD4 = "gamepad-switch-128x-face-x-normal", PADLSHOULDER = "gamepad-switch-128x-shoulder-l-normal", PADRSHOULDER = "gamepad-switch-128x-shoulder-r-normal",
               PADLTRIGGER = "gamepad-switch-128x-zl-normal", PADRTRIGGER = "gamepad-switch-128x-zr-normal", DPAD = "gamepad-switch-128x-dpad-all-normal" },
}
local TEXT = {
    xbox = { PAD1 = "A", PAD2 = "B", PAD3 = "X", PAD4 = "Y", PADLSHOULDER = "LB", PADRSHOULDER = "RB", PADLTRIGGER = "LT", PADRTRIGGER = "RT", DPAD = "+" },
    ps = { PAD1 = "X", PAD2 = "O", PAD3 = "[]", PAD4 = "^", PADLSHOULDER = "L1", PADRSHOULDER = "R1", PADLTRIGGER = "L2", PADRTRIGGER = "R2", DPAD = "+" },
    switch = { PAD1 = "B", PAD2 = "A", PAD3 = "Y", PAD4 = "X", PADLSHOULDER = "L", PADRSHOULDER = "R", PADLTRIGGER = "ZL", PADRTRIGGER = "ZR", DPAD = "+" },
}
local LABEL_STYLES = { Letters = "xbox", Generic = "xbox", Shapes = "ps", Reverse = "switch" }

local function Style()
    if C_GamePad and C_GamePad.GetActiveDeviceID and C_GamePad.GetDeviceMappedState then
        local ok, state = pcall(function() return C_GamePad.GetDeviceMappedState(C_GamePad.GetActiveDeviceID()) end)
        if ok and type(state) == "table" then
            return LABEL_STYLES[Plain(state.labelStyle) or ""] or "xbox"
        end
    end
    return "xbox"
end

local function Glyph(key, size)
    local style = Style()
    local atlas = ATLAS[style][key]
    size = size or 14
    if atlas and C_Texture and C_Texture.GetAtlasInfo and C_Texture.GetAtlasInfo(atlas) then
        return ("|A:%s:%d:%d|a"):format(atlas, size, size)
    end
    return "|cffe8c87a[" .. (TEXT[style][key] or key) .. "]|r"
end

-- ---------------------------------------------------------------------------
-- Focus model: which element the highlight sits on
-- ---------------------------------------------------------------------------
local highlight
local focus = { column = "index", row = 1 }

local function Frame()
    return Book:GetFrame()
end

local function EnsureHighlight()
    if highlight then return highlight end
    local f = Frame()
    highlight = CreateFrame("Frame", nil, f)
    highlight:SetFrameLevel((f:GetFrameLevel() or 1) + 10)
    for _, side in ipairs({ "TOP", "BOTTOM", "LEFT", "RIGHT" }) do
        local edge = highlight:CreateTexture(nil, "OVERLAY")
        edge:SetColorTexture(GOLD[1], GOLD[2], GOLD[3], 0.95)
        if side == "TOP" or side == "BOTTOM" then
            edge:SetPoint(side .. "LEFT"); edge:SetPoint(side .. "RIGHT"); edge:SetHeight(2)
        else
            edge:SetPoint("TOP" .. side); edge:SetPoint("BOTTOM" .. side); edge:SetWidth(2)
        end
    end
    local glow = highlight:CreateTexture(nil, "BACKGROUND")
    glow:SetColorTexture(GOLD[1], GOLD[2], GOLD[3], 0.10)
    glow:SetAllPoints()
    highlight:Hide()
    return highlight
end

local function VisibleRows()
    local f = Frame()
    local rows = {}
    for _, row in ipairs(f.results) do
        if row:IsShown() and row.itemID then rows[#rows + 1] = row end
    end
    return rows
end

-- the things the highlight can land on, per column
local function Targets(column)
    local f = Frame()
    if column == "index" then
        return VisibleRows()
    end
    -- the entry column: the page button and the faction ribbon
    local t = {}
    for _, k in ipairs({ "leafBtn", "factionBtn" }) do
        local b = f.L[k]
        if b and b:IsShown() then t[#t + 1] = b end
    end
    return t
end

local function Place()
    local f = Frame()
    if not f or not f:IsShown() or not GamepadEnabled() then
        if highlight then highlight:Hide() end
        return
    end
    local targets = Targets(focus.column)
    if #targets == 0 then
        local other = focus.column == "index" and "entry" or "index"
        targets = Targets(other)
        if #targets == 0 then
            if highlight then highlight:Hide() end
            return
        end
        focus.column = other
    end
    if focus.row > #targets then focus.row = #targets end
    if focus.row < 1 then focus.row = 1 end
    local target = targets[focus.row]
    local h = EnsureHighlight()
    h:ClearAllPoints()
    h:SetPoint("TOPLEFT", target, "TOPLEFT", -3, 3)
    h:SetPoint("BOTTOMRIGHT", target, "BOTTOMRIGHT", 3, -3)
    h:Show()
    focus.target = target
end

local function Move(dr)
    local targets = Targets(focus.column)
    if #targets == 0 then return Place() end
    local n = focus.row + dr
    if n < 1 then
        -- past the top of the results: previous page if there is one
        if focus.column == "index" and (Frame().resultOffset or 0) > 0 then
            Book:PageResults(-1)
            focus.row = #VisibleRows()
        else
            n = 1
            focus.row = n
        end
    elseif n > #targets then
        if focus.column == "index" and (Frame().resultOffset or 0) + #targets < (Frame().resultCount or 0) then
            Book:PageResults(1)
            focus.row = 1
        else
            focus.row = #targets
        end
    else
        focus.row = n
    end
    Place()
end

local function Switch()
    focus.column = focus.column == "index" and "entry" or "index"
    focus.row = 1
    Place()
end

local function Activate()
    local target = focus.target
    if not target then return end
    if target.itemID then
        Book:Show(target.itemID)
        focus.column = "index"
    elseif target:GetScript("OnClick") then
        target:GetScript("OnClick")(target)
    end
    Place()
end

local HANDLERS = {
    PADDUP = function() Move(-1) end,
    PADDDOWN = function() Move(1) end,
    PADDLEFT = Switch,
    PADDRIGHT = Switch,
    PAD1 = Activate,
    PAD2 = function() local f = Frame(); if f then f:Hide() end end,
    PAD3 = function() Book:ToggleFaction(); Place() end,
    PAD4 = function() local f = Frame(); if f then f.search:SetText(""); f.search:ClearFocus(); Book:UpdateIndex(); focus.row = 1; Place() end end,
    PADLSHOULDER = function() Book:HistoryStep(1) end,   -- older
    PADRSHOULDER = function() Book:HistoryStep(-1) end,  -- newer
    PADLTRIGGER = function() Book:PageResults(-1); focus.row = 1; Place() end,
    PADRTRIGGER = function() Book:PageResults(1); focus.row = 1; Place() end,
}

-- ---------------------------------------------------------------------------
-- Input capture
-- ---------------------------------------------------------------------------
local catcher = CreateFrame("Frame", nil, UIParent)
catcher:SetFrameStrata("TOOLTIP")
catcher:SetFrameLevel(9000)
catcher:SetSize(1, 1)
catcher:SetPoint("TOPLEFT")
catcher:Hide()

local pressed, held = {}, {}

local function SetPropagate(flag)
    if InCombatLockdown and InCombatLockdown() then return end
    if catcher.SetPropagateKeyboardInput then pcall(catcher.SetPropagateKeyboardInput, catcher, flag) end
end

local function Handle(key)
    Pad.lastKey = key
    Pad.presses = Pad.presses + 1
    local h = HANDLERS[key]
    if h then pcall(h) end
end

catcher:SetScript("OnGamePadButtonDown", function(_, key)
    key = Plain(key)
    local handled = HANDLERS[key] ~= nil and Frame() and Frame():IsShown()
    SetPropagate(not handled)
    if handled and not pressed[key] then
        pressed[key] = true
        held[key] = REPEAT_KEYS[key] and -REPEAT_DELAY or nil
        Handle(key)
    end
end)
catcher:SetScript("OnGamePadButtonUp", function(_, key)
    key = Plain(key)
    local handled = pressed[key] ~= nil
    pressed[key] = nil
    held[key] = nil
    SetPropagate(not handled)
end)

-- left stick as a D-pad: a push past the dead zone counts once, until it returns
local stickDir
catcher:SetScript("OnGamePadStick", function(_, stick, x, y, len)
    stick, x, y, len = Plain(stick), Plain(x), Plain(y), Plain(len)
    if stick ~= "Left" or type(len) ~= "number" then return end
    if len < 0.45 then stickDir = nil; held.STICK = nil; return end
    local dir
    if math.abs(y) >= math.abs(x) then dir = y > 0 and "PADDUP" or "PADDDOWN" else dir = x > 0 and "PADDRIGHT" or "PADDLEFT" end
    if dir ~= stickDir then
        stickDir = dir
        held.STICK = -REPEAT_DELAY
        Handle(dir)
    end
end)

catcher:SetScript("OnUpdate", function(_, elapsed)
    for key, t in pairs(held) do
        t = t + elapsed
        if t >= REPEAT_RATE then
            t = 0
            Handle(key == "STICK" and stickDir or key)
        end
        held[key] = t
    end
end)

local function Start()
    if not GamepadEnabled() then return end
    if InCombatLockdown and InCombatLockdown() then return end
    wipe(pressed); wipe(held); stickDir = nil
    catcher:Show()
    if catcher.EnableGamePadButton then pcall(catcher.EnableGamePadButton, catcher, true) end
    if catcher.EnableGamePadStick and not (ns.db and ns.db.gamepadStick == false) then pcall(catcher.EnableGamePadStick, catcher, true) end
    SetPropagate(true)
    focus.column, focus.row = "index", 1
    Place()
    Pad.active = true
end

local function Stop()
    if catcher.EnableGamePadButton and not (InCombatLockdown and InCombatLockdown()) then
        pcall(catcher.EnableGamePadButton, catcher, false)
        if catcher.EnableGamePadStick then pcall(catcher.EnableGamePadStick, catcher, false) end
    end
    SetPropagate(true)
    catcher:Hide()
    if highlight then highlight:Hide() end
    Pad.active = false
end

-- ---------------------------------------------------------------------------
-- Legend beneath the book (bottom-right tab)
-- ---------------------------------------------------------------------------
local function Legend()
    if not GamepadEnabled() then
        Book:SetLegend("")
        return
    end
    local parts = {
        Glyph("DPAD") .. " move",
        Glyph("PAD1") .. " open",
        Glyph("PAD2") .. " close",
        Glyph("PAD3") .. " faction",
        Glyph("PAD4") .. " clear search",
        Glyph("PADLSHOULDER") .. Glyph("PADRSHOULDER") .. " history",
        Glyph("PADLTRIGGER") .. Glyph("PADRTRIGGER") .. " more results",
    }
    Book:SetLegend(table.concat(parts, "   "))
end

-- ---------------------------------------------------------------------------
-- Wiring
-- ---------------------------------------------------------------------------
local wired = false
local function Wire()
    if wired then return end
    local f = Frame()
    if not f then return end
    wired = true
    f:HookScript("OnShow", function() Start(); Legend() end)
    f:HookScript("OnHide", Stop)
    -- the highlight follows re-rendered content
    hooksecurefunc(Book, "UpdateIndex", function() if Pad.active then Place() end end)
    hooksecurefunc(Book, "Render", function() if Pad.active then Place() end end)
    if f:IsShown() then Start(); Legend() end
end

-- the book frame is built lazily, so wire up when it first opens
hooksecurefunc(Book, "Open", Wire)
hooksecurefunc(Book, "Show", Wire)

local events = CreateFrame("Frame")
for _, e in ipairs({ "PLAYER_REGEN_DISABLED", "GAME_PAD_ACTIVE_CHANGED", "GAME_PAD_CONNECTED", "GAME_PAD_DISCONNECTED" }) do
    pcall(events.RegisterEvent, events, e)
end
events:SetScript("OnEvent", function(_, event)
    local f = Frame()
    if event == "PLAYER_REGEN_DISABLED" then
        -- input capture cannot change during combat: hand everything back first
        if f and f:IsShown() then f:Hide() end
    elseif f and f:IsShown() then
        Stop(); Start(); Legend()
    end
end)

function Pad:Report(print)
    print("gamepad: " .. (GamepadEnabled() and "enabled" or "not enabled") .. "; capturing: " .. tostring(self.active) ..
        "; presses seen: " .. self.presses .. "; last: " .. tostring(self.lastKey) .. "; style: " .. Style())
end
