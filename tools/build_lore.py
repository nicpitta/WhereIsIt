#!/usr/bin/env python3
"""Compose the encyclopedia's "account" of every item: one or two paragraphs
grounded in the same sources build_data.py uses (loot, vendors, spawns,
crafts, quests) and a hand-written knowledge base of the places, peoples and
materials of Azeroth (lore_world.py, lore_things.py, lore_bespoke.py).

Passages that recur (a zone's description, a people's history, a trade's
account) are written to the output once, as a table K, and each item's text
refers to them with {kind|key} tokens that the addon expands when it renders
the page. That keeps the file to a few megabytes.

Output is WhereIsIt_Lore.lua, listed in the addon's TOC after the data file.

Usage: python -I tools/build_lore.py --mangos <mangos.sqlite> --pfquest <pfQuest/db>
         --out WhereIsIt_Lore.lua [--check id ...] [--sample N]
"""
import argparse
import datetime as dt
import os
import random
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_data as B  # noqa: E402
from lore_world import ZONES, DUNGEONS, PEOPLES, BEASTS  # noqa: E402
from lore_things import (ITEMS, CULTURES, WEAPONS, ARMOR, JEWELRY, QUALITY_LINES, LEVEL_LINES,  # noqa: E402
                         CONSUMABLE_KW, RECIPE_WORDS, PROFESSIONS, VENDORS)
from lore_bespoke import BESPOKE  # noqa: E402

FACTION_NAME = {"A": "Alliance", "H": "Horde"}
OTHER = {"A": "Horde", "H": "Alliance"}
CLASS_NAMES = {1: "warriors", 2: "paladins", 4: "hunters", 8: "rogues", 16: "priests", 64: "shaman", 128: "mages", 256: "warlocks", 1024: "druids"}
GENERIC = {"humanoid foes", "beasts", "creatures", "a variety of creatures", "the restless dead", "demons", "dragonkin",
           "elementals", "giants", "strange creatures", "winged creatures", "crawling vermin", "critters"}

# shared passages, written once to the Lua file
KB = defaultdict(dict)


def T(kind, key, text):
    """Register a shared passage and return the token that stands for it."""
    if text is None:
        return None
    key = str(key)
    KB[kind][key] = text
    return "{%s|%s}" % (kind, key)


def expand_tokens(text):
    return re.sub(r"\{(\w+)\|([^}]+)\}", lambda m: KB.get(m.group(1), {}).get(m.group(2), "?"), text or "")


def pick(R, options):
    return options[R.randrange(len(options))]


def cap(s):
    return s[0].upper() + s[1:] if s else s


def lower_first(s):
    return s[0].lower() + s[1:] if s else s


def sentence(s):
    s = s.strip()
    if s and s[-1] not in ".!?\"}":
        s += "."
    return s


def the(desc):
    if desc.startswith(("the ", "a ")):
        return desc
    return "the " + desc


def singular_person(plural):
    """'alchemists' -> 'an alchemist'; 'shaman' -> 'a shaman'"""
    if plural == "shaman":
        return "a shaman"
    return B.singular_vendor(plural)


# ---------------------------------------------------------------------------
# Places
# ---------------------------------------------------------------------------
def place(w, z):
    name = w.zone_name.get(z)
    if not name:
        return None, None, False
    if name in DUNGEONS:
        return name, DUNGEONS[name], True
    return name, ZONES.get(name), False


def place_short(w, z):
    name, e, _ = place(w, z)
    if e and e.get("short"):
        return e["short"]
    return B.zone_phrase_name(name or "parts unknown")


def place_desc_token(w, z):
    name, e, dungeon = place(w, z)
    if not e:
        return None
    return T("D" if dungeon else "Z", name, e["desc"])


def group_lore_token(desc):
    if desc in GENERIC:
        return None
    if desc in PEOPLES:
        return T("P", desc, PEOPLES[desc])
    if desc in BEASTS:
        return T("B", desc, BEASTS[desc])
    if " and " in desc:
        a = desc.split(" and ", 1)[0]
        return group_lore_token(a)
    return None


