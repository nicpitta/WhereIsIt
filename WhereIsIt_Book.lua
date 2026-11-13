-- Where Is It: the encyclopedia. A two-page book: the left page is the item's
-- entry (icon, kind, flavour text, provenance, uses), the right page an atlas
-- sketch of the region it is most plentiful in plus the index (search).
-- Opened with /wii, /wii search <text>, or Alt-clicking an item or item link.
local ADDON, ns = ...

local MEDIA = "Interface\\AddOns\\" .. ADDON .. "\\Media\\"
local INK = { 0.23, 0.16, 0.10 }
local FADED = { 0.42, 0.34, 0.25 }
local RED = { 0.55, 0.18, 0.12 }
local GOLD = { 0.48, 0.31, 0.07 }
local GILT = { 0.95, 0.80, 0.42 }           -- lettering on illuminated initials
local BOOK_W, BOOK_H = 960, 640
local PAD = 38
local PAGE_W = (BOOK_W - 48) / 2 - 3 - PAD * 2
local FACTION_COLOR = { A = { 0.18, 0.34, 0.62 }, H = { 0.66, 0.16, 0.14 } }

local Book = {}
ns.Book = Book

local function Plain(v)
    if type(issecretvalue) == "function" and issecretvalue(v) then return nil end
    return v
end

-- ---------------------------------------------------------------------------
-- Drawing helpers
-- ---------------------------------------------------------------------------
local fonts
local function Fonts()
    if not fonts then
        local function from(name, fallback)
            local obj = _G[name]
            if obj and obj.GetFont then
                local path = obj:GetFont()
                if path then return path end
            end
            return fallback
        end
        fonts = {
            heading = from("QuestTitleFont", "Fonts\\MORPHEUS.TTF"),
            body = from("GameFontNormal", "Fonts\\FRIZQT__.TTF"),
        }
    end
    return fonts
end

local function Tex(parent, file, layer, color, sub)
    local t = parent:CreateTexture(nil, layer or "ARTWORK", nil, sub)
    t:SetTexture(MEDIA .. file)
    if color then t:SetVertexColor(color[1], color[2], color[3], color[4] or 1) end
    return t
end

local function Fill(parent, color, layer)
    local t = parent:CreateTexture(nil, layer or "BACKGROUND")
    t:SetColorTexture(color[1], color[2], color[3], color[4] or 1)
    return t
end

local function Txt(parent, style, size, color, layer)
    local fs = parent:CreateFontString(nil, layer or "OVERLAY", "GameFontNormal")
    local f = Fonts()
    fs:SetFont(style == "heading" and f.heading or f.body, size or 13, "")
    if fs.SetShadowColor then fs:SetShadowColor(0, 0, 0, 0) end
    color = color or INK
    fs:SetTextColor(color[1], color[2], color[3], color[4] or 1)
    fs:SetJustifyH("LEFT")
    fs:SetJustifyV("TOP")
    return fs
end

local function Outline(parent, color, thickness, layer)
    thickness = thickness or 1
    for _, side in ipairs({ "TOP", "BOTTOM", "LEFT", "RIGHT" }) do
        local edge = Fill(parent, color, layer or "BORDER")
        if side == "TOP" or side == "BOTTOM" then
            edge:SetPoint(side .. "LEFT")
            edge:SetPoint(side .. "RIGHT")
            edge:SetHeight(thickness)
        else
            edge:SetPoint("TOP" .. side)
            edge:SetPoint("BOTTOM" .. side)
            edge:SetWidth(thickness)
        end
    end
end

local function Ribbon(parent, text, color, onClick, icon)
    local b = CreateFrame("Button", nil, parent)
    b:SetSize(66, 100)
    b.shadow = Tex(b, "RibbonShadow", "BACKGROUND")
    b.shadow:SetPoint("TOPLEFT", 3, -4)
    b.shadow:SetPoint("BOTTOMRIGHT", 3, -4)
    b.shadow:SetTexCoord(0, 1, 0, 112 / 128)
    b.cloth = Tex(b, "Ribbon", "ARTWORK", color)
    b.cloth:SetAllPoints()
    b.cloth:SetTexCoord(0, 1, 0, 112 / 128)
    b.label = Txt(b, "body", 11, { 1, 0.95, 0.85 })
    b.label:SetPoint("TOP", 0, -26)
    b.label:SetJustifyH("CENTER")
    b.label:SetText(text)
    if icon then
        b.icon = Tex(b, icon, "OVERLAY", { 1, 0.95, 0.85 })
        b.icon:SetSize(22, 22)
        b.icon:SetPoint("TOP", 0, -46)
    end
    b:SetScript("OnEnter", function(self) self.cloth:SetVertexColor(math.min(1, color[1] * 1.25), math.min(1, color[2] * 1.25), math.min(1, color[3] * 1.25)) end)
    b:SetScript("OnLeave", function(self) self.cloth:SetVertexColor(color[1], color[2], color[3]) end)
    b:SetScript("OnClick", onClick)
    return b
end

-- a strip of pale parchment behind a section heading
local function ScrollTex(parent, w, h)
    local t = Tex(parent, "Scroll", "ARTWORK")
    t:SetTexCoord(0, 1, 8 / 64, 56 / 64)
    t:SetSize(w, h)
    return t
end

-- an illuminated initial: a tinted field, a gilt frame and a big gold letter
local function DropCap(parent, size, fontSize)
    local f = CreateFrame("Frame", nil, parent)
    f:SetSize(size, size)
    f.field = Tex(f, "DropCapField", "ARTWORK")
    f.field:SetAllPoints()
    f.frame = Tex(f, "DropCapFrame", "OVERLAY")
    f.frame:SetAllPoints()
    f.letter = Txt(f, "heading", fontSize, GILT, "OVERLAY")
    f.letter:SetPoint("CENTER", 0, -1)
    f.letter:SetJustifyH("CENTER")
    if f.letter.SetShadowColor then
        f.letter:SetShadowColor(0, 0, 0, 0.6)
        f.letter:SetShadowOffset(1, -1)
    end
    function f:SetFaction(fac)
        local c = FACTION_COLOR[fac] or FACTION_COLOR.A
        self.field:SetVertexColor(c[1], c[2], c[3])
    end
    return f
end

-- ---------------------------------------------------------------------------
-- Item information (names/icons from the client, hints from our data)
-- ---------------------------------------------------------------------------
local function ItemInfo(itemID)
    local getInfo = (C_Item and C_Item.GetItemInfo) or GetItemInfo
    local name, link, quality, ilvl, reqLevel, class, subclass, _, equipLoc, icon
    if getInfo then
        local ok, a, b, c, d, e, f, g, h, i, j = pcall(getInfo, itemID)
        if ok then
            name, link, quality, ilvl, reqLevel, class, subclass, equipLoc, icon = Plain(a), Plain(b), Plain(c), Plain(d), Plain(e), Plain(f), Plain(g), Plain(i), Plain(j)
        end
    end
    if not icon then
        if C_Item and C_Item.GetItemIconByID then
            local ok, v = pcall(C_Item.GetItemIconByID, itemID)
            icon = ok and Plain(v) or nil
        elseif GetItemInfoInstant then
            local ok, _, _, _, _, v = pcall(GetItemInfoInstant, itemID)
            icon = ok and Plain(v) or nil
        end
    end
    return {
        name = name or (ns.Names and ns.Names[itemID]) or ("Item " .. itemID),
        link = link, quality = quality, ilvl = ilvl, reqLevel = reqLevel,
        class = class, subclass = subclass, equipLoc = equipLoc,
        icon = icon or "Interface\\Icons\\INV_Misc_QuestionMark",
        pending = (name == nil),
    }
end

local QUALITY_WORD = { [0] = "Poor", "Common", "Uncommon", "Rare", "Epic", "Legendary", "Artifact" }

local function QualityColor(q)
    -- poor and common items are written in plain ink; white would vanish on parchment
    if q and q >= 2 and ITEM_QUALITY_COLORS and ITEM_QUALITY_COLORS[q] then
        local c = ITEM_QUALITY_COLORS[q]
        -- ink-ify: blend towards ink so it reads on parchment
        return c.r * 0.7 + INK[1] * 0.3, c.g * 0.7 + INK[2] * 0.3, c.b * 0.7 + INK[3] * 0.3
    end
    return INK[1], INK[2], INK[3]
end

local function FactionKey()
    local setting = ns.db and ns.db.faction or "auto"
    if setting == "alliance" then return "A" end
    if setting == "horde" then return "H" end
    if type(UnitFactionGroup) == "function" then
        local ok, fac = pcall(UnitFactionGroup, "player")
        if ok and Plain(fac) == "Horde" then return "H" end
    end
    return "A"
