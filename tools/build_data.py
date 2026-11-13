#!/usr/bin/env python3
"""
Builds WhereIsIt_Data.lua: item ID -> short, encyclopedia-style hint about where
an item comes from, without exact coordinates or NPC names.

Inputs (both open source):
  * vmangos world database, SQLite snapshot (mangos.sqlite)
      https://github.com/vmangos/core/releases/tag/db_latest
      -> loot tables, vendors, creature/gameobject templates, spells, quests, zones
  * pfQuest database (db/units.lua, db/objects.lua, db/enUS/*.lua)
      https://github.com/shagu/pfQuest  (MIT)
      -> per-zone spawn points for creatures and objects in the open world,
         which gives "where is the densest population" and unit faction.

Usage:
  python -I build_data.py --mangos path/to/mangos.sqlite --pfquest path/to/pfQuest/db \
      --out ../WhereIsIt_Data.lua [--check 4470 6889 ...]
"""
import argparse
import datetime as dt
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict

# ---------------------------------------------------------------------------
# Minimal Lua table-literal parser (enough for pfQuest's generated files)
# ---------------------------------------------------------------------------
_NUM = re.compile(r"-?(?:0[xX][0-9a-fA-F]+|\d+\.?\d*(?:[eE][-+]?\d+)?|\.\d+(?:[eE][-+]?\d+)?)")
_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class LuaParser:
    def __init__(self, text):
        self.s = text
        self.i = 0
        self.n = len(text)

    def ws(self):
        s, n = self.s, self.n
        while self.i < n:
            ch = s[self.i]
            if ch in " \t\r\n":
                self.i += 1
            elif s.startswith("--", self.i):
                j = s.find("\n", self.i)
                self.i = n if j < 0 else j + 1
            else:
                break

    def value(self):
        self.ws()
        ch = self.s[self.i]
        if ch == "{":
            return self.table()
        if ch in "\"'":
            return self.string(ch)
        if self.s.startswith("true", self.i):
            self.i += 4
            return True
        if self.s.startswith("false", self.i):
            self.i += 5
            return False
        if self.s.startswith("nil", self.i):
            self.i += 3
            return None
        m = _NUM.match(self.s, self.i)
        if m:
            self.i = m.end()
            t = m.group(0)
            if t.lower().startswith(("0x", "-0x")):
                return int(t, 16)
            return float(t) if any(c in t for c in ".eE") else int(t)
        raise ValueError("unexpected %r at %d" % (self.s[self.i:self.i + 20], self.i))

    def string(self, q):
        s = self.s
        self.i += 1
        out = []
        while True:
            ch = s[self.i]
            if ch == "\\":
                nxt = s[self.i + 1]
                if nxt == "n":
                    out.append("\n"); self.i += 2
                elif nxt == "t":
                    out.append("\t"); self.i += 2
                elif nxt.isdigit():
                    m = re.match(r"\d{1,3}", s[self.i + 1:self.i + 4])
                    out.append(chr(int(m.group(0)))); self.i += 1 + len(m.group(0))
                else:
                    out.append(nxt); self.i += 2
            elif ch == q:
                self.i += 1
                return "".join(out)
            else:
                out.append(ch)
                self.i += 1

    def table(self):
        self.i += 1  # {
        d = {}
        idx = 1
        while True:
            self.ws()
            ch = self.s[self.i]
            if ch == "}":
                self.i += 1
                return d
            if ch == "[":
                self.i += 1
                k = self.value()
                self.ws()
                assert self.s[self.i] == "]", "expected ] at %d" % self.i
                self.i += 1
                self.ws()
                assert self.s[self.i] == "=", "expected = at %d" % self.i
                self.i += 1
                d[k] = self.value()
            else:
                m = _IDENT.match(self.s, self.i)
                if m and m.group(0) not in ("true", "false", "nil"):
                    save = self.i
                    self.i = m.end()
                    self.ws()
                    if self.s[self.i] == "=":
                        self.i += 1
                        d[m.group(0)] = self.value()
                    else:
                        self.i = save
                        d[idx] = self.value()
                        idx += 1
                else:
                    d[idx] = self.value()
                    idx += 1
            self.ws()
            if self.s[self.i] in ",;":
                self.i += 1