# ---------------------------------------------------------------------------
# Paragraph 1: the thing itself
# ---------------------------------------------------------------------------
TRADE_KW = [
    (r"Leather|Hide|Pelt|Scale\b|Scales\b", "A leather of the tanners' trade, taken from the hunt and cured for the leatherworkers."),
    (r"Cloth|Silk|Thread|Bolt", "A cloth of the tailors' trade."),
    (r"\bOre\b", "An ore of the miners' trade, dug from the veins of Azeroth for the smelters."),
    (r"\bBar\b|Ingot", "A smelted metal, ready for the forges of the blacksmiths and engineers."),
    (r"Stone\b", "A stone of the smiths' and engineers' trade."),
    (r"Dust|Essence|Shard|Crystal", "A reagent of the enchanters' trade, distilled from magical things."),
    (r"Meat|Flesh|Rib|Flank|Haunch|Liver|Snout|Wing\b|Leg\b|Tail\b", "A cut of the hunt, for the cook's pot."),
    (r"\bEgg\b", "An egg, for the cook's pot or the collector's shelf."),
    (r"Feather|Plume", "A feather, for fletchers, tailors and the druids' reagents."),
    (r"Fang|Claw|Tooth|Tusk|Horn|Talon", "A trophy of the hunt, wanted by the tribes' craftsmen and for a dozen errands."),
    (r"Venom|Poison|Ichor|Gland|Sac\b", "A venom of the alchemists' and rogues' trade."),
    (r"Powder|Tube|Bolt|Gizmo|Widget|Casing|Framework|Strut|Modulator|Contact|Transformer|Cylinder|Wiring|Scope|Stock\b|Gear\b|Spring|Cog|Buckle|Rivet|Grip\b|Chain\b", "A component of the engineers' and smiths' trades."),
    (r"Herb|Root|Leaf|Bloom|Flower|Lotus|Moss|Weed|Thorn|Grass|Kelp|Mushroom|Cap\b|Sansam|Foil|Sage|Bite", "An herb of the herbalists' trade, gathered for the alchemists."),
    (r"Pearl|Gem|Diamond|Ruby|Sapphire|Emerald|Opal|Agate|Jade|Citrine|Aquamarine|Moonstone|Malachite|Tigerseye|Shadowgem", "A gemstone of the jewellers', enchanters' and engineers' trade."),
    (r"Vial|Flask|Bottle|Jar", "A vessel of the alchemists' trade."),
    (r"Spice|Salt|Seasoning|Flour|Sugar|Hops|Yeast|Berries|Berry|Fruit|Apple|Melon", "A provision of the cooks' trade."),
    (r"Rune|Candle|Symbol|Totem|Ankh|Seed|Figurine|Orb|Reagent", "A reagent of the spellcasting classes."),
    (r"Dye|Bleach|Ink|Parchment|Oil\b|Flux|Coal|Tannin|Tinder|Wood\b", "A supply of the crafting trades."),
]
PET_RE = re.compile(r"Cage|Carrier|Whistle|Crate|Companion|Kitten|Hatchling|Owl|Parrot|Rabbit|Snake|Frog|Prairie Dog|Cockroach|Moth|Chicken|Rat\b|Cat\b|Puppy|Worg Pup|Sprite Darter|Smolderweb|Bombling|Lil Smoky|Mechanical|Tree Frog|Pet\b", re.I)
MOUNT_RE = re.compile(r"Reins|Horn of|Whistle of|Bridle|Mechanostrider|Charger|Warhorse|Deathcharger|Resonating Crystal|Swift |Kodo$|Raptor$|Wolf$|Horse$|Ram$|Saber$|Tiger$", re.I)