end

-- the faction emblem, from whichever of the client's own textures exists
local CREST = {
    A = { atlases = { "AllianceEmblem", "UI-HUD-UnitFrame-Player-PVP-AllianceIcon" }, file = "Interface\\TargetingFrame\\UI-PVP-Alliance" },
    H = { atlases = { "HordeEmblem", "UI-HUD-UnitFrame-Player-PVP-HordeIcon" }, file = "Interface\\TargetingFrame\\UI-PVP-Horde" },
}
local function SetCrest(t, fac)
    local c = CREST[fac] or CREST.A
    if C_Texture and C_Texture.GetAtlasInfo and t.SetAtlas then
        for _, atlas in ipairs(c.atlases) do
            local ok, info = pcall(C_Texture.GetAtlasInfo, atlas)
            if ok and info then
                t:SetAtlas(atlas)
                t:SetTexCoord(0, 1, 0, 1)
                return
            end
        end
    end
    t:SetTexture(c.file)
    t:SetTexCoord(0, 0.6, 0, 0.6)
end

-- ---------------------------------------------------------------------------
-- Map art: find the uiMapID whose name matches a zone and draw its tiles
-- ---------------------------------------------------------------------------
local mapIndex
local function Norm(s)
    if type(s) ~= "string" then return nil end
    return (s:lower():gsub("[^%w\128-\255]", ""))
end

local function HasArt(id)
    local ok, layers = pcall(C_Map.GetMapArtLayers, id)
    if not ok or type(layers) ~= "table" or not layers[1] then return false end
    local ok2, tex = pcall(C_Map.GetMapArtLayerTextures, id, 1)
    return ok2 and type(tex) == "table" and #tex > 0
end

local function BuildMapIndex()
    mapIndex = {}
    if not (C_Map and C_Map.GetMapInfo and C_Map.GetMapArtLayers) then return end
    for id = 1, 2500 do
        local ok, info = pcall(C_Map.GetMapInfo, id)
        if ok and type(info) == "table" and info.name then
            local key = Norm(Plain(info.name))
            if key then
                mapIndex[key] = mapIndex[key] or {}
                table.insert(mapIndex[key], { id = id, mapType = Plain(info.mapType) or 99 })
            end
        end
    end
end

local mapCache = {}
local function FindMapID(zoneName)
    if not zoneName then return nil end
    if mapCache[zoneName] ~= nil then return mapCache[zoneName] or nil end
    if not mapIndex then BuildMapIndex() end
    local list = mapIndex[Norm(zoneName) or ""] or {}
    -- prefer Zone (3), then Dungeon (4), then anything with art
    table.sort(list, function(a, b)
        local pa = (a.mapType == 3 and 0) or (a.mapType == 4 and 1) or 2
        local pb = (b.mapType == 3 and 0) or (b.mapType == 4 and 1) or 2
        if pa ~= pb then return pa < pb end
        return a.id < b.id
    end)
    local found = false
    for _, e in ipairs(list) do
        if HasArt(e.id) then found = e.id; break end
    end
    mapCache[zoneName] = found
    return found or nil
end

local function DrawMap(holder, mapID)
    holder.tiles = holder.tiles or {}
    for _, t in ipairs(holder.tiles) do t:Hide() end
    if not mapID then return false end
    local ok, layers = pcall(C_Map.GetMapArtLayers, mapID)
    if not ok or not layers or not layers[1] then return false end
    local ok2, textures = pcall(C_Map.GetMapArtLayerTextures, mapID, 1)
    if not ok2 or not textures or #textures == 0 then return false end
    local layer = layers[1]
    local layerW = tonumber(layer.layerWidth) or 1002
    local layerH = tonumber(layer.layerHeight) or 668
    local tileW = tonumber(layer.tileWidth) or 256
    local tileH = tonumber(layer.tileHeight) or 256
    local cols = math.max(1, math.ceil(layerW / tileW))
    local artW, artH = holder:GetWidth() or 1, holder:GetHeight() or 1
    local sx, sy = artW / layerW, artH / layerH
    for i = 1, #textures do
        local t = holder.tiles[i]
        if not t then
            t = holder:CreateTexture(nil, "ARTWORK")
            holder.tiles[i] = t
        end
        local col, row = (i - 1) % cols, math.floor((i - 1) / cols)
        t:ClearAllPoints()
        t:SetSize(tileW * sx, tileH * sy)
        t:SetPoint("TOPLEFT", holder, "TOPLEFT", col * tileW * sx, -row * tileH * sy)
        t:SetTexture(textures[i])
        t:SetTexCoord(0, 1, 0, 1)
        -- an ink-and-wash look so the map sits on the parchment
        if t.SetDesaturated then t:SetDesaturated(true) end
        t:SetVertexColor(0.72, 0.68, 0.48)
        t:Show()
    end
    return true
end

-- ---------------------------------------------------------------------------
-- The book
-- ---------------------------------------------------------------------------
local frame

local function Flow(page)
    -- simple top-down layout cursor for a page
    local cursor = { y = -PAD, page = page }
    function cursor:place(region, height, gap, x)
        region:ClearAllPoints()
        region:SetPoint("TOPLEFT", page, "TOPLEFT", x or PAD, self.y)
        self.y = self.y - (height or region:GetHeight()) - (gap or 6)
    end
    function cursor:text(fs, gap)
        local h = fs:GetStringHeight()
        if (not h or h == 0) and fs:GetText() and fs:GetText() ~= "" then h = 14 end
        self:place(fs, h or 0, gap)
    end
    return cursor
end