def load_pf_table(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    start = text.index("{", text.index("="))
    return LuaParser(text[start:]).value()


# ---------------------------------------------------------------------------
# Zone knowledge
# ---------------------------------------------------------------------------
# instance map id -> zone-level AreaTable id (vmangos area_template)
MAP_TO_ZONE = {
    30: 2597, 33: 209, 34: 717, 36: 1581, 43: 718, 47: 491, 48: 719, 70: 1337,
    90: 721, 109: 1417, 129: 722, 189: 796, 209: 1176, 289: 2057, 309: 1977,
    329: 2017, 349: 2100, 369: 2257, 389: 2437, 409: 2717, 429: 2557, 449: 2918,
    469: 2677, 489: 3277, 509: 3429, 529: 3358, 531: 3428, 533: 3456,
    229: 1583, 230: 1584, 249: 2159, 450: 2917,
}
RAID_ZONES = {2717, 2677, 3429, 3428, 3456, 1977, 2159}
BATTLEGROUND_ZONES = {2597, 3277, 3358}
BATTLEGROUND_MAPS = {30, 489, 529}
DUNGEON_ZONES = set(MAP_TO_ZONE.values())
CITY_ZONES = {1519, 1537, 1657, 1637, 1638, 1497}   # a compass direction inside a city is noise

# Bosses and elites that are summoned by scripts rather than placed in the
# world, so neither pfQuest nor the creature table knows where they live.
BOSS_ZONE_OVERRIDE = {
    # Molten Core / BWL / Onyxia / AQ / Naxx / ZG
    11502: 2717, 12018: 2717, 11664: 2717, 11663: 2717,
    11583: 2677, 12463: 2677, 10184: 2159, 12739: 2159,
    15517: 3428, 15727: 3428, 15299: 3428, 15589: 3428, 14862: 3428,
    15339: 3429, 15341: 3429,
    15989: 3456, 15990: 3456, 16803: 3456, 16783: 3456, 16784: 3456, 16785: 3456,
    14515: 1977, 15082: 1977, 15083: 1977, 15084: 1977, 15085: 1977, 15114: 1977,
    # Blackrock Spire
    10584: 1583, 9596: 1583, 10263: 1583, 10339: 1583, 10264: 1583, 10268: 1583, 10447: 1583,
    10680: 1583, 10681: 1583, 10742: 1583, 10601: 1583, 10602: 1583, 10258: 1583, 10683: 1583,
    9816: 1583, 16042: 1583, 10429: 1583, 16080: 1583,
    # Blackrock Depths
    16059: 1584, 9537: 1584, 9437: 1584, 9438: 1584, 9439: 1584, 9441: 1584, 9442: 1584, 9443: 1584,
    9476: 1584, 9522: 1584, 10076: 1584, 9027: 1584, 9028: 1584, 9029: 1584, 9030: 1584, 9031: 1584,
    9032: 1584, 9541: 1584, 9502: 1584, 9034: 1584, 9035: 1584, 9036: 1584, 9037: 1584, 9038: 1584,
    9039: 1584, 9040: 1584,
    # Stratholme / Scholomance / Dire Maul
    10808: 2017, 10813: 2017, 11121: 2017, 10439: 2017, 11058: 2017, 11120: 2017, 11143: 2017,
    12128: 2017, 10394: 2017, 16101: 2017, 16102: 2017,
    14516: 2057, 1853: 2057, 10506: 2057, 16118: 2057,
    14502: 2557, 14506: 2557, 14518: 2557, 14519: 2557, 14520: 2557, 14521: 2557, 14351: 2557, 16097: 2557,
    # low level dungeons
    3654: 718, 7273: 1176, 7796: 1176, 7275: 1176, 7356: 722, 7361: 721, 2748: 1337, 7228: 1337,
    5709: 1417, 8443: 1417,
    # open world summons
    14435: 1377, 15305: 1377, 15203: 1377, 15205: 1377, 15204: 1377, 15206: 1377, 15207: 1377,
    15208: 1377, 15220: 1377, 15211: 1377, 15209: 1377, 15212: 1377, 15307: 1377, 14530: 1377,
    15625: 10, 15571: 357, 7664: 4, 7734: 4, 7735: 4, 10737: 618, 10741: 618, 14535: 618,
    2707: 47, 1494: 33, 8391: 51, 14533: 490, 14534: 46,
}

# creatures / objects that are developer leftovers
TEST_NAME_RE = re.compile(r"TEST|UNUSED|\[PH\]|\bDND\b|Trigger|Dummy|Credit|Invisible|Spawn Point|Waypoint|Programmer|Designer|Copy of|\(old\)|OLD\b|Placeholder", re.I)

# Zones that are clearly one faction's territory. Everything else is treated
# as contested/neutral and shown to both factions. Dungeons are always neutral.
ALLIANCE_ZONES = {1, 12, 38, 40, 44, 10, 11, 141, 148, 1519, 1537, 1657, 2257}
HORDE_ZONES = {14, 17, 85, 130, 215, 1637, 1638, 1497}

HERB_NAMES = {
    "Peacebloom", "Silverleaf", "Earthroot", "Mageroyal", "Briarthorn", "Stranglekelp",
    "Bruiseweed", "Wild Steelbloom", "Grave Moss", "Kingsblood", "Liferoot", "Fadeleaf",
    "Goldthorn", "Khadgar's Whisker", "Wintersbite", "Firebloom", "Purple Lotus",
    "Arthas' Tears", "Sungrass", "Blindweed", "Ghost Mushroom", "Gromsblood",
    "Golden Sansam", "Dreamfoil", "Mountain Silversage", "Plaguebloom", "Icecap",
    "Black Lotus", "Bloodthistle",
}
MINE_RE = re.compile(r"\b(Vein|Deposit|Lode|Node|Ore)\b", re.I)
CHEST_RE = re.compile(r"\b(Chest|Strongbox|Footlocker|Lockbox|Crate|Barrel|Cache|Coffer|Trunk|Supplies|Stash|Treasure|Clam)\b", re.I)

SKILL_PHRASE = {
    164: ("Forged by blacksmiths", "Blacksmithing"),
    165: ("Stitched by leatherworkers", "Leatherworking"),
    171: ("Brewed by alchemists", "Alchemy"),
    185: ("Prepared by cooks", "Cooking"),
    186: ("Smelted by miners", "Mining"),
    197: ("Woven by tailors", "Tailoring"),
    202: ("Built by engineers", "Engineering"),
    333: ("Made by enchanters", "Enchanting"),
    129: ("Made by field medics", "First Aid"),
    40: ("Mixed by rogues", "Poisons"),
    356: ("Fished up by anglers", "Fishing"),
}
RECIPE_SUBCLASS_SKILL = {1: 165, 2: 197, 3: 202, 4: 164, 5: 185, 6: 171, 7: 129, 8: 333, 9: 356}

QUALITY = {0: "poor", 1: "common", 2: "uncommon", 3: "rare", 4: "epic", 5: "legendary"}

PET_FAMILY = {
    1: "wolves", 2: "great cats", 3: "spiders", 4: "bears", 5: "boars", 6: "crocolisks",
    7: "carrion birds", 8: "crabs", 9: "gorillas", 11: "raptors", 12: "plainstriders",
    20: "scorpids", 21: "turtles", 24: "bats", 25: "hyenas", 26: "owls", 27: "wind serpents",
}
WINGED = {"carrion birds", "bats", "owls", "wind serpents", "birds of prey", "hippogryphs", "gryphons", "wyverns", "winged creatures"}
CRAWLING = {"spiders", "scorpids", "crabs", "worms and grubs", "silithid", "beetles"}

# (regex on creature name, plural descriptor) - first match wins
BEAST_KW = [
    (r"Kodo", "kodo beasts"), (r"Strider", "plainstriders"), (r"\b(Stag|Deer|Doe|Buck|Elk)\b", "stags"),
    (r"\b(Rabbit|Hare)\b", "rabbits"), (r"Prairie Dog", "prairie dogs"), (r"\b(Basilisk|Thunder Lizard|Lizard)\b", "basilisks"),
    (r"Hippogryph", "hippogryphs"), (r"Gryphon", "gryphons"), (r"\b(Buzzard|Vulture|Condor|Roc)\b", "carrion birds"),
    (r"\b(Hawk|Eagle|Falcon|Owl)\b", "birds of prey"), (r"\b(Serpent|Snake|Cobra|Adder|Viper)\b", "serpents"),
    (r"\b(Worm|Maggot|Grub|Larva|Slug|Leech)\b", "worms and grubs"), (r"Silithid", "silithid"),
    (r"\b(Wasp|Beetle|Insect|Scarab)\b", "beetles"), (r"\b(Shark|Fish|Eel|Threshadon|Whale|Snapjaw|Makrura|Murloc)\b", "sea creatures"),
    (r"Chimaera", "chimaera"), (r"\b(Owlkin|Owlbeast|Wildkin|Moonkin)\b", "wildkin"), (r"Yeti", "yeti"),
    (r"\b(Ape|Gorilla)\b", "gorillas"), (r"\b(Lion|Panther|Tiger|Cat|Sabre|Prowler|Stalker|Lynx|Cougar)\b", "great cats"),
    (r"Thresher|Threshadon", "sea creatures"), (r"Ravasaur", "raptors"), (r"Core Hound|Hound", "hounds"),
    (r"Zhevra", "zhevra"), (r"Stegodon|Diemetradon|Pterrordax|Devilsaur|Dinosaur|Incendosaur", "primordial beasts"),
    (r"Pridewing|Wyvern", "wyverns"), (r"Hydra", "hydras"),
    (r"Hyena", "hyenas"), (r"\b(Horse|Stallion|Mare)\b", "horses"), (r"Turtle", "turtles"), (r"Crab", "crabs"),
    (r"Spider|Recluse|Tarantula|Widow", "spiders"), (r"Scorpid|Scorpion", "scorpids"), (r"Raptor", "raptors"),
    (r"Boar", "boars"), (r"Bear|Grizzly", "bears"), (r"Wolf|Worg|Wolves", "wolves"), (r"Bat\b", "bats"),
    (r"Crocolisk|Croc", "crocolisks"), (r"Wind Serpent|Wyvern", "wind serpents"), (r"Bird|Parrot|Flyer|Flier", "winged creatures"),
    (r"Moth|Butterfly", "winged creatures"), (r"Frog|Toad", "frogs"), (r"Ram\b", "rams"), (r"Sheep|Cow|Pig|Chicken|Rat|Squirrel|Fawn|Hatchling", "critters"),
]
HUMANOID_KW = [
    (r"Defias", "Defias brigands"), (r"Kobold", "kobolds"), (r"Gnoll|Riverpaw|Redridge|Mosshide|Shadowhide|Rot Hide|Mudsnout|Wildpaw|Woodpaw|Palemane|Rotgrip", "gnolls"),
    (r"Murloc|Mur'gul|Greymist|Torn Fin|Bluegill|Rockpool|Saltscale|Blindlight|Daggerspine|Siltfin|Coastrunner|Tidehunter|Oracle|Netter|Minor Oracle|Warrior of the Deep", "murlocs"),
    (r"Lost One", "the Lost Ones"), (r"Dalaran", "Dalaran wizards"), (r"Stonard|Firebrand|Bloodaxe", "Blackrock orcs"), (r"Jaedenar", "cultists"),
    (r"Troll|Witherbark|Shadowpine|Skullsplitter|Bloodscalp|Vilebranch|Amani|Sandfury|Gurubashi|Hakkari|Atal'ai|Darkspear|Frostmane|Mosh'Ogg|Smolderthorn|Firetree|Spirestone", "trolls"),
    (r"Harpy|Bloodfury|Witchwing|Windfury|Screeching|Shrike", "harpies"),
    (r"Ogre|Gordok|Gordunni|Boulderfist|Deadwind|Dustbelcher|Splinter Fist|Stonemaul|Crushridge|Dreadmaul|Firegut", "ogres"),
    (r"Centaur|Kolkar|Magram|Gelkis|Galak|Maraudine", "centaur"), (r"Quilboar|Razormane|Bristleback|Razorfen|Death's Head|Deathshead", "quilboar"),
    (r"Furbolg|Gnarlpine|Thistlefur|Foulweald|Deadwood|Timbermaw|Winterfall|Blackwood|Felpaw|Ursa", "furbolg"),
    (r"Naga|Siren|Myrmidon|Sea Witch|Hatecrest|Slitherblade|Wrathtail|Spitelash|Tidecaller", "naga"),
    (r"Dark Iron|Shadowforge|Anvilrage|Twilight Emissary", "Dark Iron dwarves"), (r"Scarlet|Crimson", "Scarlet Crusaders"),
    (r"Syndicate", "Syndicate rogues"), (r"Twilight", "Twilight's Hammer cultists"),
    (r"Cult|Shadow Council|Burning Blade|Shadowsworn|Acolyte|Searing Blade|Felsworn|Argus Wake|Shadowmage|Dark Strand|Shadowsilk|Voidwalker Minion", "cultists"),
    (r"Pirate|Bloodsail|Southsea|Blackwater|Buccaneer|Corsair|Swashbuckler|Deckhand|Seadog|Freebooter", "pirates"),
    (r"Bandit|Brigand|Thief|Highwayman|Thug|Outlaw|Marauder|Rogue|Cutthroat|Smuggler|Raider|Poacher|Pillager|Looter|Scavenger", "bandits"),
    (r"Venture", "Venture Company workers"), (r"Grimtotem", "Grimtotem tauren"), (r"Blackrock", "Blackrock orcs"), (r"Dragonmaw", "Dragonmaw orcs"),
    (r"Wastewander", "Wastewander nomads"), (r"Dunemaul|Sandfury", "ogres"), (r"Trogg|Rockjaw|Stonesplinter|Stonevault|Grimlok", "troggs"),
    (r"Leper|Gnome|Dark Iron Gnome", "leper gnomes"), (r"Worgen|Wolfman|Son of Arugal|Moonrage|Nightbane", "worgen"),
    (r"Hillsbrad|Peasant|Farmer|Villager|Miner|Footman|Sentry|Guard|Militia|Watchman", "townsfolk and militia"),
    (r"Goblin|Bruiser|Tinkerer|Sapper|Shredder Operator", "goblins"), (r"Skeleton", "skeletons"),
    (r"Highborne|Night Elf|Elf|Sentinel|Druid of the Fang|Darkweaver", "elves"), (r"Dwarf|Dwarves|Wildhammer", "dwarves"),
    (r"Orc|Grunt|Warsong|Kor'kron|Bleeding Hollow", "orcs"), (r"Tauren|Bloodhoof", "tauren"),
    (r"Mercenary|Deserter|Soldier|Warrior|Archer|Scout|Hunter|Warlord|Captain|Lieutenant|Legionnaire|Knight|Marshal", "soldiers and mercenaries"),
    (r"Mage|Warlock|Priest|Shaman|Conjurer|Geomancer|Shadowcaster|Necromancer|Summoner|Spellbinder|Witch", "spellcasters"),
    (r"Fisherman|Sailor|Dockhand|Pirate", "sailors"), (r"Satyr", "satyrs"),
]
UNDEAD_KW = [
    (r"Ghoul", "ghouls"), (r"Skelet|Bone", "skeletons"), (r"Zombie|Rotting|Decaying|Shambling|Corpse|Rot ", "zombies"),
    (r"Ghost|Spirit|Spectre|Specter|Phantom|Wraith|Shade|Apparition|Haunt|Banshee|Soul", "ghosts and spirits"),
    (r"Gargoyle", "gargoyles"), (r"Abomination|Flesh|Stitched|Patchwork", "abominations"),
    (r"Scourge|Death Knight|Necromancer|Lich|Cultist|Dark Adept|Shadowmage|Plague", "the Scourge"),
    (r"Scarlet", "the Scarlet Crusade's dead"), (r"Dark Iron|Dwarf", "undead dwarves"),
]
DEMON_KW = [
    (r"\bImp\b", "imps"), (r"Felhound|Felstalker|Hound", "felhounds"), (r"Void", "voidwalkers"), (r"Succub", "succubi"),
    (r"Satyr|Legashi|Jadefire|Haldarr|Xavian|Felmusk|Zenn", "satyrs"), (r"Infernal", "infernals"),
    (r"Doomguard|Dreadlord|Felguard|Nathrezim|Pit Lord|Eredar", "greater demons"), (r"Felbeast|Fel ", "fel beasts"),
]
DRAGON_KW = [
    (r"Whelp|Hatchling|Broodling", "whelps"), (r"Drake", "drakes"), (r"Dragonspawn|Scalebane|Flayer|Wyrmkin|Flamewaker|Spawn", "dragonspawn"),
    (r"Wyrm|Dragon", "dragons"),
]
ELEMENTAL_KW = [
    (r"Water|Tide|Wave|Surf|Sea|Aqua|Rain|Ooze\b", "water elementals"),
    (r"Fire|Flame|Blaze|Cinder|Ember|Magma|Lava|Inferno|Burning|Scorch|Searing|Molten|Pyre|Heat", "fire elementals"),
    (r"Earth|Rock|Stone|Shard|Crystal|Geolord|Dust|Grit|Obsidian|Shale|Granite|Boulder", "earth elementals"),
    (r"Air|Wind|Cyclone|Vortex|Storm|Gust|Whirl|Thunder|Sky|Cloud", "air elementals"),
    (r"Ooze|Slime|Jelly|Sludge|Rot|Gloop|Gel", "oozes and slimes"),
    (r"Bog|Fungal|Treant|Ancient|Protector|Mire|Swamp|Root|Thorn", "treants and bog beasts"),
    (r"Golem|Keeper|Shardling", "stone constructs"),
]
GIANT_KW = [(r"Golem", "golems"), (r"Giant|Colossus|Titan", "giants"), (r"Ettin", "ettins"), (r"Stone|Rock|Granite|Mountain", "stone giants"), (r"Sea|Tide|Reef", "sea giants")]
OTHER_KW = [
    (r"Ooze|Slime|Jelly|Sludge|Gloop|Gel|Devourer|Decay", "oozes and slimes"), (r"Silithid|Spider|Wasp|Scarab|Beetle|Insect|Bug|Swarmer|Crawler|Gorishi|Hive|Hazzali|Centipaar|Zukk'ash", "insects"),
    (r"Bloodpetal|Vine|Lasher", "carnivorous plants"), (r"Hydra|Gahz'rilla", "hydras"),
    (r"Treant|Ancient|Tree|Protector|Sapling", "treants"), (r"Sporebat|Spore", "sporebats"), (r"Deviate", "deviate creatures"),
    (r"Yeti|Ape|Gorilla", "beasts"), (r"Elemental|Golem", "elementals"), (r"Tendril|Tentacle|Eye|Horror|Faceless|Shade", "horrors"),
]


def kw_desc(name, table, fallback):
    for pat, desc in table:
        if re.search(pat, name, re.I):
            return desc
    return fallback


def describe_creature(c):
    """Return a plural descriptor for a creature_template row (dict)."""
    t = c["type"]
    name = c["name"] or ""
    if t == 1:
        fam = PET_FAMILY.get(c["pet_family"])
        if fam:
            return fam
        return kw_desc(name, BEAST_KW, "beasts")
    if t == 7:
        return kw_desc(name, HUMANOID_KW, "humanoid foes")
    if t == 6:
        return kw_desc(name, UNDEAD_KW, "the restless dead")
    if t == 3:
        return kw_desc(name, DEMON_KW, "demons")
    if t == 2:
        return kw_desc(name, DRAGON_KW, "dragonkin")
    if t == 4:
        return kw_desc(name, ELEMENTAL_KW, "elementals")
    if t == 5:
        return kw_desc(name, GIANT_KW, "giants")
    if t == 9:
        return "mechanical constructs"
    if t == 8:
        return "critters"
    if t == 11:
        return "totems"
    if t == 10:
        return kw_desc(name, OTHER_KW, "strange creatures")
    return "creatures"


TYPE_GENERIC = {1: "beasts", 7: "humanoid foes", 6: "the restless dead", 3: "demons", 2: "dragonkin",
                4: "elementals", 5: "giants", 9: "mechanical constructs", 8: "critters", 10: "strange creatures"}


def dominant_descriptor(weighted):
    """weighted: list of (creature_row, weight). Pick the descriptor that covers
    most of the weight; fall back to super-groups, then creature type, then
    'a variety of creatures'."""
    total = sum(w for _, w in weighted) or 1.0
    by_desc = Counter()
    by_type = Counter()
    for c, w in weighted:
        by_desc[describe_creature(c)] += w
        by_type[c["type"]] += w
    top2 = by_desc.most_common(2)
    desc, w = top2[0]
    if w / total >= 0.55:
        return desc
    generic = set(TYPE_GENERIC.values()) | {"creatures", "a variety of creatures"}
    if len(top2) == 2:
        second, w2 = top2[1]
        if desc not in generic and second in generic and w / total >= 0.4:
            return desc
        if (w + w2) / total >= 0.75 and desc not in generic and second not in generic \
                and not desc.startswith("the ") and not second.startswith("the "):
            return f"{desc} and {second}"
    winged = sum(v for k, v in by_desc.items() if k in WINGED)
    if winged / total >= 0.55:
        return "winged creatures"
    crawl = sum(v for k, v in by_desc.items() if k in CRAWLING)
    if crawl / total >= 0.55:
        return "crawling vermin"
    t, tw = by_type.most_common(1)[0]
    if tw / total >= 0.55:
        return TYPE_GENERIC.get(t, "creatures")
    return "a variety of creatures"


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------
def zone_phrase_name(name):
    if name.startswith("The "):
        return "the " + name[4:]
    return name


def join_names(names):
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return names[0] + " and " + names[1]
    return ", ".join(names[:-1]) + " and " + names[-1]


# ---------------------------------------------------------------------------
# Where within a zone: compass direction from the weighted spread of spawn points
# (zone-map percentages), never a guess.
# ---------------------------------------------------------------------------
DIR_ADJ = {(-1, -1): "north-western", (0, -1): "northern", (1, -1): "north-eastern",
           (-1, 0): "western", (0, 0): "central", (1, 0): "eastern",
           (-1, 1): "south-western", (0, 1): "southern", (1, 1): "south-eastern"}
DIR_NOUN = {"north-western": "north-west", "northern": "north", "north-eastern": "north-east",
            "western": "west", "central": "centre", "eastern": "east",
            "south-western": "south-west", "southern": "south", "south-eastern": "south-east"}


def spawn_focus(points):
    """points: [(x, y, weight)] on a zone map (0-100). Returns (cx, cy, spread, adj):
    the weighted centre, the weighted spread (root of summed variances) and a
    compass adjective, or None for adj when the sources cover the whole zone."""
    total = sum(p[2] for p in points)
    if not points or total <= 0:
        return None
    cx = sum(p[0] * p[2] for p in points) / total
    cy = sum(p[1] * p[2] for p in points) / total
    var = sum(((p[0] - cx) ** 2 + (p[1] - cy) ** 2) * p[2] for p in points) / total
    spread = var ** 0.5
    dx = -1 if cx < 38 else (1 if cx > 62 else 0)
    dy = -1 if cy < 38 else (1 if cy > 62 else 0)
    adj = DIR_ADJ[(dx, dy)]
    if spread > 20 or (adj == "central" and spread > 13):
        adj = None
    return cx, cy, spread, adj


def focus_for_creatures(w, entries, zone):
    """entries: [(npc, chance, quest)] -> spawn_focus over their spawns in zone."""
    pts = []
    for npc, ch, _ in entries:
        for x, y in w.unit_pts.get(npc, {}).get(zone, ()):
            pts.append((x, y, ch))
    return spawn_focus(pts)


def focus_for_objects(w, entries, zone):
    pts = []
    for go, ch, _ in entries:
        for x, y in w.obj_pts.get(go, {}).get(zone, ()):
            pts.append((x, y, ch))
    return spawn_focus(pts)


def focus_for_units(w, npcs, zone):
    pts = []
    for npc in npcs:
        for x, y in w.unit_pts.get(npc, {}).get(zone, ()):
            pts.append((x, y, 1.0))
    return spawn_focus(pts)


# per-item accumulator of map marks: zone id -> (cx, cy, spread); reset by render_item
_MARKS = {}


def note_focus(zone, focus):
    if zone is not None and focus:
        _MARKS[zone] = (focus[0], focus[1], focus[2])
    return focus[3] if focus else None


def chance_adverb(ch):
    if ch >= 40:
        return "Commonly carried by"
    if ch >= 12:
        return "Often found on"
    if ch >= 3:
        return "Sometimes found on"
    if ch >= 0.5:
        return "A rare find on"
    return "A very rare find on"


def lua_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def plural_vendor(subname):
    """'Leather Armor Merchant' -> 'leather armor merchants'"""
    s = (subname or "").strip()
    if not s:
        return "merchants"
    low = s.lower()
    if low in ("innkeeper",):
        return "innkeepers"
    if "darkmoon" in low:
        return "Darkmoon Faire vendors"
    if re.search(r"general (goods|supplies|trade)|trade (goods|supplies|supplier)|tradesman|general trade", low):
        return "general goods merchants"
    if low.endswith(" goods"):
        return low + " vendors"
    if "quartermaster" in low:
        return "quartermasters"
    if re.search(r"food|drink|butcher|baker|bartender|barmaid|cook\b|fruit|fish vendor|meat|bread|mushroom|fungus|waitress|tavern|brew|wine|ale", low) and "supplies" not in low and "supplier" not in low:
        return "food and drink vendors"
    if "reagent" in low:
        return "reagent vendors"
    m = re.match(r"(.*?)\s*(supplies|supplier|supply)$", low)
    if m:
        return m.group(1) + " suppliers"
    m = re.match(r"(.*?)\s*(vendor|merchant|dealer|seller|trainer|smith|wright|crafter|maker|master|keeper|breeder|monger|farmer)$", low)
    if m:
        word = m.group(2)
        return (m.group(1) + " " + word + "s").strip()
    if low.endswith("s"):
        return low
    return low + "s"


def singular_vendor(plural):
    if plural.endswith("ies"):
        return "a " + plural[:-3] + "y"
    if plural == "merchants":
        return "a merchant"
    if plural.endswith("s") and not plural.endswith("ss"):
        p = plural[:-1]
        return ("an " if p[0] in "aeiou" else "a ") + p
    return plural


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
class World:
    def __init__(self, mangos_path, pf_dir):
        self.c = sqlite3.connect(mangos_path)
        self.c.row_factory = sqlite3.Row
        self.pf_dir = pf_dir
        self.load_zones()
        self.load_templates()
        self.load_spawns()
        self.load_loot()
        self.load_vendors()
        self.load_crafting()
        self.load_quests()
        self.load_uses()
        self.load_misc()

    def q(self, sql, *a):
        return self.c.execute(sql, a).fetchall()

    # -- zones ------------------------------------------------------------
    def load_zones(self):
        self.area_parent = {}
        self.zone_name = {}
        self.zone_team = {}
        self.area_name = {}
        for r in self.q("select entry, map_id, zone_id, name, team from area_template"):
            self.area_name[r["entry"]] = r["name"]
            if r["zone_id"] == 0 or r["entry"] in DUNGEON_ZONES:
                self.zone_name[r["entry"]] = r["name"]
                self.zone_team[r["entry"]] = r["team"]
            else:
                self.area_parent[r["entry"]] = r["zone_id"]
        self.zone_fac = {}
        for z in self.zone_name:
            if z in DUNGEON_ZONES:
                f = None
            elif z in ALLIANCE_ZONES or self.zone_team.get(z) == 2:
                f = "A"
            elif z in HORDE_ZONES or self.zone_team.get(z) == 4:
                f = "H"
            else:
                f = None
            if z in DUNGEON_ZONES:
                f = None
            self.zone_fac[z] = f

    def zone_of(self, area):
        area = int(area)
        for _ in range(4):
            if area in self.zone_name:
                return area
            if area in self.area_parent:
                area = self.area_parent[area]
            else:
                return None
        return None

    def zone_allowed(self, zone, fac):
        if zone in BATTLEGROUND_ZONES:
            return False
        zf = self.zone_fac.get(zone)
        return zf is None or zf == fac

    def zone_display(self, zone, adj=None):
        """'Westfall' / 'northern Westfall' / 'the northern Barrens'."""
        name = self.zone_name.get(zone, "parts unknown")
        if adj and zone not in DUNGEON_ZONES and zone not in CITY_ZONES:
            if name.startswith("The "):
                return f"the {adj} {name[4:]}"
            return f"{adj} {name}"
        return zone_phrase_name(name)

    def zones_phrase(self, zones, prep="in", dirs=None):
        """zones: ordered list of zone ids; dirs: {zone: compass adjective}."""
        dirs = dirs or {}
        names = [self.zone_display(z, dirs.get(z)) for z in zones]
        if len(zones) == 1 and zones[0] in DUNGEON_ZONES:
            prep = "within"
        return prep + " " + join_names(names)

    # -- templates --------------------------------------------------------
    def load_templates(self):
        self.items = {}
        for r in self.q("select * from item_template t where patch=(select max(patch) from item_template where entry=t.entry)"):
            self.items[r["entry"]] = dict(r)
        self.creatures = {}
        for r in self.q("select * from creature_template t where patch=(select max(patch) from creature_template where entry=t.entry)"):
            if TEST_NAME_RE.search(r["name"] or ""):
                continue
            self.creatures[r["entry"]] = dict(r)
        self.gobjs = {}
        for r in self.q("select * from gameobject_template t where patch=(select max(patch) from gameobject_template where entry=t.entry)"):
            if TEST_NAME_RE.search(r["name"] or ""):
                continue
            self.gobjs[r["entry"]] = dict(r)

    # -- spawns -----------------------------------------------------------
    def load_spawns(self):
        pf_units = load_pf_table(os.path.join(self.pf_dir, "units.lua"))
        pf_objects = load_pf_table(os.path.join(self.pf_dir, "objects.lua"))
        self.unit_fac = {}
        self.unit_zones = defaultdict(Counter)   # entry -> Counter(zone -> spawns)
        self.unit_pts = defaultdict(lambda: defaultdict(list))   # entry -> zone -> [(x, y)]
        for entry, u in pf_units.items():
            if not isinstance(entry, int):
                continue
            fac = u.get("fac")
            if fac:
                self.unit_fac[entry] = fac
            for _, co in (u.get("coords") or {}).items():
                z = self.zone_of(co[3]) if len(co) >= 3 else None
                self.unit_zones[entry][z] += 1
                if z is not None and isinstance(co.get(1), (int, float)) and isinstance(co.get(2), (int, float)):
                    self.unit_pts[entry][z].append((float(co[1]), float(co[2])))
        self.obj_zones = defaultdict(Counter)
        self.obj_pts = defaultdict(lambda: defaultdict(list))
        for entry, o in pf_objects.items():
            if not isinstance(entry, int):
                continue
            for _, co in (o.get("coords") or {}).items():
                z = self.zone_of(co[3]) if len(co) >= 3 else None
                self.obj_zones[entry][z] += 1
                if z is not None and isinstance(co.get(1), (int, float)) and isinstance(co.get(2), (int, float)):
                    self.obj_pts[entry][z].append((float(co[1]), float(co[2])))
        # instance spawns from vmangos (pfQuest has no instance coordinates)
        for r in self.q("select id,id2,id3,id4,id5,map from creature where map not in (0,1) and patch_max>=10"):
            if r["map"] in BATTLEGROUND_MAPS:
                continue
            z = MAP_TO_ZONE.get(r["map"])
            ids = [i for i in (r["id"], r["id2"], r["id3"], r["id4"], r["id5"]) if i]
            for i in ids:
                self.unit_zones[i][z] += 1.0 / len(ids)
        for r in self.q("select id,map from gameobject where map not in (0,1) and patch_max>=10"):
            if r["map"] in BATTLEGROUND_MAPS:
                continue
            self.obj_zones[r["id"]][MAP_TO_ZONE.get(r["map"])] += 1
        for entry, zone in BOSS_ZONE_OVERRIDE.items():
            known = self.unit_zones.get(entry)
            if not known or set(known) <= {None}:
                self.unit_zones[entry] = Counter({zone: 1})
        # creatures spawned in the world but missing from pfQuest -> unknown zone
        world_spawned = Counter()
        for r in self.q("select id,count(*) n from creature where map in (0,1) and patch_max>=10 group by id"):
            world_spawned[r["id"]] = r["n"]
        for entry, n in world_spawned.items():
            if not self.unit_zones.get(entry):
                self.unit_zones[entry][None] += n

    # -- loot -------------------------------------------------------------
    def _load_loot_table(self, table):
        d = defaultdict(list)
        for r in self.q(f"select entry,item,ChanceOrQuestChance ch,groupid,mincountOrRef mref,maxcount from {table} where patch_max>=10"):
            d[r["entry"]].append((r["item"], r["ch"], r["groupid"], r["mref"], r["maxcount"]))
        return d

    def load_loot(self):
        self.ref_loot = self._load_loot_table("reference_loot_template")
        self.loot = {
            "creature": self._load_loot_table("creature_loot_template"),
            "gameobject": self._load_loot_table("gameobject_loot_template"),
            "skinning": self._load_loot_table("skinning_loot_template"),
            "pickpocketing": self._load_loot_table("pickpocketing_loot_template"),
            "item": self._load_loot_table("item_loot_template"),
            "fishing": self._load_loot_table("fishing_loot_template"),
            "disenchant": self._load_loot_table("disenchant_loot_template"),
        }
        self._ref_cache = {}

    def resolve(self, rows, depth=0):
        """rows -> {item: (chance_percent, is_quest_drop)} with references and
        equal-chance groups resolved (approximately, as the server does)."""
        out = {}
        # group bookkeeping for zero-chance rows
        group_explicit = Counter()
        group_zero = Counter()
        for item, ch, grp, mref, maxc in rows:
            if grp:
                if ch == 0:
                    group_zero[grp] += 1
                else:
                    group_explicit[grp] += abs(ch)
        for item, ch, grp, mref, maxc in rows:
            quest = ch < 0
            c = abs(ch)
            if c == 0:
                if grp and group_zero[grp]:
                    c = max(0.0, 100.0 - group_explicit[grp]) / group_zero[grp]
                else:
                    c = 100.0
            if mref < 0:
                ref = -mref
                if depth > 3:
                    continue
                sub = self._ref_cache.get(ref)
                if sub is None:
                    sub = self.resolve(self.ref_loot.get(ref, []), depth + 1)
                    self._ref_cache[ref] = sub
                rolls = max(1, maxc or 1)
                for sitem, (sch, squest) in sub.items():
                    eff = min(100.0, c / 100.0 * sch * rolls)
                    prev = out.get(sitem)
                    if not prev or eff > prev[0]:
                        out[sitem] = (eff, squest or quest)
            else:
                prev = out.get(item)
                if not prev or c > prev[0]:
                    out[item] = (c, quest)
        return out

    # -- vendors ----------------------------------------------------------
    def load_vendors(self):
        self.vendors = defaultdict(dict)  # item -> {npc: maxcount}
        for r in self.q("select entry,item,maxcount from npc_vendor"):
            if r["entry"] in self.creatures:
                self.vendors[r["item"]][r["entry"]] = r["maxcount"]
        tmpl = defaultdict(list)
        for r in self.q("select entry,item,maxcount from npc_vendor_template"):
            tmpl[r["entry"]].append((r["item"], r["maxcount"]))
        for entry, c in self.creatures.items():
            vid = c.get("vendor_id") or 0
            for item, maxc in tmpl.get(vid, []):
                self.vendors[item][entry] = maxc

    # -- crafting ---------------------------------------------------------
    def load_crafting(self):
        self.spell_name = {}
        self.spell_creates = defaultdict(set)  # spell -> items
        self.spell_family = {}
        self.spell_learns = defaultdict(set)
        for r in self.q("""select entry, name, spellFamilyName fam, effect1,effect2,effect3,
                                  effectItemType1 i1, effectItemType2 i2, effectItemType3 i3,
                                  effectTriggerSpell1 t1, effectTriggerSpell2 t2, effectTriggerSpell3 t3
                           from spell_template t where build=(select max(build) from spell_template where entry=t.entry)"""):
            self.spell_name[r["entry"]] = r["name"]
            self.spell_family[r["entry"]] = r["fam"]
            for e, it, tr in ((r["effect1"], r["i1"], r["t1"]), (r["effect2"], r["i2"], r["t2"]), (r["effect3"], r["i3"], r["t3"])):
                if e == 24 and it:
                    self.spell_creates[r["entry"]].add(it)
                if e == 36 and tr:
                    self.spell_learns[r["entry"]].add(tr)
        self.spell_skill = {}  # spell -> (skill, minvalue)
        for tbl in ("npc_trainer", "npc_trainer_template"):
            for r in self.q(f"select spell, reqskill, reqskillvalue from {tbl} where reqskill>0"):
                for craft in (self.spell_learns.get(r["spell"]) or {r["spell"]}):
                    cur = self.spell_skill.get(craft)
                    if not cur or r["reqskillvalue"] < cur[1]:
                        self.spell_skill[craft] = (r["reqskill"], r["reqskillvalue"])
        for it in self.items.values():
            if it["class"] == 9:
                skill = RECIPE_SUBCLASS_SKILL.get(it["subclass"]) or it["required_skill"]
                if not skill:
                    continue
                for sid in (it["spellid_1"], it["spellid_2"], it["spellid_3"]):
                    for craft in self.spell_learns.get(sid, ()):
                        if craft not in self.spell_skill:
                            self.spell_skill[craft] = (skill, it["required_skill_rank"])
        self.crafted = defaultdict(list)  # item -> [(spell, skill, value)]
        for spell, items in self.spell_creates.items():
            sk = self.spell_skill.get(spell)
            for item in items:
                self.crafted[item].append((spell, sk[0] if sk else None, sk[1] if sk else None))

    # -- quests -----------------------------------------------------------
    def load_quests(self):
        self.quest_rewards = defaultdict(list)  # item -> [(quest, zone, facmask)]
        cols = ",".join(f"RewChoiceItemId{i}" for i in range(1, 7)) + "," + ",".join(f"RewItemId{i}" for i in range(1, 5))
        for r in self.q(f"select entry, ZoneOrSort, RequiredRaces, {cols} from quest_template t where patch=(select max(patch) from quest_template where entry=t.entry)"):
            races = r["RequiredRaces"] or 0
            fac = None
            if races and not races & 178:
                fac = "A"
            elif races and not races & 77:
                fac = "H"
            zone = self.zone_of(r["ZoneOrSort"]) if (r["ZoneOrSort"] or 0) > 0 else None
            for k in r.keys():
                if k.startswith("Rew") and r[k]:
                    self.quest_rewards[r[k]].append((r["entry"], zone, fac))

    # -- uses: what an item is for ---------------------------------------
    def load_uses(self):
        self.reagent_skills = defaultdict(set)   # item -> set(skill)
        for r in self.q("""select entry, reagent1,reagent2,reagent3,reagent4,reagent5,reagent6,reagent7,reagent8
                           from spell_template t where build=(select max(build) from spell_template where entry=t.entry)"""):
            sk = self.spell_skill.get(r["entry"])
            if not sk or sk[0] not in SKILL_PHRASE:
                continue
            for k in r.keys():
                if k.startswith("reagent") and r[k]:
                    self.reagent_skills[r[k]].add(sk[0])
        self.quest_wants = defaultdict(list)     # item -> [(zone, fac)]
        for r in self.q("""select ZoneOrSort, RequiredRaces, ReqItemId1,ReqItemId2,ReqItemId3,ReqItemId4
                           from quest_template t where patch=(select max(patch) from quest_template where entry=t.entry)"""):
            races = r["RequiredRaces"] or 0
            fac = None
            if races and not races & 178:
                fac = "A"
            elif races and not races & 77:
                fac = "H"
            zone = self.zone_of(r["ZoneOrSort"]) if (r["ZoneOrSort"] or 0) > 0 else None
            for k in ("ReqItemId1", "ReqItemId2", "ReqItemId3", "ReqItemId4"):
                if r[k]:
                    self.quest_wants[r[k]].append((zone, fac))

    # -- misc -------------------------------------------------------------
    def load_misc(self):
        self.start_items = set(r["itemid"] for r in self.q("select itemid from playercreateinfo_item"))
        self.disenchant_source = defaultdict(list)  # disenchant_id -> [(quality, ilvl)]
        for it in self.items.values():
            if it["disenchant_id"]:
                self.disenchant_source[it["disenchant_id"]].append((it["quality"], it["item_level"]))


# ---------------------------------------------------------------------------
# Source collection
# ---------------------------------------------------------------------------
def collect_sources(w):
    src = defaultdict(lambda: defaultdict(list))

    def add(item, kind, val):
        src[item][kind].append(val)

    # creature loot / skinning / pickpocketing
    for entry, c in w.creatures.items():
        for kind, idcol in (("drop", "loot_id"), ("skin", "skinning_loot_id"), ("pick", "pickpocket_loot_id")):
            lid = c.get(idcol) or 0
            if not lid:
                continue
            tbl = {"drop": "creature", "skin": "skinning", "pick": "pickpocketing"}[kind]
            rows = w.loot[tbl].get(lid)
            if not rows:
                continue
            for item, (ch, quest) in w.resolve(rows).items():
                add(item, kind, (entry, ch, quest))
    # gameobjects (chests, herbs, veins)
    for entry, g in w.gobjs.items():
        if g["type"] not in (3, 25):
            continue
        lid = g["data1"] if g["type"] == 3 else g["data1"]
        rows = w.loot["gameobject"].get(lid) if lid else None
        if not rows:
            continue
        for item, (ch, quest) in w.resolve(rows).items():
            add(item, "object", (entry, ch, quest))
    # fishing (entry = area id)
    for area, rows in w.loot["fishing"].items():
        z = w.zone_of(area)
        for item, (ch, quest) in w.resolve(rows).items():
            add(item, "fish", (z, ch, area))
    # containers
    for cont, rows in w.loot["item"].items():
        if cont not in w.items:
            continue
        for item, (ch, quest) in w.resolve(rows).items():
            add(item, "container", (cont, ch))
    # disenchant
    for did, rows in w.loot["disenchant"].items():
        for item, (ch, quest) in w.resolve(rows).items():
            add(item, "disenchant", did)
    for item, vendors in w.vendors.items():
        for npc, maxc in vendors.items():
            add(item, "vendor", (npc, maxc))
    for item, lst in w.crafted.items():
        for v in lst:
            add(item, "craft", v)
    for item, lst in w.quest_rewards.items():
        for v in lst:
            add(item, "quest", v)
    for item in w.start_items:
        add(item, "start", True)
    return src


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
OTHER = {"A": "Horde", "H": "Alliance"}
FACTION_NAME = {"A": "Alliance", "H": "Horde"}


def top_zones(scores, allowed, keep_ratio=0.4, max_n=2):
    ranked = sorted(((s, z) for z, s in scores.items() if z is not None and allowed(z) and s > 0), reverse=True)
    if not ranked:
        return []
    top = ranked[0][0]
    out = [ranked[0][1]]
    for s, z in ranked[1:max_n]:
        if s >= top * keep_ratio:
            out.append(z)
    return out


def level_band(w, weighted, share=None):
    """Weighted 10th-90th percentile of creature levels, so one heavily
    weighted creature does not define the whole band."""
    rows = [(c["level_min"] or 0, c["level_max"] or 0, x) for c, x in weighted if (c["level_max"] or 0) > 0 and x > 0]
    if not rows:
        return ""
    total = sum(x for _, _, x in rows)
    lo = hi = None
    acc = 0.0
    for lmin, lmax, x in sorted(rows, key=lambda r: r[0]):
        acc += x
        if lo is None and acc >= total * 0.10:
            lo = lmin
    acc = 0.0
    for lmin, lmax, x in sorted(rows, key=lambda r: r[1]):
        acc += x
        if hi is None and acc >= total * 0.90:
            hi = lmax
    if lo is None or hi is None:
        return ""
    if hi < lo:
        lo, hi = hi, lo
    return f"level {lo}" if lo == hi else f"levels {lo}-{hi}"


def render_creature_line(w, entries, fac, verb_mode="drop"):
    """entries: [(npc_entry, chance, quest)] -> (sentence, strength) or None.
    strength ranks lines against each other; higher = more useful."""
    zone_score = Counter()
    per_creature = {}
    for npc, ch, quest in entries:
        c = w.creatures.get(npc)
        if not c:
            continue
        if c["type"] == 8 and (verb_mode != "drop" or ch < 1):
            continue
        zones = w.unit_zones.get(npc) or Counter({None: 0.5})
        per_creature[npc] = (c, ch, quest, zones)
        for z, n in zones.items():
            zone_score[z] += n * ch
    if not per_creature:
        return None
    n_creatures = len(per_creature)
    max_chance_all = max(v[1] for v in per_creature.values())
    weighted_all = [(v[0], sum(v[3].values()) * v[1]) for v in per_creature.values()]

    zones = top_zones(zone_score, lambda z: w.zone_allowed(z, fac))
    any_zone = any(z is not None for z in zone_score)
    opposing_only = any_zone and not zones

    # creatures living in zones this faction can reasonably visit
    allowed_weighted = []
    for c, ch, quest, zc in per_creature.values():
        n = sum(v for z, v in zc.items() if z is not None and w.zone_allowed(z, fac))
        if n > 0:
            allowed_weighted.append((c, n * ch))
    if zones:
        zset = set(zones)
        weighted = []
        for c, ch, quest, zc in per_creature.values():
            n = sum(v for z, v in zc.items() if z in zset)
            if n > 0:
                weighted.append((c, n * ch))
        in_zone = [(c, ch, q) for c, ch, q, zc in per_creature.values() if any(z in zset for z in zc)]
        max_chance = max(ch for c, ch, q in in_zone)
        quest_only = all(q for c, ch, q in in_zone)
    else:
        weighted = weighted_all
        max_chance = max_chance_all
        quest_only = all(v[2] for v in per_creature.values())

    desc = dominant_descriptor(weighted)
    total_w = sum(x for _, x in weighted) or 1
    boss_share = sum(x for c, x in weighted if (c["rank"] or 0) == 3) / total_w
    rare_share = sum(x for c, x in weighted if (c["rank"] or 0) == 2) / total_w
    in_dungeon = bool(zones) and all(z in DUNGEON_ZONES for z in zones)
    in_raid = bool(zones) and all(z in RAID_ZONES for z in zones)

    allowed_scores = {z: s for z, s in zone_score.items() if z is not None and w.zone_allowed(z, fac)}
    top_s = max(allowed_scores.values()) if allowed_scores else 0
    spread = sum(1 for s in allowed_scores.values() if s >= top_s * 0.1) if top_s else 0

    def chance_strength(ch):
        if ch >= 40:
            return 80
        if ch >= 12:
            return 70
        if ch >= 3:
            return 55
        if ch >= 0.5:
            return 35
        return 20

    dirs = {}
    for z in zones:
        if z not in DUNGEON_ZONES:
            dirs[z] = note_focus(z, focus_for_creatures(w, [(n, v[1], v[2]) for n, v in per_creature.items()], z))
    names = join_names([w.zone_display(z, dirs.get(z)) for z in zones]) if zones else ""

    if verb_mode == "skin":
        t = Counter(c["type"] for c, _ in weighted).most_common(1)[0][0]
        verb = "Skinned from" if t == 1 else "Salvaged from the remains of"
        band = level_band(w, allowed_weighted or weighted)
        band_txt = f" of {band}" if band and spread >= 3 else ""
        if zones:
            where = " " + w.zones_phrase(zones, "in", dirs)
        elif opposing_only:
            where = f" in {OTHER[fac]} territory"
        else:
            where = ""
        strength = 75 if max_chance >= 5 else 25
        if opposing_only:
            strength -= 15
        return (f"{verb} {desc}{band_txt}{where}.", strength)
    if verb_mode == "pick":
        if zones:
            where = " " + w.zones_phrase(zones, "in", dirs)
        elif opposing_only:
            where = f" in {OTHER[fac]} territory"
        else:
            where = ""
        return (f"Lifted from the pockets of {desc}{where}.", 45 if max_chance >= 10 else 20)

    # creature drops
    if in_raid and boss_share >= 0.6:
        return (f"Won from the great foes within {names}.", 88)
    if in_dungeon and boss_share >= 0.6:
        return (f"Guarded by a master of {names}.", 85)
    if in_dungeon:
        adv = chance_adverb(max_chance)
        who = f"the {desc}" if not desc.startswith(("the ", "a ")) else desc
        return (f"{adv} {who} of {names}.", chance_strength(max_chance) + 5)
    if zones and rare_share >= 0.6:
        return (f"Carried by a rare creature that roams {names}.", 55)
    if zones and boss_share >= 0.6:
        return (f"Held by a mighty foe of {names}.", 60)
    if n_creatures >= 40 and max_chance_all < 0.6:
        band = level_band(w, weighted_all, share=0.0)
        return (f"A rare world drop from creatures of {band}." if band else "A rare world drop.", 30)
    adv = chance_adverb(max_chance)
    strength = chance_strength(max_chance)
    if quest_only:
        adv = "While on a quest, taken from"
        strength -= 10
    if zones:
        if spread >= 4:
            band = level_band(w, allowed_weighted or weighted_all)
            band_txt = f" of {band}" if band else ""
            return (f"{adv} {desc}{band_txt}, most plentifully in {names}.", strength)
        return (f"{adv} {desc} of {names}.", strength)
    if opposing_only:
        return (f"{adv} {desc} in {OTHER[fac]} territory.", strength - 15)
    return (f"{adv} {desc}.", strength - 5)


def render_vendor_line(w, item, entries, fac):
    it = w.items.get(item) or {}
    sellers = {}
    for npc, maxc in entries:
        if npc not in w.creatures:
            continue
        sellers[npc] = (w.unit_fac.get(npc, "AH"), maxc)
    mine = {npc: v for npc, v in sellers.items() if fac in v[0]}
    if not mine:
        if sellers:
            return (f"Sold only by {OTHER[fac]} merchants.", 30)
        return None
    if it.get("required_reputation_faction"):
        return ("Sold by a quartermaster to those of sufficient standing with their faction.", 75)
    cats = Counter()
    zone_count = Counter()
    limited = False
    for npc, (f, maxc) in mine.items():
        c = w.creatures.get(npc) or {}
        cats[plural_vendor(c.get("subname"))] += 1
        if maxc:
            limited = True
        for z, n in (w.unit_zones.get(npc) or {}).items():
            if z is not None and z not in BATTLEGROUND_ZONES:
                zone_count[z] += 1
    top = cats.most_common(2)
    cat, catn = top[0]
    if catn / len(mine) < 0.4:
        if len(top) == 2 and (catn + top[1][1]) / len(mine) >= 0.6:
            cat = f"{cat} and {top[1][0]}"
        else:
            cat = "merchants"
    zones = [z for _, z in sorted(((n, z) for z, n in zone_count.items()), reverse=True)]
    n = len(mine)
    dirs = {}
    if n <= 6:
        for z in zones[:2]:
            sellers_here = [npc for npc in mine if z in (w.unit_zones.get(npc) or {})]
            dirs[z] = note_focus(z, focus_for_units(w, sellers_here, z))
    if n == 1:
        where = (" " + w.zones_phrase(zones[:1], "in", dirs)) if zones else ""
        line = f"Sold by {singular_vendor(cat)}{where}"
        strength = 80
    elif n >= 8 and len(zones) >= 5:
        line = f"Sold by {cat} in most settlements"
        strength = 100
    else:
        strength = 95
        if len(zones) > 2:
            line = f"Sold by {cat} in {', '.join(w.zone_display(z, dirs.get(z)) for z in zones[:2])} and elsewhere"
        elif zones:
            line = f"Sold by {cat} {w.zones_phrase(zones, 'in', dirs)}"
        else:
            line = f"Sold by {cat}"
    if limited:
        line += " (limited stock)"
        strength -= 25
    return (line + ".", strength)


def render_object_lines(w, item, entries, fac):
    """Return dict kind -> (line, strength) for herbs/mines/chests/other objects."""
    groups = defaultdict(list)
    for go, ch, quest in entries:
        g = w.gobjs.get(go)
        if not g:
            continue
        name = g["name"] or ""
        if name in HERB_NAMES:
            groups["herb"].append((go, ch, name))
        elif MINE_RE.search(name):
            groups["mine"].append((go, ch, name))
        elif CHEST_RE.search(name):
            groups["chest"].append((go, ch, name))
        else:
            groups["other"].append((go, ch, name))
    out = {}
    itname = (w.items.get(item) or {}).get("name", "")
    for kind, lst in groups.items():
        zone_score = Counter()
        name_score = Counter()
        max_ch = 0
        for go, ch, name in lst:
            spawns = w.obj_zones.get(go) or Counter({None: 0.5})
            for z, n in spawns.items():
                zone_score[z] += n * ch
            name_score[name] += sum(spawns.values()) * ch
            max_ch = max(max_ch, ch)
        zones = top_zones(zone_score, lambda z: w.zone_allowed(z, fac))
        allowed_scores = {z: s for z, s in zone_score.items() if z is not None and w.zone_allowed(z, fac)}
        top_s = max(allowed_scores.values()) if allowed_scores else 0
        spread = sum(1 for s in allowed_scores.values() if s >= top_s * 0.1) if top_s else 0
        dirs = {}
        for z in zones:
            if z not in DUNGEON_ZONES:
                dirs[z] = note_focus(z, focus_for_objects(w, [(go, ch, None) for go, ch, _ in lst], z))
        where = (" " + w.zones_phrase(zones, "in", dirs)) if zones else ""
        names, seen = [], set()
        for n, _ in name_score.most_common():
            key = re.sub(r"[^a-z]", "", n.lower())
            if key not in seen:
                seen.add(key)
                names.append(n)
            if len(names) == 2:
                break
        if kind == "herb":
            if itname in names or itname in HERB_NAMES:
                line = f"Harvested by herbalists{where}" if spread < 5 else f"Harvested by herbalists across Azeroth, most plentifully{where}"
            else:
                line = f"Gathered by herbalists alongside {join_names(names)}{where}"
            strength = 85 if max_ch >= 5 else 25
        elif kind == "mine":
            veins = join_names(sorted({re.sub(r"^(Ooze Covered|Small|Rich|Lesser|Greater|Hakkari) ", "", n).lower() + ("" if n.lower().endswith("s") else "s") for n in names}))
            line = f"Mined from {veins}{where}" if spread < 5 else f"Mined from {veins} across Azeroth, most plentifully{where}"
            strength = 85 if max_ch >= 5 else 25
        elif kind == "chest":
            line = f"Found in chests and caches{where}"
            strength = 40 if max_ch >= 5 else 12
        else:
            line = f"Taken from {join_names(names)}{where}" if names else f"Found{where}"
            strength = 50 if max_ch >= 20 else 12
        out[kind] = (line.replace("  ", " ").strip() + ".", strength)
    return out


def water_name(w, area, zone):
    """'Lake Everstill in Redridge Mountains' when the fishing table is keyed by a
    named sub-area of the zone, else None."""
    if area == zone or area not in w.area_name:
        return None
    name = w.area_name[area]
    if not name or name == w.zone_name.get(zone):
        return None
    return f"{zone_phrase_name(name)} in {w.zone_display(zone)}"


def render_fish_line(w, entries, fac):
    zone_score = Counter()
    area_best = {}   # zone -> (chance, area)
    for z, ch, area in entries:
        if z is not None:
            zone_score[z] = max(zone_score[z], ch)
            if ch >= area_best.get(z, (0, None))[0]:
                area_best[z] = (ch, area)
    zones = top_zones(zone_score, lambda z: w.zone_allowed(z, fac), keep_ratio=0.6)
    n_allowed = sum(1 for z in zone_score if w.zone_allowed(z, fac))
    max_ch = max((zone_score[z] for z in zones), default=max(zone_score.values(), default=0))
    strength = 72 if max_ch >= 5 else (30 if max_ch >= 1 else 8)
    if not zones:
        if zone_score:
            return (f"Fished from waters in {OTHER[fac]} territory.", strength - 15)
        return ("Fished from the waters of Azeroth.", strength - 5)
    names = []
    for z in zones:
        wn = water_name(w, area_best[z][1], z)
        names.append(wn or w.zone_display(z))
    names = join_names(names)
    if n_allowed >= 8:
        return (f"Fished from waters across Azeroth, most readily from {names}.", strength)
    return (f"Fished from {names}.", strength)


def with_article(name):
    low = name.lower()
    if low.endswith("s") and not low.endswith("ss"):
        return name
    if low.startswith(("a ", "an ", "the ")):
        return name
    return ("an " if low[0] in "aeiou" else "a ") + name


def render_container_line(w, entries):
    names = Counter()
    max_ch = 0
    for cont, ch in entries:
        names[(w.items.get(cont) or {}).get("name", "container")] += ch
        max_ch = max(max_ch, ch)
    top = [n for n, _ in names.most_common(2)]
    strength = 50 if max_ch >= 10 else (30 if max_ch >= 1 else 12)
    if len(names) == 1:
        return (f"Found inside {with_article(top[0])}.", strength)
    return (f"Found inside containers such as {join_names(top)}.", strength)


# name-based fallbacks for recipes that are learned automatically with the
# profession and therefore never appear in trainer or recipe-item data
CRAFT_NAME_HINTS = [
    (r"^Smelt ", 186), (r"Essence$|Dust$|Shard$", 333),
    (r"Potion|Elixir|Oil$|Flask", 171), (r"Powder|Shot$|Bullet|Bomb|Grenade|Dynamite|Gear|Scope|Goggles|Gyro|Blasting|Charge$", 202),
    (r"Bandage", 129), (r"Bolt of|Linen|Woolen|Silk|Mageweave|Runecloth|Cloak|Robe|Shirt|Tunic|Pants|Bracers$|Gloves$|Hat$|Boots$|Belt$", 197),
    (r"Leather|Hide|Armor Kit|Cured|Hides", 165), (r"Bread|Meat|Egg|Fish|Spice|Stew|Soup|Roast|Cooked|Baked|Crab Cake|Omelet|Clam|Snapper|Trout|Mackerel|Longjaw|Brilliant|Spotted|Rockscale|Kebab|Jerky|Cake|Pie|Chops|Steak", 185),
    (r"Copper|Bronze|Iron|Steel|Mithril|Thorium|Sharpening Stone|Grinding Stone|Weightstone|Rod$|Chain|Plate|Shield$|Axe$|Sword$|Mace$|Dagger$|Hammer$", 164),
]
CRAFT_SKIP_RE = re.compile(r"DND|Create|Summon|Quest|Reward|Conjure|Copy of|Sample|Destroy|Receive|Signing|Deputize|Collect|Draw|Prize|Punctured|Talisman|Signet|Mark of Honor|Light Torch|Repair", re.I)


def render_craft_line(w, entries):
    best = None
    for spell, skill, val in entries:
        if skill in SKILL_PHRASE:
            if not best or (val or 0) < (best[2] or 0):
                best = (spell, skill, val)
    if not best:
        for spell, skill, val in entries:
            name = w.spell_name.get(spell) or ""
            if CRAFT_SKIP_RE.search(name):
                continue
            for pat, sk in CRAFT_NAME_HINTS:
                if re.search(pat, name, re.I):
                    best = (spell, sk, None)
                    break
            if best:
                break
    if best:
        phrase, skname = SKILL_PHRASE[best[1]]
        if best[2]:
            return (f"{phrase} ({skname} {best[2]}).", 90)
        return (f"{phrase}.", 85)
    fams = {w.spell_family.get(s) for s, _, _ in entries}
    if 3 in fams:
        return ("Conjured by mages.", 80)
    if 5 in fams:
        return ("Created by warlocks.", 80)
    return None


def render_quest_line(w, item, entries, fac):
    mine = [(q, z) for q, z, f in entries if f is None or f == fac]
    if not mine:
        return (f"Awarded only by {OTHER[fac]} quests.", 30) if entries else None
    if (w.items.get(item) or {}).get("quality") == 5:
        return ("Forged at the end of a legendary quest chain.", 90)
    zones = Counter(z for _, z in mine if z is not None and w.zone_allowed(z, fac))
    if not zones:
        return ("Awarded for completing a quest.", 55)
    top = [z for z, _ in zones.most_common(2)]
    if len(mine) == 1:
        return (f"Awarded for a quest {w.zones_phrase(top[:1])}.", 65)
    return (f"Awarded by quests {w.zones_phrase(top)}.", 65)


def render_disenchant_line(w, dids):
    qs, lo, hi = set(), 99, 0
    for did in set(dids):
        for qual, ilvl in w.disenchant_source.get(did, []):
            qs.add(qual)
            lo, hi = min(lo, ilvl), max(hi, ilvl)
    if hi == 0:
        return ("Distilled by enchanters from unwanted magical gear.", 60)
    qnames = join_names([QUALITY[q] for q in sorted(qs) if q in QUALITY])
    band = f"level {lo}" if lo == hi else f"levels {lo}-{hi}"
    return (f"Distilled by enchanters from {qnames} items of {band}.", 60)


PRIORITY = ["vendor", "craft", "herb", "mine", "fish", "skin", "drop", "container", "chest", "other", "pick", "quest", "disenchant", "start"]

SKILL_PEOPLE = {164: "blacksmiths", 165: "leatherworkers", 171: "alchemists", 185: "cooks", 186: "miners",
                197: "tailors", 202: "engineers", 333: "enchanters", 129: "field medics", 40: "rogues", 356: "anglers"}
ITEM_CLASS_WORD = {0: "consumable", 1: "container", 2: "weapon", 4: "armour", 5: "reagent", 6: "ammunition",
                   7: "trade good", 9: "recipe", 11: "quiver", 12: "quest item", 13: "key", 15: "curio"}


def render_uses(w, item, fac):
    """Short 'what is it for' sentence(s) for the encyclopedia page."""
    it = w.items.get(item) or {}
    parts = []
    skills = sorted(SKILL_PEOPLE[s] for s in w.reagent_skills.get(item, ()) if s in SKILL_PEOPLE)
    if skills:
        parts.append(f"A reagent prized by {join_names(skills)}.")
    wants = [(z, f) for z, f in w.quest_wants.get(item, []) if f is None or f == fac]
    if wants:
        zones = Counter(z for z, _ in wants if z is not None and w.zone_allowed(z, fac))
        if zones:
            top = [z for z, _ in zones.most_common(2)]
            parts.append(f"Sought by questgivers {w.zones_phrase(top)}.")
        else:
            parts.append("Sought by questgivers somewhere in Azeroth.")
    if it.get("class") == 9:
        skill = RECIPE_SUBCLASS_SKILL.get(it.get("subclass")) or it.get("required_skill")
        who = SKILL_PEOPLE.get(skill)
        rank = it.get("required_skill_rank") or 0
        if who:
            parts.append(f"Teaches {who} a new technique" + (f" (skill {rank})." if rank else "."))
    if it.get("start_quest"):
        parts.append("Begins a quest when read.")
    if it.get("disenchant_id") and (it.get("quality") or 0) >= 2:
        parts.append("Can be disenchanted.")
    return " ".join(parts)


def render_item(w, item, s, fac, max_lines=3):
    _MARKS.clear()
    lines = {}
    if s.get("vendor"):
        lines["vendor"] = render_vendor_line(w, item, s["vendor"], fac)
    if s.get("craft"):
        lines["craft"] = render_craft_line(w, s["craft"])
    if s.get("object"):
        lines.update(render_object_lines(w, item, s["object"], fac))
    if s.get("fish"):
        lines["fish"] = render_fish_line(w, s["fish"], fac)
    if s.get("skin"):
        lines["skin"] = render_creature_line(w, s["skin"], fac, "skin")
    if s.get("drop"):
        lines["drop"] = render_creature_line(w, s["drop"], fac, "drop")
    if s.get("container"):
        lines["container"] = render_container_line(w, s["container"])
    if s.get("pick"):
        lines["pick"] = render_creature_line(w, s["pick"], fac, "pick")
    if s.get("quest"):
        lines["quest"] = render_quest_line(w, item, s["quest"], fac)
    if s.get("disenchant"):
        lines["disenchant"] = render_disenchant_line(w, s["disenchant"])
    if s.get("start"):
        lines["start"] = ("Issued to new adventurers as starting equipment.", 40)
    ranked = []
    for i, k in enumerate(PRIORITY):
        v = lines.get(k)
        if v:
            ranked.append((-v[1], i, v[0]))
    ranked.sort()
    if not ranked:
        return []
    best = -ranked[0][0]
    out = []
    for neg, _, text in ranked:
        strength = -neg
        # once a solid source is known, do not pad with junk sources
        if best >= 50 and strength <= 12:
            continue
        out.append(text)
    return out[:max_lines]


def first_zone(w, lines):
    """Name of the first zone mentioned in the ranked lines (for the atlas page)."""
    names = sorted(set(w.zone_name.values()), key=len, reverse=True)
    for line in lines:
        best, best_pos = None, None
        for n in names:
            variants = [n, zone_phrase_name(n)]
            if n.startswith("The "):
                variants.append(n[4:])
            for variant in variants:
                pos = line.find(variant)
                if pos >= 0 and (best_pos is None or pos < best_pos):
                    best, best_pos = n, pos
        if best:
            return best
    return None


def mark_for(w, zone_name, marks):
    """'x,y,r' for the atlas zone, from the marks noted while rendering."""
    for z, (cx, cy, r) in marks.items():
        if w.zone_name.get(z) == zone_name:
            return f"{cx:.1f},{cy:.1f},{r:.1f}"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mangos", required=True)
    ap.add_argument("--pfquest", required=True, help="pfQuest db directory (contains units.lua, objects.lua)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--check", nargs="*", type=int, default=[])
    ap.add_argument("--max-lines", type=int, default=3)
    args = ap.parse_args()

    print("loading world...", file=sys.stderr)
    w = World(args.mangos, args.pfquest)
    print(f"  items={len(w.items)} creatures={len(w.creatures)} objects={len(w.gobjs)} zones={len(w.zone_name)}", file=sys.stderr)
    print("collecting sources...", file=sys.stderr)
    src = collect_sources(w)
    print(f"  items with sources: {len(src)}", file=sys.stderr)

    if args.check:
        for item in args.check:
            it = w.items.get(item, {})
            print(f"\n[{item}] {it.get('name')}")
            for fac in ("A", "H"):
                for line in render_item(w, item, src.get(item, {}), fac, args.max_lines):
                    print(f"  {fac}: {line}")
        return

    print("rendering...", file=sys.stderr)
    out_lines = []
    name_lines = []
    extra_lines = []
    n_items = 0
    n_split = 0
    for item in sorted(src):
        it = w.items.get(item)
        if not it:
            continue
        a = render_item(w, item, src[item], "A", args.max_lines)
        marks_a = dict(_MARKS)
        h = render_item(w, item, src[item], "H", args.max_lines)
        marks_h = dict(_MARKS)
        if not a and not h:
            continue
        n_items += 1
        if a == h:
            out_lines.append(f"D[{item}]={lua_str(chr(10).join(a))}")
        else:
            n_split += 1
            out_lines.append(f"D[{item}]={{A={lua_str(chr(10).join(a))},H={lua_str(chr(10).join(h))}}}")
        name_lines.append(f"N[{item}]={lua_str(it['name'] or '')}")
        # encyclopedia extras: zone for the atlas page, flavour text, uses
        fields = []
        za, zh = first_zone(w, a), first_zone(w, h)
        if za:
            fields.append(f"z={lua_str(za)}")
        if zh and zh != za:
            fields.append(f"zh={lua_str(zh)}")
        ma = mark_for(w, za, marks_a) if za else None
        mh = mark_for(w, zh or za, marks_h) if (zh or za) else None
        if ma:
            fields.append(f"m={lua_str(ma)}")
        if mh and mh != ma:
            fields.append(f"mh={lua_str(mh)}")
        flavour = (it.get("description") or "").strip()
        if flavour:
            fields.append(f"f={lua_str(flavour)}")
        ua, uh = render_uses(w, item, "A"), render_uses(w, item, "H")
        if ua:
            fields.append(f"u={lua_str(ua)}")
        if uh and uh != ua:
            fields.append(f"uh={lua_str(uh)}")
        if fields:
            extra_lines.append(f"X[{item}]={{{','.join(fields)}}}")
    today = dt.date.today().isoformat()
    header = f"""-- WhereIsIt item source hints. GENERATED FILE - do not edit by hand.
-- Built {today} by tools/build_data.py from:
--   vmangos world database (https://github.com/vmangos/core, db_latest SQLite snapshot)
--   pfQuest spawn data (https://github.com/shagu/pfQuest, MIT)
-- Entries: {n_items} items ({n_split} with separate Alliance/Horde wording).
-- D[id] = ranked hint lines ("line\\nline..." or {{A=...,H=...}}); the tooltip shows the first few,
--         the encyclopedia shows them all.
-- N[id] = item name (for searching).  X[id] = {{z=atlas zone, zh=Horde zone if different,
--         m="x,y,spread" where the sources cluster on that zone's map (mh for the Horde),
--         f=flavour text, u=uses, uh=Horde uses if different}}.
local _, ns = ...
ns.DataVersion = "{today}"
local D, N, X = {{}}, {{}}, {{}}
ns.Data, ns.Names, ns.Extra = D, N, X
"""
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(header)
        f.write("\n".join(out_lines))
        f.write("\n")
        f.write("\n".join(name_lines))
        f.write("\n")
        f.write("\n".join(extra_lines))
        f.write("\n")
    print(f"wrote {args.out}: {n_items} items, {n_split} faction-split, {len(extra_lines)} with extras, {os.path.getsize(args.out)/1e6:.1f} MB", file=sys.stderr)


if __name__ == "__main__":
    main()