def nature(w, it, src, R):
    name = it["name"] or ""
    cls, sub, inv, q = it["class"], it["subclass"], it["inventory_type"], it["quality"] or 0
    sents = []
    gear = cls in (2, 4)
    if name in ITEMS:
        sents.append(T("I", name, ITEMS[name]))
    elif cls == 2:
        kind, s = WEAPONS.get(sub, ("weapon", None))
        sents.append(T("W", sub, s) if s else "A weapon of uncertain style.")
    elif cls == 4:
        s = ARMOR.get(sub)
        if s is None:
            j = JEWELRY.get(inv)
            sents.append(T("J", inv, j) if j else "An accessory of the adventuring trade.")
        else:
            sents.append(T("A", sub, s))
    elif cls == 0:
        hit = next((i for i, (pat, t) in enumerate(CONSUMABLE_KW) if re.search(pat, name, re.I)), None)
        sents.append(T("K", hit, CONSUMABLE_KW[hit][1]) if hit is not None else "A consumable of the road, used once and gone.")
    elif cls == 9:
        word = RECIPE_WORDS.get(sub, "recipe")
        skill = B.RECIPE_SUBCLASS_SKILL.get(sub) or it.get("required_skill")
        prof = PROFESSIONS.get(skill)
        made = []
        for sid in (it.get("spellid_1"), it.get("spellid_2"), it.get("spellid_3")):
            for craft in w.spell_learns.get(sid, ()):
                for prod in w.spell_creates.get(craft, ()):
                    pn = (w.items.get(prod) or {}).get("name")
                    if pn:
                        made.append(pn)
        lead = f"A {word} of the {prof[0].lower()} trade" if prof else f"A {word}"
        if made:
            lead += f", which teaches the making of {B.join_names(sorted(set(made))[:2])}"
        elif ":" in name:
            lead += f", which teaches {name.split(':', 1)[1].strip()}"
        sents.append(lead + ".")
        if prof:
            sents.append(T("T", skill, prof[1]))
        rank = it.get("required_skill_rank") or 0
        if rank and prof:
            who = singular_person(B.SKILL_PEOPLE.get(skill, "crafters"))
            sents.append(pick(R, [
                f"Only {who} of some skill (around {rank}) can follow it.",
                f"It asks a skill of about {rank} of {who} who attempts it.",
            ]))
    elif cls in (7, 5):
        hit = next((i for i, (pat, t) in enumerate(TRADE_KW) if re.search(pat, name, re.I)), None)
        sents.append(T("R", hit, TRADE_KW[hit][1]) if hit is not None else "A material of the crafting trades.")
    elif cls == 12:
        sents.append(pick(R, [
            "An object of significance to someone in Azeroth, wanted for a task rather than for itself.",
            "A thing wanted not for its own sake but because someone, somewhere, has asked for it.",
            "A token, proof or ingredient of somebody's errand, worth nothing to anyone else.",
        ]))
    elif cls == 13:
        sents.append("A key, which opens one door in Azeroth and no other.")
    elif cls == 1:
        sents.append("Bags are the most practical product of the tailors' and leatherworkers' trades, and every adventurer wants more of them.")
    elif cls == 6:
        sents.append("Ammunition for the hunters' bows and guns, sold by every bowyer and gunsmith and made by the engineers.")
    elif cls == 11:
        sents.append("A quiver or ammunition pouch, the leatherworkers' product for the hunters.")
    elif cls == 15:
        if q >= 3 and MOUNT_RE.search(name):
            sents.append("A mount, the pride of its rider, bred by the stables of its people or won from the great foes.")
        elif q >= 1 and PET_RE.search(name):
            sents.append("A companion creature, kept by adventurers for company on the long roads and sold by the pet dealers of the capitals or found in the far places.")
        elif q == 0:
            sents.append(pick(R, [
                "A curio of no use beyond the coin a merchant will give for it.",
                "Junk, in a word: the sort of thing that fills the pockets of the dead and the sacks of adventurers.",
                "A trifle carried for no good reason by whoever it was taken from, and sold at the first shop.",
            ]))
        else:
            sents.append("A curio of the adventuring trade.")
    else:
        sents.append("An object of the adventuring trade.")

    if cls in (2, 4, 12, 13, 15, 1, 11):
        for i, (pat, t) in enumerate(CULTURES):
            if re.search(pat, name, re.I):
                sents.append(T("C", i, t))
                break
    if gear:
        if q >= 2 or q == 0:
            opts = QUALITY_LINES.get(q, QUALITY_LINES[1])
            i = R.randrange(len(opts))
            sents.append(T("Q", f"{q}.{i}", opts[i]))
        elif R.random() < 0.4:
            i = R.randrange(len(QUALITY_LINES[1]))
            sents.append(T("Q", f"1.{i}", QUALITY_LINES[1][i]))
        lvl = it.get("required_level") or 0
        if lvl > 0:
            for i, (cutoff, t) in enumerate(LEVEL_LINES):
                if lvl <= cutoff:
                    sents.append(T("L", i, t))
                    break
        if (it.get("bonding") == 1) and q >= 3:
            sents.append(pick(R, [
                "It binds itself to whoever first takes it up, and cannot be sold or given away.",
                "Once taken up it will serve no other hand.",
            ]))
    return " ".join(sentence(s) for s in sents if s)


# ---------------------------------------------------------------------------
# Paragraph 2: provenance
# ---------------------------------------------------------------------------
def analyze_creatures(w, entries, fac, mode):
    zone_score = Counter()
    per = {}
    for npc, ch, quest in entries:
        c = w.creatures.get(npc)
        if not c:
            continue
        if c["type"] == 8 and (mode != "drop" or ch < 1):
            continue
        zones = w.unit_zones.get(npc) or Counter({None: 0.5})
        per[npc] = (c, ch, quest, zones)
        for z, n in zones.items():
            zone_score[z] += n * ch
    if not per:
        return None
    zones = B.top_zones(zone_score, lambda z: w.zone_allowed(z, fac))
    any_zone = any(z is not None for z in zone_score)
    weighted_all = [(v[0], sum(v[3].values()) * v[1]) for v in per.values()]
    if zones:
        zset = set(zones)
        weighted = [(c, sum(v for z, v in zc.items() if z in zset) * ch) for c, ch, q, zc in per.values() if any(z in zset for z in zc)]
        in_zone = [(c, ch, q) for c, ch, q, zc in per.values() if any(z in zset for z in zc)]
        max_chance = max(ch for c, ch, q in in_zone)
        quest_only = all(q for c, ch, q in in_zone)
    else:
        weighted = weighted_all
        max_chance = max(v[1] for v in per.values())
        quest_only = all(v[2] for v in per.values())
    total = sum(x for _, x in weighted) or 1
    return {
        "focus": B.focus_for_creatures(w, [(n, v[1], v[2]) for n, v in per.items()], zones[0]) if zones else None,
        "zones": zones,
        "desc": B.dominant_descriptor(weighted),
        "boss_share": sum(x for c, x in weighted if (c["rank"] or 0) == 3) / total,
        "rare_share": sum(x for c, x in weighted if (c["rank"] or 0) == 2) / total,
        "in_dungeon": bool(zones) and all(z in B.DUNGEON_ZONES for z in zones),
        "in_raid": bool(zones) and all(z in B.RAID_ZONES for z in zones),
        "max_chance": max_chance,
        "quest_only": quest_only,
        "opposing_only": any_zone and not zones,
        "world_drop": len(per) >= 40 and max(v[1] for v in per.values()) < 0.6,
        "band": B.level_band(w, weighted_all),
    }