local function BuildBook()
    frame = CreateFrame("Frame", "WhereIsItBook", UIParent)
    frame:SetSize(BOOK_W, BOOK_H)
    frame:SetPoint("CENTER", 0, 20)
    frame:SetFrameStrata("HIGH")
    frame:SetToplevel(true)
    frame:SetMovable(true)
    frame:EnableMouse(true)
    frame:RegisterForDrag("LeftButton")
    frame:SetScript("OnDragStart", function(self) self:StartMoving() end)
    frame:SetScript("OnDragStop", function(self) self:StopMovingOrSizing() end)
    frame:SetClampedToScreen(true)
    frame:Hide()
    if UISpecialFrames then table.insert(UISpecialFrames, "WhereIsItBook") end
    local base = frame:GetFrameLevel() or 1

    -- leather cover
    local leather = frame:CreateTexture(nil, "BACKGROUND")
    leather:SetTexture(MEDIA .. "Leather", "REPEAT", "REPEAT")
    if leather.SetHorizTile then leather:SetHorizTile(true); leather:SetVertTile(true) end
    leather:SetAllPoints()
    local edgeDark = Fill(frame, { 0, 0, 0, 0.35 }, "BORDER")
    edgeDark:SetPoint("TOPLEFT"); edgeDark:SetPoint("BOTTOMRIGHT")
    edgeDark:SetAlpha(0)
    -- darker, worn rim of the cover and a stitched thread just inside it
    local rim = CreateFrame("Frame", nil, frame)
    rim:SetAllPoints()
    Outline(rim, { 0.05, 0.02, 0.01, 0.8 }, 2, "BORDER")
    local function StitchLine(file, p1, p2, horiz)
        local t = frame:CreateTexture(nil, "BORDER", nil, 1)
        t:SetTexture(MEDIA .. file, "REPEAT", "REPEAT")
        if horiz then
            if t.SetHorizTile then t:SetHorizTile(true) end
            t:SetHeight(8)
        else
            if t.SetVertTile then t:SetVertTile(true) end
            t:SetWidth(8)
        end
        t:SetPoint(p1[1], p1[2], p1[3])
        t:SetPoint(p2[1], p2[2], p2[3])
        t:SetAlpha(0.75)
    end
    StitchLine("Stitch", { "TOPLEFT", 10, -8 }, { "TOPRIGHT", -10, -8 }, true)
    StitchLine("Stitch", { "BOTTOMLEFT", 10, 8 }, { "BOTTOMRIGHT", -10, 8 }, true)
    StitchLine("StitchV", { "TOPLEFT", 8, -10 }, { "BOTTOMLEFT", 8, 10 }, false)
    StitchLine("StitchV", { "TOPRIGHT", -8, -10 }, { "BOTTOMRIGHT", -8, 10 }, false)

    -- metal corner guards
    for _, c in ipairs({ { "TOPLEFT", 0, 1, 0, 1 }, { "TOPRIGHT", 1, 0, 0, 1 }, { "BOTTOMLEFT", 0, 1, 1, 0 }, { "BOTTOMRIGHT", 1, 0, 1, 0 } }) do
        local t = Tex(frame, "Corner", "OVERLAY")
        t:SetSize(72, 72)
        t:SetPoint(c[1], 1 * (c[1]:find("LEFT") and 1 or -1), 1 * (c[1]:find("TOP") and -1 or 1))
        t:SetTexCoord(c[2], c[3], c[4], c[5])
    end

    -- pages
    local function Page(side)
        local p = CreateFrame("Frame", nil, frame)
        p:SetFrameLevel(base + 2)
        local paper = Tex(p, "Page", "BACKGROUND")
        paper:SetAllPoints()
        if side == "right" then paper:SetTexCoord(1, 0, 0, 1) end
        -- soft shadow towards the spine
        local shade = Fill(p, { 0.2, 0.12, 0.05, 0.10 }, "BORDER")
        shade:SetWidth(40)
        if side == "left" then
            shade:SetPoint("TOPRIGHT"); shade:SetPoint("BOTTOMRIGHT")
            if shade.SetGradient and CreateColor then
                shade:SetGradient("HORIZONTAL", CreateColor(0.2, 0.12, 0.05, 0), CreateColor(0.2, 0.12, 0.05, 0.30))
            end
        else
            shade:SetPoint("TOPLEFT"); shade:SetPoint("BOTTOMLEFT")
            if shade.SetGradient and CreateColor then
                shade:SetGradient("HORIZONTAL", CreateColor(0.2, 0.12, 0.05, 0.30), CreateColor(0.2, 0.12, 0.05, 0))
            end
        end
        -- inked vines curling out of the two outer corners
        local corners = side == "left"
            and { { "TOPLEFT", 0, 1, 0, 1 }, { "BOTTOMLEFT", 0, 1, 1, 0 } }
            or { { "TOPRIGHT", 1, 0, 0, 1 }, { "BOTTOMRIGHT", 1, 0, 1, 0 } }
        for _, c in ipairs(corners) do
            local v = Tex(p, "Vine", "BACKGROUND", { FADED[1], FADED[2], FADED[3], 0.6 }, 2)
            v:SetSize(130, 130)
            v:SetPoint(c[1], c[1]:find("LEFT") and 10 or -10, c[1]:find("TOP") and -10 or 10)
            v:SetTexCoord(c[2], c[3], c[4], c[5])
        end
        return p
    end
    local left = Page("left")
    left:SetPoint("TOPLEFT", 26, -26)
    left:SetPoint("BOTTOMRIGHT", frame, "BOTTOM", -3, 26)
    local right = Page("right")
    right:SetPoint("TOPLEFT", frame, "TOP", 3, -26)
    right:SetPoint("BOTTOMRIGHT", -26, 26)
    frame.left, frame.right = left, right

    -- the fore-edge: a few offset sheets peeking out beneath each page
    local function PageStack(page, dir)
        local shades = { { 0.80, 0.70, 0.52, 0.95 }, { 0.72, 0.62, 0.45, 0.9 }, { 0.62, 0.52, 0.37, 0.85 } }
        for i, col in ipairs(shades) do
            local sheet = Fill(frame, col, "BORDER")
            sheet:SetPoint("TOPLEFT", page, "TOPLEFT", dir < 0 and -2 * i or 0, -2 * i)
            sheet:SetPoint("BOTTOMRIGHT", page, "BOTTOMRIGHT", dir > 0 and 2 * i or 0, -2 * i)
        end
    end
    PageStack(left, -1)
    PageStack(right, 1)
    local pageW = PAGE_W

    -- spine: a dark gutter with a worn thread down the middle
    local spine = Fill(frame, { 0.07, 0.035, 0.015, 0.95 }, "ARTWORK")
    spine:SetWidth(10)
    spine:SetPoint("TOP", 0, -26); spine:SetPoint("BOTTOM", 0, 26)
    -- fittings that lie over the pages: cord lacing the spine
    local fittings = CreateFrame("Frame", nil, frame)
    fittings:SetAllPoints()
    fittings:SetFrameLevel(base + 3)
    local lace = fittings:CreateTexture(nil, "ARTWORK")
    lace:SetTexture(MEDIA .. "Lace", "REPEAT", "REPEAT")
    if lace.SetVertTile then lace:SetVertTile(true) end
    lace:SetWidth(26)
    lace:SetPoint("TOP", 0, -36); lace:SetPoint("BOTTOM", 0, 36)
    lace:SetAlpha(0.9)

    -- page numbers; the left page turns, so its number changes with the leaf
    frame.pageNum = {}
    for i, p in ipairs({ left, right }) do
        local n = Txt(p, "body", 11, FADED)
        n:SetPoint("BOTTOM", 0, 14)
        n:SetJustifyH("CENTER")
        n:SetText("~ " .. (i == 1 and 1 or 3) .. " ~")
        frame.pageNum[i] = n
    end
    -- one page button, centred above the left page's number, turns its leaf:
    -- "Next Page" with the arrow after it, or "Previous Page" with the arrow before
    local leafBtn = CreateFrame("Button", nil, left)
    leafBtn:SetSize(140, 22)
    leafBtn:SetPoint("BOTTOM", left, "BOTTOM", 0, 32)
    leafBtn.label = Txt(leafBtn, "body", 12, FADED)
    leafBtn.label:SetJustifyV("MIDDLE")
    leafBtn.glyph = Tex(leafBtn, "Arrow", "OVERLAY", FADED)
    leafBtn.glyph:SetSize(18, 18)
    function leafBtn:SetDirection(dir)
        self.dir = dir
        self.label:SetText(dir > 0 and "Next Page" or "Previous Page")
        self.label:ClearAllPoints()
        self.glyph:ClearAllPoints()
        local w = (self.label:GetStringWidth() or 70) + 24
        self:SetWidth(w)
        if dir > 0 then
            self.glyph:SetTexCoord(0, 1, 0, 1)
            self.label:SetPoint("LEFT", self, "LEFT", 0, 0)
            self.glyph:SetPoint("LEFT", self.label, "RIGHT", 6, 0)
        else
            self.glyph:SetTexCoord(1, 0, 0, 1)
            self.glyph:SetPoint("LEFT", self, "LEFT", 0, 0)
            self.label:SetPoint("LEFT", self.glyph, "RIGHT", 6, 0)
        end
    end
    leafBtn:SetScript("OnClick", function(self) Book:TurnLeaf(self.dir or 1) end)
    leafBtn:SetScript("OnEnter", function(self)
        self.glyph:SetVertexColor(INK[1], INK[2], INK[3])
        self.label:SetTextColor(INK[1], INK[2], INK[3])
    end)
    leafBtn:SetScript("OnLeave", function(self)
        self.glyph:SetVertexColor(FADED[1], FADED[2], FADED[3])
        self.label:SetTextColor(FADED[1], FADED[2], FADED[3])
    end)
    leafBtn:Hide()
    frame.leafBtn = leafBtn
    left:EnableMouseWheel(true)
    left:SetScript("OnMouseWheel", function(_, delta) Book:TurnLeaf(delta > 0 and -1 or 1) end)

    -- compass watermark
    local compass = Tex(left, "Compass", "BACKGROUND", { FADED[1], FADED[2], FADED[3], 0.14 }, 1)
    compass:SetSize(210, 210)
    compass:SetPoint("BOTTOMRIGHT", -30, 30)

    -- close button
    local close = CreateFrame("Button", nil, frame)
    close:SetSize(32, 32)
    close:SetPoint("TOPRIGHT", -14, -14)
    close:SetFrameLevel(base + 6)
    close.disc = Tex(close, "Brass", "ARTWORK")
    close.disc:SetAllPoints()
    close.glyph = Tex(close, "Cross", "OVERLAY", { 0.25, 0.15, 0.05 })
    close.glyph:SetSize(18, 18)
    close.glyph:SetPoint("CENTER")
    close:SetScript("OnClick", function() frame:Hide() end)
    close:SetScript("OnEnter", function(self) self.disc:SetVertexColor(1.15, 1.15, 1.1) end)
    close:SetScript("OnLeave", function(self) self.disc:SetVertexColor(1, 1, 1) end)

    -- the settings ribbon, hanging over the top of the right page
    local settings = Ribbon(frame, "Settings", { 0.78, 0.58, 0.16 }, function() if ns.OpenOptions then ns.OpenOptions() end end, "Gear")
    settings:SetPoint("TOP", frame, "TOPRIGHT", -112, 10)
    settings:SetFrameLevel(base + 6)
    frame.settingsRibbon = settings

    -- ======================= LEFT PAGE: the entry =======================
    local L = {}
    frame.L = L
    -- the faction's crest in sepia above the title banner; both always shown
    L.crest = left:CreateTexture(nil, "ARTWORK")
    L.crest:SetSize(56, 56)
    L.crest:SetPoint("TOP", left, "TOP", 0, -PAD + 8)
    if L.crest.SetDesaturated then L.crest:SetDesaturated(true) end
    L.crest:SetVertexColor(0.45, 0.33, 0.18, 0.55)
    L.kickerScroll = ScrollTex(left, 240, 40)
    L.kickerScroll:SetPoint("TOP", left, "TOP", 0, -PAD - 44)
    L.kicker = Txt(left, "heading", 15, RED)
    L.kicker:SetPoint("CENTER", L.kickerScroll, "CENTER", 0, 1)
    L.kicker:SetJustifyH("CENTER")
    L.kicker:SetText("Encyclopaedia Azerothica")
    L.iconFrame = CreateFrame("Frame", nil, left)
    L.iconFrame:SetSize(54, 54)
    L.iconGilt = Tex(L.iconFrame, "DropCapFrame", "OVERLAY")
    L.iconGilt:SetAllPoints()
    L.icon = L.iconFrame:CreateTexture(nil, "ARTWORK")
    L.icon:SetPoint("TOPLEFT", 5, -5); L.icon:SetPoint("BOTTOMRIGHT", -5, 5)
    L.icon:SetTexCoord(0.07, 0.93, 0.07, 0.93)
    L.title = Txt(left, "heading", 26, INK)
    L.title:SetWidth(pageW - 66)
    L.title:SetWordWrap(true)
    L.subtitle = Txt(left, "body", 12, FADED)
    L.subtitle:SetWidth(pageW - 66)
    L.subtitle:SetWordWrap(true)
    L.divider = Tex(left, "Flourish", "ARTWORK", FADED)
    L.divider:SetSize(300, 38)
    L.flavour = Txt(left, "body", 13, FADED)
    L.flavour:SetWidth(pageW)
    L.flavour:SetWordWrap(true)
    L.provScroll = ScrollTex(left, 180, 38)
    L.provHead = Txt(left, "heading", 18, RED)
    L.provHead:SetPoint("LEFT", L.provScroll, "LEFT", 24, 1)
    L.provHead:SetText("Provenance")
    L.rows = {}
    for i = 1, 6 do
        local row = {}
        row.bullet = Tex(left, "Diamond", "ARTWORK", GOLD)
        row.bullet:SetSize(9, 9)
        row.text = Txt(left, "body", 13, INK)
        row.text:SetWidth(pageW - 18)
        row.text:SetWordWrap(true)
        L.rows[i] = row
    end
    L.usesScroll = ScrollTex(left, 160, 38)
    L.usesHead = Txt(left, "heading", 18, RED)
    L.usesHead:SetPoint("LEFT", L.usesScroll, "LEFT", 24, 1)
    L.usesHead:SetText("Of use to")
    L.drop = DropCap(left, 42, 28)
    L.uses = Txt(left, "body", 13, INK)
    L.uses:SetWidth(pageW)
    L.uses:SetWordWrap(true)
    -- the account: the encyclopedia's full write-up, set after the entry or overleaf
    L.accountScroll = ScrollTex(left, 170, 38)
    L.accountHead = Txt(left, "heading", 18, RED)
    L.accountHead:SetPoint("LEFT", L.accountScroll, "LEFT", 24, 1)
    L.accountHead:SetText("The account")
    L.accountDrop = DropCap(left, 42, 28)
    L.account = {}
    for i = 1, 3 do
        local fs = Txt(left, "body", 12, INK)
        fs:SetWidth(pageW)
        fs:SetWordWrap(true)
        L.account[i] = fs
    end
    L.leafBtn = frame.leafBtn
    L.factionNote = Txt(left, "body", 11, FADED)
    L.factionNote:SetPoint("BOTTOMLEFT", left, "BOTTOMLEFT", PAD, 14)
    L.empty = Txt(left, "body", 13, FADED)
    L.empty:SetWidth(pageW)
    L.empty:SetWordWrap(true)
    L.empty:SetPoint("TOPLEFT", left, "TOPLEFT", PAD, -PAD - 110)
    L.empty:SetText("Alt-click an item in your bags or a link in chat, or search the index on the facing page, and its entry will be written up here.")

    -- the faction ribbon: a bookmark hanging out from between the pages beneath
    -- the left page, bearing the crest of the other faction: click it to read
    -- the entry as recorded for them.
    local fr = CreateFrame("Button", nil, frame)
    fr:SetSize(60, 96)
    fr:SetFrameLevel(base + 1)                -- behind the pages, over the cover
    fr:SetPoint("TOP", frame, "BOTTOM", -150, 46)
    fr.shadow = Tex(fr, "RibbonShadow", "BACKGROUND")
    fr.shadow:SetPoint("TOPLEFT", 3, -4)
    fr.shadow:SetPoint("BOTTOMRIGHT", 3, -4)
    fr.shadow:SetTexCoord(0, 1, 0, 112 / 128)
    fr.cloth = Tex(fr, "Ribbon", "ARTWORK")
    fr.cloth:SetAllPoints()
    fr.cloth:SetTexCoord(0, 1, 0, 112 / 128)
    fr.crest = fr:CreateTexture(nil, "OVERLAY")
    fr.crest:SetSize(34, 34)
    fr.crest:SetPoint("TOP", 0, -36)
    fr.color = FACTION_COLOR.A
    fr:SetScript("OnClick", function() Book:ToggleFaction() end)
    fr:SetScript("OnEnter", function(self)
        local c = self.color
        self.cloth:SetVertexColor(math.min(1, c[1] * 1.25), math.min(1, c[2] * 1.25), math.min(1, c[3] * 1.25))
        if GameTooltip then
            GameTooltip:SetOwner(self, "ANCHOR_BOTTOM")
            GameTooltip:SetText(frame.currentFac == "H" and "Show for the Alliance" or "Show for the Horde", 1, 0.95, 0.85)
            GameTooltip:AddLine(frame.currentFac == "H" and "This entry is written as recorded for the Horde." or "This entry is written as recorded for the Alliance.", 0.8, 0.8, 0.8)
            GameTooltip:Show()
        end
    end)
    fr:SetScript("OnLeave", function(self)
        local c = self.color
        self.cloth:SetVertexColor(c[1], c[2], c[3])
        if GameTooltip then GameTooltip:Hide() end
    end)
    L.factionBtn = fr

    -- ======================= RIGHT PAGE: atlas + index ===================
    local R = {}
    frame.R = R
    -- "Where to look", opening with an illuminated W
    R.drop = DropCap(right, 44, 30)
    R.drop:SetPoint("TOPLEFT", right, "TOPLEFT", PAD, -PAD - 4)
    R.drop.letter:SetText("W")
    R.head = Txt(right, "heading", 24, INK)
    R.head:SetPoint("LEFT", R.drop, "RIGHT", 4, -3)
    R.head:SetJustifyV("MIDDLE")
    R.head:SetText("here to look")
    R.headRule = Tex(right, "Flourish", "ARTWORK", FADED)
    R.headRule:SetSize(280, 30)
    R.headRule:SetPoint("TOPLEFT", R.drop, "BOTTOMLEFT", -4, -2)
    -- the chart, glued in with a toasted, ragged rim
    R.mapHolder = CreateFrame("Frame", nil, right)
    local mapW = 296
    local mapH = math.floor(mapW * 668 / 1002)
    R.mapHolder:SetSize(mapW, mapH)
    R.mapHolder:SetPoint("TOPLEFT", R.headRule, "BOTTOMLEFT", 4 + (pageW - mapW) / 2, -12)
    R.mapEdge = Tex(R.mapHolder, "MapEdge", "OVERLAY", nil, 2)
    R.mapEdge:SetPoint("TOPLEFT", -14, 14)
    R.mapEdge:SetPoint("BOTTOMRIGHT", 14, -14)
    R.mapWash = Fill(R.mapHolder, { 0.93, 0.86, 0.70, 0.12 }, "OVERLAY")
    R.mapWash:SetAllPoints()
    R.mapCompass = Tex(R.mapHolder, "Compass", "BACKGROUND", { FADED[1], FADED[2], FADED[3], 0.35 })
    R.mapCompass:SetSize(140, 140)
    R.mapCompass:SetPoint("CENTER")
    R.mapNone = Txt(R.mapHolder, "body", 12, FADED)
    R.mapNone:SetPoint("BOTTOM", 0, 10)
    R.mapNone:SetJustifyH("CENTER")
    R.mapNone:SetWidth(pageW - 40)
    R.caption = Txt(right, "body", 12, FADED)
    R.caption:SetPoint("TOPLEFT", R.mapHolder, "BOTTOMLEFT", -(pageW - mapW) / 2, -16)
    R.caption:SetWidth(pageW)
    R.caption:SetHeight(16)
    R.caption:SetJustifyH("CENTER")
    R.caption:SetWordWrap(false)

    R.indexScroll = ScrollTex(right, 130, 38)
    R.indexScroll:SetPoint("TOPLEFT", R.caption, "BOTTOMLEFT", -16, -8)
    R.indexHead = Txt(right, "heading", 18, RED)
    R.indexHead:SetPoint("LEFT", R.indexScroll, "LEFT", 24, 1)
    R.indexHead:SetText("Index")
    local box = CreateFrame("Frame", nil, right)
    box:SetSize(pageW, 28)
    box:SetPoint("TOPLEFT", R.indexScroll, "BOTTOMLEFT", 16, -2)
    Fill(box, { 1, 0.97, 0.88, 0.45 }):SetAllPoints()
    Outline(box, INK, 1)
    box.lens = Tex(box, "Lens", "OVERLAY", INK)
    box.lens:SetSize(18, 18)
    box.lens:SetPoint("RIGHT", -6, 0)
    local search = CreateFrame("EditBox", nil, box)
    search:SetPoint("TOPLEFT", 8, 0); search:SetPoint("BOTTOMRIGHT", -30, 0)
    search:SetAutoFocus(false)
    search:SetFont(Fonts().body, 13, "")
    search:SetTextColor(INK[1], INK[2], INK[3])
    if search.SetShadowColor then search:SetShadowColor(0, 0, 0, 0) end
    search:SetMaxLetters(60)
    search.placeholder = Txt(box, "body", 13, { FADED[1], FADED[2], FADED[3], 0.7 })
    search.placeholder:SetPoint("LEFT", 8, 0)
    search.placeholder:SetText("Look something up...")
    search:SetScript("OnTextChanged", function(self)
        self.placeholder:SetShown(self:GetText() == "")
        Book:UpdateIndex()
    end)
    search:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)
    search:SetScript("OnEnterPressed", function(self)
        self:ClearFocus()
        if frame.results and frame.results[1] and frame.results[1].itemID then Book:Show(frame.results[1].itemID) end
    end)
    frame.search = search
    R.indexNote = Txt(right, "body", 12, INK)
    R.indexNote:SetPoint("TOPLEFT", box, "BOTTOMLEFT", 0, -5)
    R.indexNote:SetHeight(14)
    R.indexNote:SetWidth(pageW)
    -- a tapering rule runs from the end of the note to the margin
    R.indexRule = Tex(right, "Rule", "ARTWORK", FADED)
    R.indexRule:SetHeight(12)
    R.indexRule:SetPoint("RIGHT", R.indexNote, "RIGHT", 0, 0)
    R.indexRule:SetPoint("LEFT", R.indexNote, "LEFT", 120, 0)
    frame.results = {}
    local prev = R.indexNote
    for i = 1, 5 do
        local row = CreateFrame("Button", nil, right)
        row:SetSize(pageW, 21)
        row:SetPoint("TOPLEFT", prev, "BOTTOMLEFT", 0, i == 1 and -4 or 0)
        row.hover = row:CreateTexture(nil, "BACKGROUND")
        row.hover:SetAllPoints()
        row.hover:SetColorTexture(1, 1, 1, 1)
        if row.hover.SetGradient and CreateColor then
            row.hover:SetGradient("HORIZONTAL", CreateColor(GOLD[1], GOLD[2], GOLD[3], 0.38), CreateColor(GOLD[1], GOLD[2], GOLD[3], 0))
        else
            row.hover:SetColorTexture(GOLD[1], GOLD[2], GOLD[3], 0.14)
        end
        row.hover:Hide()
        row.icon = row:CreateTexture(nil, "ARTWORK")
        row.icon:SetSize(18, 18)
        row.icon:SetPoint("LEFT", 2, 0)
        row.icon:SetTexCoord(0.07, 0.93, 0.07, 0.93)
        row.name = Txt(row, "body", 13, INK)
        row.name:SetPoint("LEFT", row.icon, "RIGHT", 8, 0)
        row.name:SetPoint("RIGHT", -4, 0)
        row.name:SetWordWrap(false)
        row:SetScript("OnEnter", function(self) self.hover:Show() end)
        row:SetScript("OnLeave", function(self) self.hover:Hide() end)
        row:SetScript("OnClick", function(self) if self.itemID then Book:Show(self.itemID) end end)
        row:Hide()
        frame.results[i] = row
        prev = row
    end

    -- controller legend: a small leather tab hanging beneath the book's bottom-right
    -- edge, filled in by the gamepad module when a pad is in use
    local legend = CreateFrame("Frame", nil, frame)
    legend:SetPoint("TOPRIGHT", frame, "BOTTOMRIGHT", -24, 2)
    legend:SetHeight(30)
    legend:SetFrameLevel((frame:GetFrameLevel() or 1) + 1)
    local legendBg = legend:CreateTexture(nil, "BACKGROUND")
    legendBg:SetTexture(MEDIA .. "Leather", "REPEAT", "REPEAT")
    if legendBg.SetHorizTile then legendBg:SetHorizTile(true); legendBg:SetVertTile(true) end
    legendBg:SetAllPoints()
    legendBg:SetVertexColor(0.55, 0.45, 0.35)
    Outline(legend, { 0.05, 0.02, 0.01, 0.8 }, 2, "BORDER")
    legend.text = Txt(legend, "body", 11, { 0.86, 0.78, 0.60 })
    legend.text:SetPoint("LEFT", 14, 0)
    legend.text:SetPoint("RIGHT", -14, 0)
    legend.text:SetJustifyH("RIGHT")
    legend.text:SetJustifyV("MIDDLE")
    legend.text:SetWordWrap(false)
    if legend.text.SetShadowColor then
        legend.text:SetShadowColor(0, 0, 0, 0.9)
        legend.text:SetShadowOffset(1, -1)
    end
    legend:Hide()
    frame.legend = legend
    R.legend = legend.text

    frame:SetScript("OnShow", function() Book:Render(); Book:UpdateIndex() end)
    frame:RegisterEvent("GET_ITEM_INFO_RECEIVED")
    frame:SetScript("OnEvent", function(self, event, id)
        if event == "GET_ITEM_INFO_RECEIVED" and self:IsShown() and self.itemID and Plain(id) == self.itemID then
            Book:Render()
        end
    end)