def chance_sentence(R, desc, ch, where=""):
    generic = desc in GENERIC
    who = "the creatures of the region" if desc in ("a variety of creatures", "creatures") else the(desc)
    if generic and desc == "humanoid foes":
        who = "the raiders and tribesmen there"
    elif generic and desc == "beasts":
        who = "the wild beasts there"
    if ch >= 40:
        return pick(R, [f"Nearly every one of {who} carries one{where}.", f"It is found on almost all of {who}{where}."])
    if ch >= 12:
        return pick(R, [f"A good share of {who} carry it{where}.", f"Perhaps one in four of {who} has one about them{where}."])
    if ch >= 3:
        return pick(R, [f"One of {who} in a score or so carries it{where}.", f"It turns up on {who} now and then, perhaps once in twenty{where}."])
    if ch >= 0.5:
        return pick(R, [f"It is a rare find among {who}{where}; a patient hunter may see one in a long day's culling.", f"Only occasionally does one of {who} carry it{where}."])
    return pick(R, [f"It is a very rare find among {who}{where}, the kind of thing found once in a lifetime of hunting them.", f"One of {who} in many hundreds carries it{where}."])


def direction_sentence(R, w, zone, focus, what="they"):
    """A sentence placing the sources within the zone, from their spawn spread."""
    if not focus or not focus[3] or zone in B.DUNGEON_ZONES:
        return None
    noun = B.DIR_NOUN.get(focus[3])
    if not noun:
        return None
    short = place_short(w, zone)
    if noun == "centre":
        return pick(R, [f"Within {short}, {what} keep to the heart of the land.", f"Look to the middle of {short}."])
    return pick(R, [f"Within {short}, {what} keep to the {noun}.", f"Look to the {noun} of {short}.",
                    f"It is the {noun} of {short} that rewards the search."])


def zones_intro(w, zones, R, lead_options, focus=None, what="they"):
    out = [pick(R, lead_options).format(short=place_short(w, zones[0]))]
    d = place_desc_token(w, zones[0])
    if d:
        out.append(d)
    ds = direction_sentence(R, w, zones[0], focus, what)
    if ds:
        out.append(ds)
    if len(zones) > 1:
        out.append(pick(R, [
            f"It is found as readily in {place_short(w, zones[1])}.",
            f"The other place to look is {place_short(w, zones[1])}.",
        ]))
    return out


DROP_LEADS = ["The place to look is {short}.", "Hunters find it most readily in {short}.", "Its home, so far as it has one, is {short}."]
SKIN_LEADS = ["Skinners know it from {short}.", "It is a skinner's find, chiefly in {short}."]
PICK_LEADS = ["Pickpockets know it from {short}."]


def expand_drop(w, a, R, fac, mode="drop"):
    out = []
    desc = a["desc"]
    glore = group_lore_token(desc)
    if a["world_drop"]:
        band = a["band"]
        return [pick(R, [
            "It is what the trade calls a world drop: no tribe, beast or master carries it in particular, and it surfaces wherever adventurers" + (f" of {band}" if band else "") + " fight, from one end of the continents to the other.",
            "No one owner can be named for it. It turns up in the hoards and pockets of foes across Azeroth" + (f", most often among creatures of {band}" if band else "") + ", and no two finders agree where to look.",
        ])]
    zones = a["zones"]
    if zones and (a["in_dungeon"] or a["in_raid"]):
        name, e, _ = place(w, zones[0])
        short = e["short"] if e else place_short(w, zones[0])
        out.append(pick(R, [f"It comes out of {short}.", f"Its source is {short}, and nowhere in the open world."]))
        d = place_desc_token(w, zones[0])
        if d:
            out.append(d)
        if a["boss_share"] >= 0.6 and e:
            out.append(pick(R, [
                f"The great prizes of {short} are kept by {e['masters']}, and this is one of them.",
                f"It is among the treasures that {e['masters']} hold there, and only their fall releases it.",
            ]))
        else:
            if glore:
                out.append(glore)
            if desc in GENERIC:
                out.append(pick(R, [f"Within, it is carried by the common run of the place's defenders.", f"The rank and file of {short} have it about them."]))
            else:
                out.append(pick(R, [f"Within, it is {the(desc)} who carry it.", f"It is {the(desc)} of {short} who have it about them."]))
        return out
    if zones:
        leads = SKIN_LEADS if mode == "skin" else PICK_LEADS if mode == "pick" else DROP_LEADS
        out.extend(zones_intro(w, zones, R, leads, a["focus"], "they"))
        if glore:
            out.append(glore)
        if mode == "skin":
            out.append(pick(R, [f"Skinners take it from the carcasses of {the(desc)} there.", f"It is cut from {the(desc)} there by anyone with a skinning knife and the patience."]))
        elif mode == "pick":
            out.append(f"Rogues lift it from the pockets of {the(desc)} there, who seldom notice.")
        elif a["rare_share"] >= 0.6:
            out.append("It is carried by one of the rare, named creatures that roam there and are seen only now and then, and nowhere else.")
        elif a["boss_share"] >= 0.6:
            out.append(f"It is held by one of the mighty foes of {place_short(w, zones[0])}, not by the common run of its creatures.")
        elif a["quest_only"]:
            out.append(f"{cap(the(desc))} there surrender it only to those on the business of a quest.")
        else:
            out.append(chance_sentence(R, desc, a["max_chance"]))
        return out
    if a["opposing_only"]:
        out.append(pick(R, [
            f"Our correspondents report it among {the(desc)} in {OTHER[fac]} lands, where travellers of the {FACTION_NAME[fac]} are not welcome; it will be hard to come by.",
            f"It is carried by {the(desc)}, but only in the territory of the {OTHER[fac]}, and a traveller of the {FACTION_NAME[fac]} must go armed or trade for it.",
        ]))
        if glore:
            out.append(glore)
        return out
    if glore:
        out.append(glore)
    out.append(chance_sentence(R, desc, a["max_chance"]))
    return out


def expand_vendor(w, item, entries, fac, R):
    it = w.items.get(item) or {}
    sellers = {npc: (w.unit_fac.get(npc, "AH"), maxc) for npc, maxc in entries if npc in w.creatures}
    mine = {npc: v for npc, v in sellers.items() if fac in v[0]}
    out = []
    if not mine:
        if sellers:
            out.append(f"It is stocked only by merchants of the {OTHER[fac]}; a traveller of the {FACTION_NAME[fac]} must trade for it at the neutral ports or do without.")
        return out
    if it.get("required_reputation_faction"):
        return ["It is issued by a quartermaster, and only to those who have earned their faction's trust through long service."]
    cats = Counter()
    zone_count = Counter()
    for npc, (f, maxc) in mine.items():
        c = w.creatures.get(npc) or {}
        cats[B.plural_vendor(c.get("subname"))] += 1
        for z, n in (w.unit_zones.get(npc) or {}).items():
            if z is not None and z not in B.BATTLEGROUND_ZONES:
                zone_count[z] += 1
    cat = cats.most_common(1)[0][0]
    out.append(pick(R, ["It is bought, not hunted.", "This is a thing one buys."]))
    if VENDORS.get(cat):
        out.append(T("V", cat, VENDORS[cat]))
    zones = [z for z, _ in zone_count.most_common()]
    n = len(mine)
    if n >= 8 and len(zones) >= 5:
        out.append(pick(R, [
            f"It is as common as bread: nearly every settlement in {FACTION_NAME[fac]} lands stocks it, and the goblin ports besides.",
            f"Travellers of the {FACTION_NAME[fac]} will find it on the shelves of most towns and outposts, and in the neutral markets of the goblins.",
        ]))
    elif zones:
        d = place_desc_token(w, zones[0])
        if d:
            out.append(d)
        sellers_here = [npc for npc in mine if zones[0] in (w.unit_zones.get(npc) or {})]
        focus = B.focus_for_units(w, sellers_here, zones[0])
        if len(zones) > 1:
            out.append(f"Merchants in {place_short(w, zones[0])} and {place_short(w, zones[1])} stock it.")
        else:
            out.append(f"A merchant in {place_short(w, zones[0])} stocks it.")
        if focus and focus[3] and B.DIR_NOUN.get(focus[3]) and B.DIR_NOUN[focus[3]] != "centre":
            out.append(f"The shop is in the {B.DIR_NOUN[focus[3]]} of the land.")
    if any(maxc for _, maxc in mine.values()):
        out.append("Stock is limited, and whoever gets there first takes it.")
    return out


def craft_reagents(w, spell):
    rows = w.q("""select reagent1,reagent2,reagent3,reagent4,reagent5,reagent6,reagent7,reagent8
                  from spell_template t where entry=? and build=(select max(build) from spell_template where entry=t.entry)""", spell)
    names = []
    for r in rows:
        for k in r.keys():
            if r[k]:
                n = (w.items.get(r[k]) or {}).get("name")
                if n and n not in names:
                    names.append(n)
    return names


def expand_craft(w, it, entries, R):
    if it.get("class") == 12:
        return ["It is prepared on the spot by the adventurer who needs it, from what the errand provides."]
    best = None
    for spell, skill, val in entries:
        if skill in PROFESSIONS:
            if not best or (val or 0) < (best[2] or 0):
                best = (spell, skill, val)
    if not best:
        for spell, skill, val in entries:
            name = w.spell_name.get(spell) or ""
            if B.CRAFT_SKIP_RE.search(name):
                continue
            for pat, sk in B.CRAFT_NAME_HINTS:
                if re.search(pat, name, re.I):
                    best = (spell, sk, None)
                    break
            if best:
                break
    if not best:
        fams = {w.spell_family.get(s) for s, _, _ in entries}
        if 3 in fams:
            return ["It is conjured by mages out of nothing, as they conjure bread and water, and vanishes when its maker is long gone."]
        if 5 in fams:
            return ["It is created by warlocks from the stuff of the Nether, and lasts only so long as its maker does."]
        return []
    spell, skill, val = best
    pname, ptext = PROFESSIONS[skill]
    out = [pick(R, ["It is made, not found.", "This is the work of a craftsman's hands."]), T("T", skill, ptext)]
    reagents = craft_reagents(w, spell)
    if reagents:
        out.append(pick(R, [f"This one is worked from {B.join_names(reagents[:3])}.", f"Its making calls for {B.join_names(reagents[:3])}."]))
    if val:
        who = singular_person(B.SKILL_PEOPLE.get(skill, "crafters"))
        if val < 200:
            out.append(pick(R, [f"{cap(who)} of middling skill (around {val}) can attempt it.", f"It is first attempted at a {pname} skill of about {val}."]))
        else:
            out.append(pick(R, [f"Only {who} of real accomplishment (skill around {val}) can attempt it.", f"It is first attempted at a {pname} skill of about {val}."]))
    return out