end

-- ---------------------------------------------------------------------------
-- Rendering
-- ---------------------------------------------------------------------------
local function Lines(itemID, fac)
    local entry = ns.Data and ns.Data[itemID]
    if not entry then return nil end
    local text = type(entry) == "string" and entry or (entry[fac] or entry.A or entry.H)
    if not text then return nil end
    local out = {}
    for line in text:gmatch("[^\n]+") do out[#out + 1] = line end
    return out
end

local function KindLine(info)
    local parts = {}
    if info.quality then parts[#parts + 1] = QUALITY_WORD[info.quality] or "" end
    if info.class and info.class ~= "" then parts[#parts + 1] = info.class end
    if info.subclass and info.subclass ~= "" and info.subclass ~= info.class then parts[#parts + 1] = info.subclass end
    if info.equipLoc and info.equipLoc ~= "" and _G[info.equipLoc] then parts[#parts + 1] = _G[info.equipLoc] end
    local s = table.concat(parts, "  -  ")
    if info.reqLevel and info.reqLevel > 1 then s = s .. "  -  Requires level " .. info.reqLevel end
    return s
end

function Book:Render()
    if not frame then return end
    local L, R = frame.L, frame.R
    local itemID = frame.itemID
    local fac = frame.facOverride or FactionKey()
    frame.currentFac = fac

    local showEntry = itemID ~= nil
    SetCrest(L.crest, fac)
    R.drop:SetFaction(fac)
    L.drop:SetFaction(fac)
    L.empty:SetShown(not showEntry)
    for _, k in ipairs({ "iconFrame", "title", "subtitle", "divider", "flavour", "provScroll", "provHead", "usesScroll", "usesHead", "drop", "uses", "factionNote", "factionBtn" }) do
        L[k]:SetShown(showEntry)
    end
    for _, row in ipairs(L.rows) do row.bullet:Hide(); row.text:Hide() end
    L.accountScroll:Hide(); L.accountHead:Hide(); L.accountDrop:Hide()
    for _, fs in ipairs(L.account) do fs:Hide() end
    frame.leafBtn:Hide()
    L.accountDrop:SetFaction(fac)
    if not showEntry then
        R.caption:SetText("")
        R.mapNone:SetText("")
        R.mapCompass:Show()
        DrawMap(R.mapHolder, nil)
        return
    end

    local info = ItemInfo(itemID)
    local lines = Lines(itemID, fac)
    local extra = ns.Extra and ns.Extra[itemID] or {}

    -- left page flow, starting below the crest and title banner
    local flow = Flow(frame.left)
    flow.y = -PAD - 44 - 40 - 14
    L.icon:SetTexture(info.icon)
    local iconY = flow.y
    flow:place(L.iconFrame, 54, 10)
    L.title:SetText(info.name)
    L.title:SetTextColor(QualityColor(info.quality))
    L.title:ClearAllPoints()
    L.title:SetPoint("TOPLEFT", frame.left, "TOPLEFT", PAD + 66, iconY + 2)
    L.subtitle:SetText(KindLine(info))
    L.subtitle:ClearAllPoints()
    L.subtitle:SetPoint("TOPLEFT", L.title, "BOTTOMLEFT", 0, -2)
    local titleBottom = iconY - 2 - (L.title:GetStringHeight() or 26) - 2 - (L.subtitle:GetStringHeight() or 12)
    if titleBottom < flow.y then flow.y = titleBottom - 8 end
    L.divider:ClearAllPoints()
    L.divider:SetPoint("TOP", frame.left, "TOP", 0, flow.y + 4)
    flow.y = flow.y - 30
    if extra.f and extra.f ~= "" then
        L.flavour:SetText("\"" .. extra.f .. "\"")
        L.flavour:Show()
        flow:text(L.flavour, 12)
    else
        L.flavour:Hide()
    end
    L.provScroll:SetWidth((L.provHead:GetStringWidth() or 100) + 70)
    flow:place(L.provScroll, 38, 2, PAD - 16)
    if lines then
        for i, line in ipairs(lines) do
            local row = L.rows[i]
            if row then
                row.text:SetText(line)
                row.text:Show()
                row.bullet:Show()
                row.text:ClearAllPoints()
                row.text:SetPoint("TOPLEFT", frame.left, "TOPLEFT", PAD + 18, flow.y)
                row.bullet:ClearAllPoints()
                row.bullet:SetPoint("TOPLEFT", frame.left, "TOPLEFT", PAD + 2, flow.y - 3)
                local h = row.text:GetStringHeight()
                if not h or h == 0 then h = 14 end
                flow.y = flow.y - h - 5
            end
        end
    else
        local row = L.rows[1]
        row.text:SetText("The archives hold no record of where this item comes from. It may be new to Forever, or simply not yet catalogued.")
        row.text:Show()
        row.bullet:Show()
        row.text:ClearAllPoints()
        row.text:SetPoint("TOPLEFT", frame.left, "TOPLEFT", PAD + 18, flow.y)
        row.bullet:ClearAllPoints()
        row.bullet:SetPoint("TOPLEFT", frame.left, "TOPLEFT", PAD + 2, flow.y - 3)
        flow.y = flow.y - (row.text:GetStringHeight() or 28) - 5
    end
    flow.y = flow.y - 8
    local uses = (fac == "H" and extra.uh) or extra.u
    if uses and uses ~= "" then
        L.usesScroll:SetWidth((L.usesHead:GetStringWidth() or 80) + 70)
        flow:place(L.usesScroll, 38, 4, PAD - 16)
        local first, rest = uses:match("^(%a)(.*)$")
        if first then
            -- an illuminated initial, with the paragraph set beside it
            L.drop.letter:SetText(first)
            L.uses:SetText((rest:gsub("^%s+", "")))
            L.drop:Show()
            L.drop:ClearAllPoints()
            L.drop:SetPoint("TOPLEFT", frame.left, "TOPLEFT", PAD, flow.y)
            L.uses:SetWidth(PAGE_W - 52)
            L.uses:ClearAllPoints()
            L.uses:SetPoint("TOPLEFT", frame.left, "TOPLEFT", PAD + 52, flow.y - 3)
            local h = L.uses:GetStringHeight()
            if not h or h == 0 then h = 14 end
            flow.y = flow.y - math.max(42, h + 3) - 6
        else
            L.drop:Hide()
            L.uses:SetText(uses)
            L.uses:SetWidth(PAGE_W)
            flow:text(L.uses, 6)
        end
        L.usesHead:Show()
        L.uses:Show()
    else
        L.usesScroll:Hide()
        L.usesHead:Hide()
        L.drop:Hide()
        L.uses:Hide()
    end
    -- the account: lore paragraphs, on this leaf if they fit, otherwise overleaf
    local paras = (ns.GetLore and ns.GetLore(itemID, fac)) or {}
    local pageH = BOOK_H - 52
    local reserve = 80                      -- room for the page button, faction note and page number
    local function PlaceParas(startY, first, headText)
        -- lay out paragraphs first..#paras from startY; returns the index of the first that did not fit
        L.accountHead:SetText(headText)
        L.accountScroll:SetWidth((L.accountHead:GetStringWidth() or 90) + 70)
        L.accountScroll:ClearAllPoints()
        L.accountScroll:SetPoint("TOPLEFT", frame.left, "TOPLEFT", PAD - 16, startY)
        local y = startY - 38 - 4
        local limit = -(pageH - reserve)
        local shown = 0
        for i = first, #paras do
            local fs = L.account[i - first + 1]
            if not fs then break end
            local text = paras[i]
            local letter, rest = text:match("^(%a)(.*)$")
            local useDrop = (i == 1) and letter ~= nil
            fs:Show()
            local h
            if useDrop then
                fs:SetWidth(PAGE_W - 52)
                fs:SetText((rest:gsub("^%s+", "")))
                h = fs:GetStringHeight()
                if not h or h == 0 then h = 14 end
                h = math.max(42, h + 3)
            else
                fs:SetWidth(PAGE_W)
                fs:SetText(text)
                h = fs:GetStringHeight()
                if not h or h == 0 then h = 14 end
            end
            if y - h < limit then
                fs:Hide()
                break
            end
            fs:ClearAllPoints()
            if useDrop then
                L.accountDrop.letter:SetText(letter)
                L.accountDrop:ClearAllPoints()
                L.accountDrop:SetPoint("TOPLEFT", frame.left, "TOPLEFT", PAD, y)
                L.accountDrop:Show()
                fs:SetPoint("TOPLEFT", frame.left, "TOPLEFT", PAD + 52, y - 3)
            else
                fs:SetPoint("TOPLEFT", frame.left, "TOPLEFT", PAD, y)
            end
            shown = shown + 1
            y = y - h - 8
        end
        if shown > 0 then L.accountScroll:Show(); L.accountHead:Show() end
        return first + shown
    end
    local leaf = frame.leaf or 1
    local nextIndex = 1
    if #paras > 0 then
        nextIndex = PlaceParas(flow.y - 6, 1, "The account")
    end
    local leafCount = (nextIndex <= #paras) and 2 or 1
    if leaf > leafCount then leaf = 1; frame.leaf = 1 end
    frame.leafCount = leafCount
    if leaf == 2 then
        -- overleaf: the crest and banner stay, the entry gives way to the account
        for _, k in ipairs({ "iconFrame", "title", "subtitle", "divider", "flavour", "provScroll", "provHead", "usesScroll", "usesHead", "drop", "uses" }) do L[k]:Hide() end
        for _, row in ipairs(L.rows) do row.bullet:Hide(); row.text:Hide() end
        for _, fs in ipairs(L.account) do fs:Hide() end
        L.accountDrop:Hide()
        PlaceParas(-PAD - 100, nextIndex, nextIndex > 1 and "The account, continued" or "The account")
    end
    frame.pageNum[1]:SetText(leaf == 2 and "~ 2 ~" or "~ 1 ~")
    if leaf == 2 then
        frame.leafBtn:SetDirection(-1)
        frame.leafBtn:Show()
    elseif leafCount == 2 then
        frame.leafBtn:SetDirection(1)
        frame.leafBtn:Show()
    end
    L.factionNote:SetText(fac == "H" and "As recorded for the Horde." or "As recorded for the Alliance.")
    -- the ribbon is the switch, so it wears the colours of the faction it flips to
    local other = (fac == "H") and "A" or "H"
    local fc = FACTION_COLOR[other]
    L.factionBtn.color = fc
    L.factionBtn.cloth:SetVertexColor(fc[1], fc[2], fc[3])
    SetCrest(L.factionBtn.crest, other)

    -- right page: atlas
    local zone = (fac == "H" and extra.zh) or extra.z
    local mapID = zone and FindMapID(zone)
    local drawn = mapID and DrawMap(R.mapHolder, mapID)
    R.mapCompass:SetShown(not drawn)
    if drawn then
        R.mapNone:SetText("")
        R.caption:SetText("Most plentiful in " .. zone .. ".")
    elseif zone then
        R.mapNone:SetText("No chart of " .. zone .. " is to hand.")
        R.caption:SetText("Most plentiful in " .. zone .. ".")
    else
        R.mapNone:SetText(lines and "No single region to chart." or "Uncharted.")
        R.caption:SetText(lines and "This item is not tied to one place; see the entry." or "")
    end
end

-- ---------------------------------------------------------------------------
-- Index / search
-- ---------------------------------------------------------------------------
local function AddHistory(itemID)
    if not ns.db then return end
    ns.db.history = ns.db.history or {}
    local h = ns.db.history
    for i = #h, 1, -1 do if h[i] == itemID then table.remove(h, i) end end
    table.insert(h, 1, itemID)
    while #h > 12 do table.remove(h) end
end

function Book:UpdateIndex(keepOffset)
    if not frame then return end
    local query = frame.search:GetText() or ""
    query = query:lower():gsub("^%s+", ""):gsub("%s+$", "")
    if query ~= frame.lastQuery then
        frame.lastQuery = query
        frame.resultOffset = 0
    elseif not keepOffset then
        frame.resultOffset = frame.resultOffset or 0
    end
    local ids = {}
    if query == "" then
        frame.R.indexNote:SetText("Recently consulted")
        for _, id in ipairs(ns.db and ns.db.history or {}) do ids[#ids + 1] = id end
    else
        local starts, contains = {}, {}
        for id, name in pairs(ns.Names or {}) do
            local low = name:lower()
            local pos = low:find(query, 1, true)
            if pos == 1 then starts[#starts + 1] = id elseif pos then contains[#contains + 1] = id end
        end
        local byName = function(a, b) return ns.Names[a] < ns.Names[b] end
        table.sort(starts, byName)
        table.sort(contains, byName)
        for _, id in ipairs(starts) do ids[#ids + 1] = id end
        for _, id in ipairs(contains) do ids[#ids + 1] = id end
        local offset = frame.resultOffset or 0
        local shown = #ids > #frame.results and (", showing " .. (offset + 1) .. "-" .. math.min(#ids, offset + #frame.results)) or ""
        frame.R.indexNote:SetText(#ids == 0 and "Nothing by that name in the archives." or (#ids .. " entr" .. (#ids == 1 and "y" or "ies") .. shown))
    end
    frame.resultCount = #ids
    local noteW = frame.R.indexNote:GetStringWidth() or 0
    frame.R.indexRule:SetPoint("LEFT", frame.R.indexNote, "LEFT", noteW + 10, 0)
    frame.R.indexRule:SetShown(noteW + 40 < PAGE_W)
    local offset = frame.resultOffset or 0
    if offset >= #ids then offset = 0; frame.resultOffset = 0 end
    for i, row in ipairs(frame.results) do
        local id = ids[offset + i]
        if id then
            row.itemID = id
            local info = ItemInfo(id)
            row.icon:SetTexture(info.icon)
            row.name:SetText(info.name)
            row.name:SetTextColor(QualityColor(info.quality))
            row:Show()
        else
            row.itemID = nil
            row:Hide()
        end
    end
end

-- ---------------------------------------------------------------------------
-- Public API
-- ---------------------------------------------------------------------------
function Book:Open()
    if not frame then BuildBook() end
    frame:Show()
end

function Book:GetFrame()
    return frame
end

-- Show the next/previous page of search results (gamepad triggers).
function Book:PageResults(delta)
    if not frame then return end
    local per = #frame.results
    local count = frame.resultCount or 0
    local offset = (frame.resultOffset or 0) + delta * per
    if offset < 0 then offset = 0 end
    if offset >= count then offset = math.max(0, (frame.resultOffset or 0)) end
    frame.resultOffset = offset
    Book:UpdateIndex(true)
end

-- Step through recently consulted entries (gamepad shoulders).
function Book:HistoryStep(delta)
    local h = ns.db and ns.db.history or {}
    if not frame or #h == 0 then return end
    local pos
    for i, id in ipairs(h) do if id == frame.itemID then pos = i end end
    local target = (pos or 0) + delta
    if target < 1 or target > #h then return end
    local id = h[target]
    -- do not reorder history while browsing it
    frame.itemID = id
    frame.lastShow = GetTime and GetTime() or 0
    frame.facOverride = nil
    frame.leaf = 1
    Book:Render()
end

-- Turn the left page between the entry and the account.
function Book:TurnLeaf(delta)
    if not frame or not frame.itemID then return end
    local leaf = (frame.leaf or 1) + delta
    if leaf < 1 or leaf > (frame.leafCount or 1) then return end
    frame.leaf = leaf
    Book:Render()
end

function Book:ToggleFaction()
    if not frame then return end
    frame.facOverride = (frame.currentFac == "A") and "H" or "A"
    Book:Render()
end

function Book:SetLegend(text)
    if not (frame and frame.legend) then return end
    text = text or ""
    frame.legend.text:SetText(text)
    if text == "" then
        frame.legend:Hide()
    else
        -- size the tab to its contents, with room for the padding on each side
        local w = frame.legend.text:GetStringWidth() or 0
        frame.legend:SetWidth(math.min(BOOK_W - 48, w + 28))
        frame.legend:Show()
    end
end

function Book:Toggle()
    if frame and frame:IsShown() then frame:Hide() else Book:Open() end
end

function Book:Show(itemID)
    itemID = tonumber(itemID)
    if not itemID then return end
    -- several click paths can report the same click; open once
    local now = GetTime and GetTime() or 0
    if frame and frame.itemID == itemID and frame.lastShow and now - frame.lastShow < 0.4 then
        frame:Show()
        return
    end
    if not frame then BuildBook() end
    frame.itemID = itemID
    frame.lastShow = now
    frame.facOverride = nil
    frame.leaf = 1
    AddHistory(itemID)
    frame:Show()
    Book:Render()
    Book:UpdateIndex()
end

function Book:ShowLink(link)
    link = Plain(link)
    if type(link) ~= "string" then return end
    local id = link:match("item:(%d+)")
    if id then Book:Show(tonumber(id)) end
end

function Book:Search(text)
    Book:Open()
    frame.search:SetText(text or "")
    frame.search:SetFocus()
    Book:UpdateIndex()
end

-- ---------------------------------------------------------------------------
-- Alt-click hooks (bags, character sheet, merchant, chat links)
-- ---------------------------------------------------------------------------
ns.debug = { hooks = {}, clicks = 0, lastLink = nil, lastItem = nil }

local function AltHeld()
    if not (ns.db and ns.db.altClick ~= false) then return false end
    if type(IsAltKeyDown) ~= "function" then return false end
    local ok, down = pcall(IsAltKeyDown)
    return ok and Plain(down) == true
end

local function AltClick(link, itemID)
    ns.debug.clicks = ns.debug.clicks + 1
    ns.debug.lastLink = type(Plain(link)) == "string" and link or (link ~= nil and "<secret or non-string>" or nil)
    ns.debug.lastItem = itemID
    if not AltHeld() then return end
    if itemID then Book:Show(itemID) else Book:ShowLink(link) end
end

-- Item ID of a bag slot, asked of the client directly so a secret link does
-- not get in the way.
local function SlotItemID(bag, slot)
    if bag == nil or slot == nil then return nil end
    local getID = (C_Container and C_Container.GetContainerItemID) or GetContainerItemID
    if type(getID) ~= "function" then return nil end
    local ok, id = pcall(getID, bag, slot)
    id = ok and Plain(id) or nil
    return type(id) == "number" and id or nil
end

local function ButtonBagSlot(button)
    local bag, slot
    if button.GetBagID then
        local ok, v = pcall(button.GetBagID, button)
        bag = ok and Plain(v) or nil
    end
    if bag == nil and button.GetParent then
        local parent = button:GetParent()
        if parent and parent.GetID then
            local ok, v = pcall(parent.GetID, parent)
            bag = ok and Plain(v) or nil
        end
    end
    if button.GetID then
        local ok, v = pcall(button.GetID, button)
        slot = ok and Plain(v) or nil
    end
    return bag, slot
end

local function HookBagButton(button)
    if not button or button.wiiHooked or not button.HookScript then return end
    button.wiiHooked = true
    button:HookScript("OnClick", function(self, mouse)
        if not AltHeld() then return end
        local bag, slot = ButtonBagSlot(self)
        local id = SlotItemID(bag, slot)
        if id then AltClick(nil, id) end
    end)
    ns.debug.hooks.bagButtons = (ns.debug.hooks.bagButtons or 0) + 1
end

local function HookBags()
    -- combined bag (modern clients)
    local combined = _G.ContainerFrameCombinedBags
    if combined and type(combined.Items) == "table" then
        for _, b in pairs(combined.Items) do HookBagButton(b) end
    end
    for i = 1, 13 do
        local cf = _G["ContainerFrame" .. i]
        if cf then
            if type(cf.Items) == "table" then
                for _, b in pairs(cf.Items) do HookBagButton(b) end
            end
            for j = 1, 36 do
                local b = _G["ContainerFrame" .. i .. "Item" .. j]
                if b then HookBagButton(b) else break end
            end
        end
    end
    -- bank
    for j = 1, 28 do
        local b = _G["BankFrameItem" .. j]
        if b then HookBagButton(b) end
    end
end

if type(hooksecurefunc) == "function" then
    if type(HandleModifiedItemClick) == "function" then
        hooksecurefunc("HandleModifiedItemClick", function(link) AltClick(link) end)
        ns.debug.hooks.HandleModifiedItemClick = true
    end
    if type(SetItemRef) == "function" then
        hooksecurefunc("SetItemRef", function(link) AltClick(link) end)
        ns.debug.hooks.SetItemRef = true
    end
    if type(ContainerFrameItemButton_OnModifiedClick) == "function" then
        hooksecurefunc("ContainerFrameItemButton_OnModifiedClick", function(self)
            local bag, slot = ButtonBagSlot(self)
            AltClick(nil, SlotItemID(bag, slot))
        end)
        ns.debug.hooks.ContainerFrameItemButton_OnModifiedClick = true
    end
    -- modern bag buttons are created from a mixin; hook the mixin for buttons
    -- made later, and the existing buttons directly whenever bags update
    if type(ContainerFrameItemButtonMixin) == "table" and type(ContainerFrameItemButtonMixin.OnClick) == "function" then
        hooksecurefunc(ContainerFrameItemButtonMixin, "OnClick", function(self)
            if self.wiiHooked then return end
            if not AltHeld() then return end
            local bag, slot = ButtonBagSlot(self)
            AltClick(nil, SlotItemID(bag, slot))
        end)
        ns.debug.hooks.ContainerFrameItemButtonMixin = true
    end
end

local bagWatcher = CreateFrame("Frame")
bagWatcher:RegisterEvent("PLAYER_LOGIN")
bagWatcher:RegisterEvent("BAG_UPDATE_DELAYED")
bagWatcher:RegisterEvent("BANKFRAME_OPENED")
bagWatcher:SetScript("OnEvent", function() pcall(HookBags) end)
for i = 1, 13 do
    local cf = _G["ContainerFrame" .. i]
    if cf and cf.HookScript then cf:HookScript("OnShow", function() pcall(HookBags) end) end
end
if _G.ContainerFrameCombinedBags and _G.ContainerFrameCombinedBags.HookScript then
    _G.ContainerFrameCombinedBags:HookScript("OnShow", function() pcall(HookBags) end)
end

-- Alt-click anywhere an item tooltip is showing: profession reagents and
-- results, auction listings, quest rewards, loot windows, chat links...
local catcher = CreateFrame("Frame")
if catcher.RegisterEvent then pcall(catcher.RegisterEvent, catcher, "GLOBAL_MOUSE_DOWN") end
catcher:SetScript("OnEvent", function(_, event, button)
    if Plain(button) ~= "LeftButton" or not AltHeld() then return end
    for _, tip in ipairs({ GameTooltip, ItemRefTooltip }) do
        if tip and tip.IsShown and tip:IsShown() and tip.GetItem then
            local ok, _, link = pcall(tip.GetItem, tip)
            link = ok and Plain(link) or nil
            if type(link) == "string" then
                local id = link:match("item:(%d+)")
                if id then
                    ns.debug.hoverClicks = (ns.debug.hoverClicks or 0) + 1
                    AltClick(link, tonumber(id))
                    return
                end
            end
        end
    end
end)
ns.debug.hooks.GLOBAL_MOUSE_DOWN = true

-- ---------------------------------------------------------------------------
-- Minimap button
-- ---------------------------------------------------------------------------
local minimapButton
function Book:UpdateMinimapButton()
    if not minimapButton then return end
    local cfg = ns.db and ns.db.minimap or {}
    if cfg.hide then minimapButton:Hide() else minimapButton:Show() end
    local angle = math.rad(cfg.angle or 200)
    local radius = (Minimap and Minimap.GetWidth and (Minimap:GetWidth() or 140) / 2 + 10) or 80
    minimapButton:ClearAllPoints()
    minimapButton:SetPoint("CENTER", Minimap, "CENTER", math.cos(angle) * radius, math.sin(angle) * radius)
end

function Book:CreateMinimapButton()
    if minimapButton or not Minimap then return end
    local b = CreateFrame("Button", "WhereIsItMinimapButton", Minimap)
    minimapButton = b
    b:SetSize(31, 31)
    b:SetFrameStrata("MEDIUM")
    b:SetFrameLevel(8)
    b:RegisterForClicks("LeftButtonUp", "RightButtonUp")
    b:RegisterForDrag("LeftButton")
    b:SetHighlightTexture("Interface\\Minimap\\UI-Minimap-ZoomButton-Highlight")
    local bg = b:CreateTexture(nil, "BACKGROUND")
    bg:SetTexture("Interface\\Minimap\\UI-Minimap-Background")
    bg:SetSize(20, 20)
    bg:SetPoint("TOPLEFT", 7, -5)
    local icon = b:CreateTexture(nil, "ARTWORK")
    icon:SetTexture("Interface\\Icons\\INV_Misc_Book_11")
    icon:SetSize(18, 18)
    icon:SetPoint("TOPLEFT", 6, -6)
    icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)
    local border = b:CreateTexture(nil, "OVERLAY")
    border:SetTexture("Interface\\Minimap\\MiniMap-TrackingBorder")
    border:SetSize(53, 53)
    border:SetPoint("TOPLEFT")

    b:SetScript("OnClick", function(_, mouse)
        if mouse == "RightButton" then
            if ns.OpenOptions then ns.OpenOptions() end
        else
            Book:Toggle()
        end
    end)
    b:SetScript("OnEnter", function(self)
        GameTooltip:SetOwner(self, "ANCHOR_LEFT")
        GameTooltip:SetText("Where Is It")
        GameTooltip:AddLine("Left-click: open the encyclopedia", 1, 1, 1)
        GameTooltip:AddLine("Right-click: options", 1, 1, 1)
        GameTooltip:AddLine("Drag: move this button", 0.7, 0.7, 0.7)
        GameTooltip:Show()
    end)
    b:SetScript("OnLeave", function() GameTooltip:Hide() end)
    b:SetScript("OnDragStart", function(self)
        self:SetScript("OnUpdate", function(self)
            local mx, my = Minimap:GetCenter()
            local cx, cy = GetCursorPosition()
            local scale = Minimap:GetEffectiveScale() or 1
            cx, cy = cx / scale, cy / scale
            if mx and my then
                ns.db.minimap = ns.db.minimap or {}
                ns.db.minimap.angle = math.deg(math.atan2(cy - my, cx - mx))
                Book:UpdateMinimapButton()
            end
        end)
    end)
    b:SetScript("OnDragStop", function(self) self:SetScript("OnUpdate", nil) end)
    Book:UpdateMinimapButton()
end

function Book:DebugReport(print)
    local d = ns.debug
    local hooks = {}
    for k, v in pairs(d.hooks) do hooks[#hooks + 1] = k .. "=" .. tostring(v) end
    table.sort(hooks)
    print("book loaded: yes; frame built: " .. tostring(frame ~= nil) .. "; altClick option: " .. tostring(ns.db and ns.db.altClick))
    print("hooks: " .. (#hooks > 0 and table.concat(hooks, ", ") or "none"))
    print("clicks seen: " .. d.clicks .. " (" .. tostring(d.hoverClicks or 0) .. " via hovered tooltip); last link: " .. tostring(d.lastLink) .. "; last item: " .. tostring(d.lastItem))
    print("HandleModifiedItemClick is " .. type(HandleModifiedItemClick) .. ", ContainerFrameItemButtonMixin is " .. type(ContainerFrameItemButtonMixin) .. ", C_Container is " .. type(C_Container))
    local okMap, info = pcall(function() return C_Map.GetMapInfo(C_Map.GetBestMapForUnit("player")) end)
    print("map api: " .. (okMap and type(info) == "table" and ("ok, you are in " .. tostring(Plain(info.name))) or "unavailable"))
end