def expand_objects(w, item, entries, fac, R):
    groups = {}
    for go, ch, quest in entries:
        g = w.gobjs.get(go)
        if not g:
            continue
        name = g["name"] or ""
        if name in B.HERB_NAMES:
            k = "herb"
        elif B.MINE_RE.search(name):
            k = "mine"
        elif B.CHEST_RE.search(name):
            k = "chest"
        else:
            k = "other"
        groups.setdefault(k, []).append((go, ch, name))
    out = {}
    for kind, lst in groups.items():
        zone_score = Counter()
        names = Counter()
        for go, ch, name in lst:
            spawns = w.obj_zones.get(go) or Counter({None: 0.5})
            for z, n in spawns.items():
                zone_score[z] += n * ch
            names[name] += sum(spawns.values()) * ch
        zones = B.top_zones(zone_score, lambda z: w.zone_allowed(z, fac))
        top = names.most_common(1)[0][0]
        leads = {"herb": ["Herbalists know it from {short}."], "mine": ["Miners know it from {short}."],
                 "chest": ["It is a finder's prize, chiefly in {short}."], "other": ["It is found in {short}."]}[kind]
        focus = B.focus_for_objects(w, [(go, ch, None) for go, ch, _ in lst], zones[0]) if zones else None
        what = {"herb": "the plants", "mine": "the veins", "chest": "the caches", "other": "they"}[kind]
        sents = zones_intro(w, zones, R, leads, focus, what) if zones else []
        where = f" in {place_short(w, zones[0])}" if zones else ""
        if kind == "herb":
            sents.append(pick(R, [f"Herbalists gather it{where}, where it grows thickest.", f"It is the herbalists who bring it in{where}."]))
        elif kind == "mine":
            vein = re.sub(r"^(Ooze Covered|Small|Rich|Lesser|Greater|Hakkari) ", "", top).lower()
            sents.append(pick(R, [f"Miners strike it in the {vein}s{where}.", f"It comes out of the {vein}s{where}, under the miner's pick."]))
        elif kind == "chest":
            sents.append(pick(R, [
                f"It turns up in the chests and caches that adventurers find{where}: the lost baggage of the dead, the stashes of bandits and the strongboxes of camps long abandoned.",
                f"Chests and strongboxes{where} hold it now and then, left by whoever did not live to open them.",
            ]))
        else:
            sents.append(f"It is taken from {B.with_article(top)}{where}.")
        out[kind] = sents
    return out


def expand_fish(w, entries, fac, R):
    zone_score = Counter()
    area_best = {}
    for z, ch, area in entries:
        if z is not None:
            zone_score[z] = max(zone_score[z], ch)
            if ch >= area_best.get(z, (0, None))[0]:
                area_best[z] = (ch, area)
    zones = B.top_zones(zone_score, lambda z: w.zone_allowed(z, fac), keep_ratio=0.6)
    if not zones:
        return ["Anglers pull it from the waters of Azeroth, though our correspondents disagree on which."]
    name, e, _ = place(w, zones[0])
    waters = B.water_name(w, area_best[zones[0]][1], zones[0]) or (e or {}).get("waters") or f"the waters of {place_short(w, zones[0])}"
    out = zones_intro(w, zones, R, [f"It is a catch of {waters}.", "Anglers know it from {short}."])
    out.append(pick(R, [f"Anglers pull it from {waters}.", f"It is fished from {waters} by anyone with a pole and the patience."]))
    return out


def expand_container(w, entries, R):
    names = Counter()
    for cont, ch in entries:
        names[(w.items.get(cont) or {}).get("name", "container")] += ch
    top = names.most_common(1)[0][0]
    low = top.lower()
    if "lockbox" in low:
        return ["Lockboxes are the strongboxes of travellers who did not survive to open them, carried off by whatever killed them. Only a rogue's picks or an engineer's seaforium will open one, and this is among what they hold."]
    if "junkbox" in low:
        return ["Junkboxes are the pocket-hoards that rogues lift from the unwary, and this is the sort of thing they contain."]
    if "clam" in low:
        return ["It is found in the clams of the coasts, pried open by whoever gathers them from the shallows and the murlocs."]
    if "darkmoon" in low or "prize" in low:
        return ["It is among the prizes of the Darkmoon Faire, won with tickets at Silas Darkmoon's carnival."]
    if "spoils" in low:
        return ["It is among the spoils of the battlegrounds, handed out in sacks to those who fought."]
    if "gift" in low:
        return [f"It comes wrapped in {B.with_article(top)}, a festival present."]
    return [f"It is found inside {B.with_article(top)}, and nowhere else in particular."]


def expand_quest(w, item, entries, fac, R):
    mine = [(q, z) for q, z, f in entries if f is None or f == fac]
    if not mine:
        return [f"It is given only by the {OTHER[fac]}'s questgivers, in thanks for errands a traveller of the {FACTION_NAME[fac]} cannot run."] if entries else []
    if (w.items.get(item) or {}).get("quality") == 5:
        return ["It is forged at the end of a legendary quest chain, and the chain is the story."]
    zones = Counter(z for _, z in mine if z is not None and w.zone_allowed(z, fac))
    if not zones:
        return ["It is given in thanks by a questgiver somewhere in Azeroth, for an errand run."]
    top = [z for z, _ in zones.most_common(2)]
    name, e, dungeon = place(w, top[0])
    out = zones_intro(w, top, R, ["It is earned, not found: a reward for service in {short}.", "It is a reward for service rendered in {short}."])
    if dungeon:
        out.append(f"Those who have a stake in {place_short(w, top[0])} give it to the adventurers who serve their cause there.")
    else:
        out.append(pick(R, [
            f"The folk of {place_short(w, top[0])} have reason to be grateful to adventurers, and this is among what they give in thanks.",
            f"It is given in thanks by those in {place_short(w, top[0])} whose troubles an adventurer takes on.",
        ]))
    return out


def expand_disenchant(w, dids):
    qs, lo, hi = set(), 99, 0
    for did in set(dids):
        for qual, ilvl in w.disenchant_source.get(did, []):
            qs.add(qual)
            lo, hi = min(lo, ilvl), max(hi, ilvl)
    out = ["It is distilled, not found.", T("T", 333, PROFESSIONS[333][1])]
    if hi:
        qnames = B.join_names([B.QUALITY[q] for q in sorted(qs) if q in B.QUALITY])
        band = f"level {lo}" if lo == hi else f"levels {lo}-{hi}"
        out.append(f"This is drawn from {qnames} items of {band}.")
    return out


def expand_start(w, it):
    mask = it.get("allowable_class") or 0
    classes = [n for bit, n in CLASS_NAMES.items() if mask & bit] if mask and mask != -1 else []
    if len(classes) == 1:
        who = classes[0] if classes[0] == "shaman" else classes[0][:-1]
        return [f"It is issued to every young {who} who takes up the path, before they leave their home valley, and most are glad to be rid of it by the second town."]
    return ["It is issued to new adventurers as they set out, and most are glad to be rid of it by the second town."]


def provenance(w, item, it, s, fac, R):
    lines = {}
    if s.get("vendor"):
        lines["vendor"] = B.render_vendor_line(w, item, s["vendor"], fac)
    if s.get("craft"):
        lines["craft"] = B.render_craft_line(w, s["craft"])
    if s.get("object"):
        lines.update(B.render_object_lines(w, item, s["object"], fac))
    if s.get("fish"):
        lines["fish"] = B.render_fish_line(w, s["fish"], fac)
    if s.get("skin"):
        lines["skin"] = B.render_creature_line(w, s["skin"], fac, "skin")
    if s.get("drop"):
        lines["drop"] = B.render_creature_line(w, s["drop"], fac, "drop")
    if s.get("container"):
        lines["container"] = B.render_container_line(w, s["container"])
    if s.get("pick"):
        lines["pick"] = B.render_creature_line(w, s["pick"], fac, "pick")
    if s.get("quest"):
        lines["quest"] = B.render_quest_line(w, item, s["quest"], fac)
    if s.get("disenchant"):
        lines["disenchant"] = B.render_disenchant_line(w, s["disenchant"])
    if s.get("start"):
        lines["start"] = ("Issued to new adventurers as starting equipment.", 40)
    ranked = []
    for i, k in enumerate(B.PRIORITY):
        v = lines.get(k)
        if v:
            ranked.append((-v[1], i, k, v[0]))
    ranked.sort()
    if not ranked:
        return []
    best_strength = -ranked[0][0]
    kind = ranked[0][2]
    out = []
    if kind in ("drop", "skin", "pick"):
        a = analyze_creatures(w, s[kind], fac, kind)
        if a:
            out = expand_drop(w, a, R, fac, kind)
    elif kind == "vendor":
        out = expand_vendor(w, item, s["vendor"], fac, R)
    elif kind == "craft":
        out = expand_craft(w, it, s["craft"], R)
    elif kind in ("herb", "mine", "chest", "other"):
        out = expand_objects(w, item, s["object"], fac, R).get(kind, [])
    elif kind == "fish":
        out = expand_fish(w, s["fish"], fac, R)
    elif kind == "container":
        out = expand_container(w, s["container"], R)
    elif kind == "quest":
        out = expand_quest(w, item, s["quest"], fac, R)
    elif kind == "disenchant":
        out = expand_disenchant(w, s["disenchant"])
    elif kind == "start":
        out = expand_start(w, it)
    for neg, _, k2, text in ranked[1:]:
        strength = -neg
        if k2 == kind or strength < 50 or (best_strength >= 50 and strength <= 12):
            continue
        if text.startswith("While on a quest"):
            continue
        out.append("It is also " + lower_first(text))
        break
    return out


# ---------------------------------------------------------------------------
def compose(w, item, src, fac):
    it = w.items.get(item)
    if not it:
        return None
    if item in BESPOKE:
        name, text = BESPOKE[item]
        if (it.get("name") or "") == name:
            return text["A" if fac == "A" else "H"] if isinstance(text, dict) else text
        if fac == "A":
            print(f"  warning: bespoke {item} expected {name!r} but database has {it.get('name')!r}; skipped", file=sys.stderr)
    # the same seed for both factions, so wording differs only where the facts do
    R = random.Random(item * 7919)
    s = src.get(item, {})
    p1 = nature(w, it, s, R)
    p2 = " ".join(sentence(x) for x in provenance(w, item, it, s, fac, R) if x)
    paras = [p for p in (p1, p2) if p]
    return "\n".join(paras) if paras else None


def compose_both(w, item, src):
    # paragraph 1 does not depend on faction; compute A then reuse the seed for H
    a = compose(w, item, src, "A")
    h = compose(w, item, src, "H")
    return a, h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mangos", required=True)
    ap.add_argument("--pfquest", required=True)
    ap.add_argument("--out", required=True, help="path of WhereIsIt_Lore.lua in the addon folder")
    ap.add_argument("--check", nargs="*", type=int, default=[])
    ap.add_argument("--sample", type=int, default=0, help="print N random entries to stderr")
    args = ap.parse_args()

    print("loading world...", file=sys.stderr)
    w = B.World(args.mangos, args.pfquest)
    src = B.collect_sources(w)
    items = sorted(i for i in src if i in w.items)
    items = [i for i in items if B.render_item(w, i, src[i], "A", 1) or B.render_item(w, i, src[i], "H", 1)]
    print(f"  {len(items)} items with sources", file=sys.stderr)

    if args.check:
        for item in args.check:
            print(f"\n[{item}] {(w.items.get(item) or {}).get('name')}")
            a, h = compose_both(w, item, src)
            for fac, text in (("A", a), ("H", h)):
                if fac == "H" and h == a:
                    print("  --- H: same ---")
                    continue
                print(f"  --- {fac} ---")
                for p in expand_tokens(text or "(nothing)").split("\n"):
                    print("  " + p)
        return

    out_lines = []
    n_split = 0
    lengths = []
    for item in items:
        a, h = compose_both(w, item, src)
        if not a and not h:
            continue
        lengths.append(len(a or h))
        if a == h:
            out_lines.append(f"L[{item}]={B.lua_str(a)}")
        else:
            n_split += 1
            out_lines.append(f"L[{item}]={{A={B.lua_str(a)},H={B.lua_str(h)}}}")
    if args.sample:
        R = random.Random(2)
        for item in R.sample(items, args.sample):
            print(f"\n[{item}] {w.items[item]['name']}", file=sys.stderr)
            for p in expand_tokens(compose(w, item, src, 'A') or '').split("\n"):
                print("  " + p, file=sys.stderr)
    today = dt.date.today().isoformat()
    kb_lines = []
    for kind in sorted(KB):
        kb_lines.append(f"K.{kind}={{}}")
        for key, text in sorted(KB[kind].items()):
            kb_lines.append(f"K.{kind}[{B.lua_str(key)}]={B.lua_str(text)}")
    header = f"""-- WhereIsIt encyclopedia accounts. GENERATED FILE - do not edit by hand.
-- Built {today} by tools/build_lore.py from the same sources as WhereIsIt_Data.lua
-- plus the hand-written knowledge base in tools/lore_world.py, lore_things.py and lore_bespoke.py.
-- Entries: {len(out_lines)} items ({n_split} with separate Alliance/Horde accounts).
-- L[id] = "paragraph\\nparagraph" or {{A=..., H=...}}. Passages shared between entries are
-- stored once in K and referenced as {{kind|key}}; the book expands them when it renders a page.
local _, ns = ...
local L, K = {{}}, {{}}
ns.LoreData, ns.LoreShared = L, K
ns.LoreVersion = "{today}"
"""
    path = args.out
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(header)
        f.write("\n".join(kb_lines))
        f.write("\n")
        f.write("\n".join(out_lines))
        f.write("\n")
    avg = sum(lengths) / max(1, len(lengths))
    nk = sum(len(v) for v in KB.values())
    print(f"wrote {path}: {len(out_lines)} items, {n_split} faction-split, {nk} shared passages, avg {avg:.0f} chars/entry, {os.path.getsize(path)/1e6:.1f} MB", file=sys.stderr)


if __name__ == "__main__":
    main()
