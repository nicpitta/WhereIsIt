# Lore knowledge base for the encyclopedia: places and peoples of Azeroth as they
# stood in the years after the Third War (the world of the original game).
# Written in the voice of an encyclopaedist. Keys are the zone/dungeon names used
# by the world database (area_template) and the creature descriptors produced by
# build_data.describe_creature.

# ZONES[name] = {"desc": ..., "short": noun phrase for mid-sentence use, "waters": optional}
ZONES = {
    "Elwynn Forest": {
        "short": "the woods of Elwynn",
        "desc": "Elwynn Forest is the green heart of the kingdom of Stormwind: oak and elm, "
                "mill-ponds and farmsteads, the Eastvale logging camp and the quiet lake of Crystal Lake. "
                "Its troubles are small ones by the standards of the age, though kobolds squat in the old "
                "Fargodeep and Jasperlode mines and Defias stragglers and Riverpaw gnolls harass the roads "
                "south of Goldshire.",
        "waters": "Crystal Lake, Stone Cairn Lake and the brooks of Elwynn",
    },
    "Westfall": {
        "short": "the fallow farmland of Westfall",
        "desc": "Westfall's wheat once fed Stormwind, but the farms have gone to ruin. When the House of "
                "Nobles refused to pay the masons who rebuilt the city after the Second War, their leader "
                "Edwin VanCleef turned them into the Defias Brotherhood, and the Brotherhood now rules the "
                "homesteads from the Jangolode Mine to Moonbrook. Harvest golems run untended through the "
                "fields, Riverpaw gnolls prowl the Dagger Hills, and the People's Militia at Sentinel Hill "
                "holds what it can.",
        "waters": "the Westfall coast and the Longshore",
    },
    "Redridge Mountains": {
        "short": "the red hills around Lake Everstill",
        "desc": "Redridge is a hard border country of red stone and pine lying between Elwynn and the "
                "orc-held Burning Steppes. Its one town, Lakeshire, stands on Lake Everstill with its bridge "
                "half-built and its garrison stretched thin, for Blackrock orcs raid down from Stonewatch Keep, "
                "the Redridge gnoll packs hold the eastern hills, and murlocs crowd the lakeshore.",
        "waters": "Lake Everstill",
    },
    "Duskwood": {
        "short": "the dark woods of Duskwood",
        "desc": "Duskwood lies under a perpetual twilight. Once it was the sunny Brightwood, but since the "
                "necromancer Morbent Fel settled at Forlorn Rowe above Raven Hill, the dead walk its graveyards, giant spiders web the trees and the worgen "
                "hunt by night. The Night Watch of Darkshire guards the road, and the fallen hero Mor'Ladim "
                "wanders the Raven Hill cemetery.",
    },
    "Stranglethorn Vale": {
        "short": "the jungles of Stranglethorn",
        "desc": "Stranglethorn is the great jungle of the southern Eastern Kingdoms, steaming and loud with "
                "panthers, raptors and parrots. The Gurubashi troll empire once ruled it from Zul'Gurub, and "
                "its descendants, the Bloodscalp and Skullsplitter tribes, war over the ruins. Goblins of the "
                "Steamwheedle Cartel run the port of Booty Bay at the vale's southern tip, the Bloodsail "
                "Buccaneers lurk off the coast, and Nesingwary's camp draws hunters from both factions.",
        "waters": "the rivers and coves of Stranglethorn",
    },
    "Swamp of Sorrows": {
        "short": "the sodden Swamp of Sorrows",
        "desc": "The Swamp of Sorrows is a drowned land of cypress and black water east of Deadwind Pass. "
                "The Horde's Stonard, oldest orc settlement in Azeroth, still stands here, as does the "
                "refuge of the Lost Ones, draenei broken by the journey through the Dark Portal. Beneath its "
                "lake lies the Temple of Atal'Hakkar, where the Atal'ai trolls labour to bring back the "
                "blood god Hakkar.",
        "waters": "the swamp pools and the Pool of Tears",
    },
    "Blasted Lands": {
        "short": "the Blasted Lands",
        "desc": "The Blasted Lands are what the Dark Portal made of the Black Morass: red dust, dead "
                "trees and the hulking stone frame of the Portal itself, guarded now by the Nethergarde Keep "
                "mages of Stormwind. Demons and the Shadowsworn cultists of the Burning Legion haunt the "
                "Tainted Scar, and the ogres of the Dreadmaul clan hold the southern reaches.",
    },
    "Deadwind Pass": {
        "short": "the haunted Deadwind Pass",
        "desc": "Deadwind Pass is a shunned gorge between Duskwood and the Swamp of Sorrows, overlooked "
                "by the sealed tower of Karazhan, where the Guardian Medivh once lived and died. Nothing "
                "wholesome grows there; the Deadwind ogres and the ghosts of the tower's household are its "
                "only tenants.",
    },
    "Burning Steppes": {
        "short": "the ash plains of the Burning Steppes",
        "desc": "The Burning Steppes are a scorched plain of cinders and lava flows in the shadow of "
                "Blackrock Mountain. The Blackrock orcs under the black dragon Nefarian's sway rule it from "
                "their camps and the Dreadmaul Rock ogres hold the east, while the Thorium Brotherhood dwarves "
                "maintain their forge at Flame Crest and Morgan's Vigil keeps a Stormwind watch on the pass "
                "to Redridge.",
    },
    "Searing Gorge": {
        "short": "the smoking Searing Gorge",
        "desc": "Searing Gorge is a black bowl of slag and heat north of Blackrock Mountain, mined for "
                "centuries by the Dark Iron dwarves and now worked by their slaves. The Thorium Brotherhood, "
                "Dark Irons who broke with their emperor, trade from Thorium Point, and the gorge's heat "
                "breeds fire elementals and gigantic lava spiders.",
    },
    "Badlands": {
        "short": "the Badlands",
        "desc": "The Badlands are a wasteland of red rock and dust east of Loch Modan, broken by the ruin "
                "of Uldaman, a Titan vault the Dark Iron dwarves and the Shadowforge have dug into. Black "
                "dragonkin nest at Lethlor Ravine, ogres and the Rock Elemental roam the canyons, and the "
                "goblins of Kargath keep an outpost for the Horde.",
    },
    "Loch Modan": {
        "short": "the loch country of Loch Modan",
        "desc": "Loch Modan is a cold, pleasant valley of pine and granite east of Ironforge, held by the "
                "great Stonewrought Dam and the lake it makes. Dwarves hold Thelsamar and the Explorers' "
                "League digs in the south, but the Stonesplinter and Mo'grosh troggs and ogres have grown "
                "bold since Gnomeregan fell, and the Dark Irons stir in the hills.",
        "waters": "the Loch",
    },
    "Dun Morogh": {
        "short": "the snowfields of Dun Morogh",
        "desc": "Dun Morogh is the snowbound homeland of the Bronzebeard dwarves and the gnome refugees of "
                "Gnomeregan, a white valley of pines ringed by mountains, with Ironforge at its heart. Frostmane "
                "trolls hold the western caves, Rockjaw troggs infest the mines, and wendigo haunt the "
                "frozen tunnels; even so, its hunters and brewers count it a gentle land.",
        "waters": "Iceflow Lake and the frozen pools of Dun Morogh",
    },
    "Wetlands": {
        "short": "the marshes of the Wetlands",
        "desc": "The Wetlands are a grey, rain-soaked fen north of Dun Algaz, where the dwarven port of "
                "Menethil Harbor keeps the Alliance's only sea road to Kalimdor. Crocolisks and raptors fill "
                "the marsh, the Dragonmaw orcs hold Grim Batol's approaches, and the murlocs and the "
                "Bluegill tribe swarm the coast; Dark Iron excavations at Dun Modr keep the dwarves anxious.",
        "waters": "the Wetlands marsh and Baradin Bay",
    },
    "Arathi Highlands": {
        "short": "the Arathi Highlands",
        "desc": "The Arathi Highlands are rolling grassland and limestone where the first human kingdom, "
                "Arathor, was founded; the ruins of Stromgarde still stand on its western edge, divided "
                "between the kingdom's last loyalists, the Syndicate and the Boulderfist ogres. The Horde's "
                "Hammerfall rises in the east on the bones of the old internment camp, and the Witherbark "
                "trolls hold the southern hills.",
    },
    "Hillsbrad Foothills": {
        "short": "the farmland of Hillsbrad",
        "desc": "Hillsbrad is green farming country south of Lordaeron's ruins, contested daily between the "
                "Alliance town of Southshore and the Forsaken garrison at Tarren Mill. The yeti of Alterac "
                "come down from the hills, the Syndicate holds Durnholde Keep, and murlocs infest the coast.",
        "waters": "the Hillsbrad coast and its mill streams",
    },
    "Alterac Mountains": {
        "short": "the Alterac Mountains",
        "desc": "The Alterac Mountains are the cold, ruined homeland of a kingdom destroyed for treason in "
                "the Second War. The Syndicate, its former nobles turned bandits, haunts the ruined city, "
                "Crushridge ogres hold the heights, yeti and winter wolves the slopes, and in the deepest "
                "valley the Frostwolf orcs and Stormpike dwarves fight their endless war.",
        "waters": "Lordamere Lake and Lake Dalaran",
    },
    "Silverpine Forest": {
        "short": "the grey woods of Silverpine",
        "desc": "Silverpine is a fog-bound forest of silver-barked pines west of Tirisfal, where the "
                "Forsaken's Sepulcher stands against Dalaran's agents at Ambermill, the Rot Hide gnolls, and "
                "the worgen that the mage Arugal summoned to Shadowfang Keep. Sons of Arugal roam the "
                "roads, and the Greymane Wall seals the south.",
        "waters": "Lordamere Lake and the Silverpine coast",
    },
    "Tirisfal Glades": {
        "short": "the blighted glades of Tirisfal",
        "desc": "Tirisfal Glades is the northern forest of the fallen kingdom of Lordaeron, now the home of "
                "the Forsaken. Below the ruined capital lies the Undercity, Lady Sylvanas's seat; above, the "
                "Scarlet Crusade holds the Monastery and its outposts, mindless Scourge still shamble "
                "through Agamand Mills and Brill's dead rest uneasily.",
        "waters": "Brightwater Lake",
    },
    "Western Plaguelands": {
        "short": "the Western Plaguelands",
        "desc": "The Western Plaguelands are what the Scourge left of Lordaeron's richest farmland: grey "
                "grass, plague cauldrons and the shattered towns of Andorhal and Hearthglen. The Argent Dawn "
                "holds Chillwind Camp against the undead, the Scarlet Crusade holds Hearthglen, and beneath "
                "Caer Darrow the school of necromancy called Scholomance raises the dead for the Lich King.",
        "waters": "Darrowmere Lake",
    },
    "Eastern Plaguelands": {
        "short": "the Eastern Plaguelands",
        "desc": "The Eastern Plaguelands are the Scourge's own country: orange skies, fungal growths and "
                "the ruined city of Stratholme, where Prince Arthas first damned himself. The Argent Dawn keeps "
                "Light's Hope Chapel, the Scarlet Crusade keeps Tyr's Hand, and everywhere else the ziggurats "
                "and plague cauldrons of the Cult of the Damned hold sway.",
    },
    "The Hinterlands": {
        "short": "the Hinterlands",
        "desc": "The Hinterlands are a high, forested shelf between Alterac and the sea, home of the "
                "Wildhammer dwarves and their gryphons at Aerie Peak. The Vilebranch and Witherbark forest "
                "trolls hold the eastern hills and the troll city of Jintha'Alor, the Horde's Revantusk trolls "
                "keep a village on the coast, and owlbeasts and wolves fill the woods.",
        "waters": "the Hinterlands coast and its mountain streams",
    },
    "Stormwind City": {
        "short": "the city of Stormwind",
        "desc": "Stormwind is the capital of the Alliance in the Eastern Kingdoms, rebuilt in white stone "
                "after the orcs burned it in the First War. Its Trade District, Dwarven District and Mage "
                "Quarter hold every craft and guild, and the Cathedral of Light and Stormwind Keep stand over "
                "all; under the Keep, the Stockade holds Defias prisoners in revolt.",
        "waters": "the canals of Stormwind",
    },
    "Ironforge": {
        "short": "the dwarven city of Ironforge",
        "desc": "Ironforge is the mountain-city of the Bronzebeard dwarves, carved into the heart of "
                "Khaz Modan with the Great Forge at its centre. The gnomes of Tinker Town shelter there "
                "since the fall of Gnomeregan, and the Deeprun Tram links it to Stormwind.",
    },
    "Darnassus": {
        "short": "the night elf city of Darnassus",
        "desc": "Darnassus is the night elves' new capital, built in the boughs of the World Tree "
                "Teldrassil after the Third War. Its temples to Elune and the Cenarion enclave look out "
                "over quiet lakes, and from Rut'theran Village below the boat sails to Darkshore.",
    },
    "Teldrassil": {
        "short": "the boughs of Teldrassil",
        "desc": "Teldrassil is the World Tree raised by the druids off the coast of Kalimdor, so vast that "
                "a whole forest grows on its crown. Its glades are wholesome for the most part, but the "
                "Gnarlpine furbolg have turned savage, timberlings and webwood spiders grow strange, and the "
                "druids fret about a corruption at the roots.",
        "waters": "the lakes and pools of Teldrassil",
    },
    "Darkshore": {
        "short": "the stormy coast of Darkshore",
        "desc": "Darkshore is a grey, wind-scoured coast of ruined night elf towers north of Ashenvale, "
                "served by the port of Auberdine. Naga of the Hatecrest hold the sea caves, the Blackwood furbolg have been corrupted, and the Greymist murlocs crowd the beaches "
                "among wrecks the storms throw up.",
        "waters": "the Veiled Sea off Darkshore",
    },
    "Ashenvale": {
        "short": "the ancient forest of Ashenvale",
        "desc": "Ashenvale is the night elves' ancestral forest, a cathedral of ancient trees where "
                "Astranaar and the Sentinels hold against the Horde's Warsong lumber camp and the Splintertree "
                "outpost. The Thistlefur and Foulweald furbolg have gone wild, the satyrs of Xavian and "
                "Satyrnaar corrupt the eastern woods, and the demon-tainted Felfire Hill smoulders near "
                "Demon Fall Canyon, where Grom Hellscream fell.",
        "waters": "Lake Falathim, the Falfarren River and Mystral Lake",
    },
    "Stonetalon Mountains": {
        "short": "the Stonetalon Mountains",
        "desc": "The Stonetalon Mountains rise between Ashenvale and Desolace, their peaks holding Stonetalon "
                "Peak, where the druid Keeper Ordanus and the Talon Den dwell. The Venture Company strips the "
                "forest at Windshear Crag, the Horde holds Sun Rock Retreat, and the Grimtotem tauren and "
                "harpies hold the heights.",
    },
    "Desolace": {
        "short": "the grey wastes of Desolace",
        "desc": "Desolace is a dead, grey land between Stonetalon and Feralas, where the centaur clans "
                "Kolkar, Magram and Gelkis wage their endless war of extermination and the Burning Blade cult "
                "holds Mannoroc Coven. The Kodo Graveyard and the demon-haunted ruins of Maraudon lie within "
                "it, and both factions keep lonely posts at Nijel's Point and Shadowprey Village.",
        "waters": "the Sar'theris Strand",
    },
    "Feralas": {
        "short": "the rainforest of Feralas",
        "desc": "Feralas is a lush, rainy highland forest in southwestern Kalimdor, scattered with the ruins "
                "of the Highborne. The Gordunni ogres hold the great ruined city of Dire Maul, the Grimtotem "
                "and Woodpaw gnolls roam the valleys, and the night elves keep Feathermoon Stronghold on the "
                "western isle while the Horde holds Camp Mojache in the east. Hippogryphs and giants are common.",
        "waters": "the Verdantis River and the Forgotten Coast",
    },
    "Dustwallow Marsh": {
        "short": "the mists of Dustwallow Marsh",
        "desc": "Dustwallow Marsh is a steaming swamp on Kalimdor's eastern coast, dominated by Lady Jaina "
                "Proudmoore's island city of Theramore. The Horde's ogre allies of the Stonemaul clan hold "
                "Brackenwall Village, the black dragonflight nests at the Wyrmbog, and beneath the marsh "
                "Onyxia's own lair lies hidden.",
        "waters": "the dark pools of Dustwallow",
    },
    "The Barrens": {
        "short": "the savannah of the Barrens",
        "desc": "The Barrens are the great golden savannah at the centre of Kalimdor, the Horde's "
                "heartland between Durotar and Mulgore. The Crossroads sits on its spine, the goblin port of "
                "Ratchet trades with everyone, and the Razormane and Bristleback quilboar, Kolkar centaur, "
                "harpies and Venture Company encroach from every side. Plainstriders, zhevra and lions roam "
                "the grass, and beneath it lie the Wailing Caverns.",
        "waters": "the Southfury River and the Merchant Coast",
    },
    "Durotar": {
        "short": "the red desert of Durotar",
        "desc": "Durotar is the harsh red land Thrall chose for the new Horde after the Third War, named for "
                "his father. Orgrimmar rises from its northern canyons, the trolls of the Darkspear tribe hold "
                "Sen'jin Village on the coast, and Razor Hill drills the Horde's young. Scorpids and boars "
                "live on its scrub, and the Burning Blade cult festers in Skull Rock.",
        "waters": "the Southfury River and the coast of Durotar",
    },
    "Mulgore": {
        "short": "the plains of Mulgore",
        "desc": "Mulgore is the grassy, mesa-ringed homeland the tauren finally won from the centaur with "
                "the Horde's help, with Thunder Bluff rising on its great mesa and Bloodhoof Village on the "
                "lake. Kodo herds, prairie wolves and plainstriders cover the plains, Palemane gnolls and "
                "Bristleback quilboar trouble the edges, and the Venture Company mines near the Windfury "
                "harpy roost.",
        "waters": "Stonebull Lake",
    },
    "Thousand Needles": {
        "short": "the mesas of Thousand Needles",
        "desc": "Thousand Needles is a dry canyon of red stone spires south of the Barrens, where the "
                "tauren keep Freewind Post atop the mesas and the Grimtotem plot below. Galak centaur hold the "
                "canyon floor, and at its southern end the salt flats of the Shimmering Flats hold the "
                "goblin and gnome racetrack of Mirage Raceway.",
    },
    "Tanaris": {
        "short": "the desert of Tanaris",
        "desc": "Tanaris is a vast sand desert on Kalimdor's southern coast, ruled by the Steamwheedle "
                "goblins from Gadgetzan and the pirate port of Steamwheedle. The Wastewander nomads hold the "
                "watering holes, Southsea pirates the Lost Rigger Cove, and the Sandfury trolls their city of "
                "Zul'Farrak; the Caverns of Time lie hidden in the eastern mountains, and the silithid gather "
                "in the Noxious Lair.",
        "waters": "the Tanaris coast and the oases of the Noonshade",
    },
    "Un'Goro Crater": {
        "short": "the jungle crater of Un'Goro",
        "desc": "Un'Goro Crater is a vast volcanic bowl walled off from Tanaris and Silithus, its floor a "
                "primordial jungle of devilsaurs, stegodons and giant insects. The Titans seem to have shaped "
                "it, for crystal pylons stand in its corners and the mysterious caretakers of the "
                "crater's heart tend it; Marshal's Refuge is its only camp.",
        "waters": "the lakes and streams of Un'Goro",
    },
    "Silithus": {
        "short": "the sands of Silithus",
        "desc": "Silithus is the insect-haunted desert in Kalimdor's far southwest, where the silithid hives "
                "boil up from the ground and the Twilight's Hammer cult courts the Old Gods. The Cenarion "
                "Circle holds Cenarion Hold against them, and behind the Scarab Wall lie the ruins and the "
                "temple of Ahn'Qiraj, where the qiraji wait.",
    },
    "Felwood": {
        "short": "the poisoned forest of Felwood",
        "desc": "Felwood is a forest poisoned by the Burning Legion's passage during the Third War, its "
                "trees weeping fel, its streams green and its furbolg, the Deadwood and Felpaw, driven mad. "
                "The Shadow Council's cultists of Jaedenar work demons there, Timbermaw furbolg hold the pass "
                "north to Winterspring, and the Emerald Circle druids labour to cleanse what they can.",
    },
    "Winterspring": {
        "short": "the snows of Winterspring",
        "desc": "Winterspring is a high snowbound valley in Kalimdor's northeast, reached only through the "
                "Timbermaw tunnels. Goblins of Everlook trade in its centre, the Winterfall furbolg brew their "
                "firewater, frostsabers and chimaera hunt the slopes, and the blue dragonflight guards Mazthoril "
                "under the frozen lake.",
        "waters": "Lake Kel'Theril",
    },
    "Azshara": {
        "short": "the fallen coast of Azshara",
        "desc": "Azshara is the shattered coast of the old Highborne empire, its red-leaved forest strewn "
                "with ruined temples where the ghosts of elves still argue. Naga of the Spitelash hold the "
                "shore and the Ruins of Eldarath, the blue dragon Azuregos guards the southern coast, and the Horde's Valormok and the Alliance's "
                "Talrendis Point watch each other across the ravines.",
        "waters": "the Bay of Storms",
    },
    "Moonglade": {
        "short": "the sanctuary of Moonglade",
        "desc": "Moonglade is the druids' sanctuary in northern Kalimdor, a peaceful lakeside glade where "
                "the Cenarion Circle gathers in Nighthaven, tauren and night elf druids study together and the "
                "great bear spirit of Remulos presides. Nothing hostile lives there by anyone's leave.",
        "waters": "Lake Elune'ara",
    },
    "Orgrimmar": {
        "short": "the Horde capital of Orgrimmar",
        "desc": "Orgrimmar is Thrall's capital, raised in the red canyons of Durotar and named for Orgrim "
                "Doomhammer. Its Valley of Strength, Drag and Valley of Spirits hold the Horde's merchants and "
                "trainers, and the Cleft of Shadow leads down to Ragefire Chasm, where the Burning Blade "
                "plots in secret.",
    },
    "Thunder Bluff": {
        "short": "the mesa city of Thunder Bluff",
        "desc": "Thunder Bluff is the tauren capital, a city of tents and totems atop a great mesa in "
                "Mulgore, reached by lifts from the plain below. Its rises hold the druids, hunters and "
                "shaman of the tribes, and its markets trade in hides, herbs and kodo.",
    },
    "Undercity": {
        "short": "the Undercity",
        "desc": "The Undercity is the Forsaken capital, dug beneath the ruins of Lordaeron's palace. Its "
                "canals run with green slime, its Apothecarium brews plagues, and its merchants sell to "
                "any of the Horde who can stomach the air.",
    },
    "Blackrock Mountain": {
        "short": "Blackrock Mountain",
        "desc": "Blackrock Mountain is the volcano that rose when the Dark Iron dwarves summoned Ragnaros, "
                "standing between the Burning Steppes and Searing Gorge. The Dark Irons hold the Depths "
                "below, the Blackrock orcs the Spire above, and in the fires beneath the Firelord waits.",
    },
    "Deeprun Tram": {
        "short": "the Deeprun Tram",
        "desc": "The Deeprun Tram is the gnomish railway running under the sea between Stormwind and "
                "Ironforge, lit by its own power and occasionally by escaped rats.",
    },
    "Dire Maul": {
        "short": "the ruins of Dire Maul",
        "desc": "Dire Maul is the ruined Highborne city of Eldre'Thalas in Feralas, where the Gordunni ogres "
                "squat in the arena and the Shen'dralar elves, kept alive by the imprisoned demon Immol'thar, "
                "haunt the libraries.",
    },
}

# Dungeons and raids. "masters" names the kind of foe whose hoard the great items come from.
DUNGEONS = {
    "Ragefire Chasm": {
        "short": "Ragefire Chasm",
        "desc": "Ragefire Chasm is the volcanic cavern beneath Orgrimmar's Cleft of Shadow, where the Burning "
                "Blade cult and the Searing Blade troggs plot against Thrall under the very feet of the Horde.",
        "masters": "the Searing Blade's leaders and their demon-tainted allies",
    },
    "Wailing Caverns": {
        "short": "the Wailing Caverns",
        "desc": "The Wailing Caverns are a cave system beneath the Barrens where the druid Naralex tried to "
                "dream a new forest into being and fell into a nightmare. His Druids of the Fang went mad, "
                "and the caverns teem with deviate creatures twisted by the dream.",
        "masters": "the Druids of the Fang and the nightmare's great serpents",
    },
    "The Deadmines": {
        "short": "the Deadmines",
        "desc": "The Deadmines beneath Moonbrook in Westfall are the Defias Brotherhood's stronghold, where "
                "Edwin VanCleef's masons and goblin shipwrights are building a warship in the flooded "
                "heart of the mine.",
        "masters": "the Defias captains and VanCleef himself",
    },
    "Shadowfang Keep": {
        "short": "Shadowfang Keep",
        "desc": "Shadowfang Keep in Silverpine was the baron's castle until the mage Arugal fled there "
                "with the worgen he had summoned. Its halls hold the cursed Sons of Arugal, the ghosts of "
                "the baron's household and the Dalaran apprentice who followed Arugal into madness.",
        "masters": "Arugal and the keep's cursed lords",
    },
    "Blackfathom Deeps": {
        "short": "Blackfathom Deeps",
        "desc": "Blackfathom Deeps is a drowned temple of Elune on the Darkshore coast, taken by the naga "
                "and the Twilight's Hammer cult, who worship the Old God's servant Aku'mai in its depths.",
        "masters": "the naga priestesses and the Twilight cultists who serve Aku'mai",
    },
    "The Stockade": {
        "short": "the Stockade",
        "desc": "The Stockade is Stormwind's prison beneath the Canals, where Defias convicts under "
                "Bazil Thredd have overpowered the guards and hold the cells.",
        "masters": "the ringleaders of the prison revolt",
    },
    "Gnomeregan": {
        "short": "Gnomeregan",
        "desc": "Gnomeregan was the gnomes' great city under Dun Morogh until the trogg invasion drove "
                "Mekgineer Thermaplugg to flood it with radiation. Leper gnomes, troggs and runaway machines "
                "now hold its halls.",
        "masters": "Thermaplugg and the machines he set against his own people",
    },
    "Razorfen Kraul": {
        "short": "Razorfen Kraul",
        "desc": "Razorfen Kraul is the quilboar's thorn-walled warren at the southern edge of the Barrens, "
                "grown from the bones of the demigod Agamaggan. The Death's Head tribe rules it with "
                "boars, bats and dark shamanism.",
        "masters": "the Death's Head chieftains",
    },
    "Razorfen Downs": {
        "short": "Razorfen Downs",
        "desc": "Razorfen Downs is the quilboar's sacred burial warren, where the Scourge has installed "
                "the lich Amnennar the Coldbringer and raised the dead quilboar as his army.",
        "masters": "Amnennar the Coldbringer and the Death's Head he corrupted",
    },
    "Scarlet Monastery": {
        "short": "the Scarlet Monastery",
        "desc": "The Scarlet Monastery in Tirisfal is the fortress-abbey of the Scarlet Crusade, zealots who "
                "hunt the undead and anyone else they judge tainted. Its graveyard, library, armory and "
                "cathedral are each garrisoned by the Crusade's elite.",
        "masters": "the Crusade's commanders and the abbot Mograine",
    },
    "Uldaman": {
        "short": "Uldaman",
        "desc": "Uldaman is a Titan vault in the Badlands, excavated by the Explorers' League and the Dark "
                "Iron dwarves alike. Troggs and stone constructs guard its halls, and the Titan's keeper "
                "Archaedas sleeps at its heart with the Discs of Norgannon.",
        "masters": "the vault's Titan guardians and the Dark Iron overseers",
    },
    "Zul'Farrak": {
        "short": "Zul'Farrak",
        "desc": "Zul'Farrak is the sandstone city of the Sandfury trolls in northern Tanaris, where the "
                "hydra Gahz'rilla sleeps in the sacred pool and the witch doctors raise troll dead.",
        "masters": "the Sandfury chieftains and the hydra of their pool",
    },
    "Maraudon": {
        "short": "Maraudon",
        "desc": "Maraudon is the great cavern-temple of the centaur in Desolace, tomb of their ancestress "
                "Theradras, the earth elemental who bore the first centaur to the demigod Zaetar. Satyrs, "
                "corrupted elementals and the centaur's own Maraudine guard it.",
        "masters": "Princess Theradras and the celebrants of the centaur",
    },
    "Sunken Temple": {
        "short": "the Temple of Atal'Hakkar",
        "desc": "The Temple of Atal'Hakkar lies drowned beneath the Swamp of Sorrows, sunk by the green "
                "dragonflight to stop the Atal'ai trolls summoning the blood god Hakkar. The Atal'ai still "
                "labour there among green drakes gone mad.",
        "masters": "the Atal'ai high priests and the shade of Hakkar",
    },
    "The Temple of Atal'Hakkar": {
        "short": "the Temple of Atal'Hakkar",
        "desc": "The Temple of Atal'Hakkar lies drowned beneath the Swamp of Sorrows, sunk by the green "
                "dragonflight to stop the Atal'ai trolls summoning the blood god Hakkar.",
        "masters": "the Atal'ai high priests and the shade of Hakkar",
    },
    "Blackrock Depths": {
        "short": "Blackrock Depths",
        "desc": "Blackrock Depths is the Dark Iron city under Blackrock Mountain: the Shadowforge, the "
                "Ring of Law, the Grim Guzzler tavern and the throne of Emperor Dagran Thaurissan, who "
                "holds the dwarven princess Moira as his bride.",
        "masters": "Emperor Thaurissan and the Dark Iron senate",
    },
    "Blackrock Spire": {
        "short": "Blackrock Spire",
        "desc": "Blackrock Spire is the upper fortress of Blackrock Mountain, where the Blackrock orcs "
                "under Warchief Rend Blackhand serve the black dragon Nefarian, alongside Smolderthorn trolls, "
                "Spirestone ogres and the dragonspawn of the black flight.",
        "masters": "Rend Blackhand, General Drakkisath and the Spire's warlords",
    },
    "Stratholme": {
        "short": "Stratholme",
        "desc": "Stratholme is the burned city where Arthas culled his own people. Its western half is "
                "held by the Scarlet Crusade under Grand Crusader Dathrohan, its eastern half by the Scourge "
                "under Baron Rivendare, and plague and fire never leave its streets.",
        "masters": "Baron Rivendare, the Scarlet commanders and the city's death knights",
    },
    "Scholomance": {
        "short": "Scholomance",
        "desc": "Scholomance is the school of necromancy in the crypts beneath Caer Darrow, where the "
                "Cult of the Damned trains its necromancers under Darkmaster Gandling and the lich Ras "
                "Frostwhisper.",
        "masters": "Darkmaster Gandling and the school's lich instructors",
    },
    "Molten Core": {
        "short": "the Molten Core",
        "desc": "The Molten Core is the heart of Blackrock Mountain, the lava sea where Ragnaros the "
                "Firelord has been imprisoned since the Dark Irons summoned him. Flamewaker lieutenants, core "
                "hounds and fire giants guard him, and Majordomo Executus keeps his court.",
        "masters": "Ragnaros and his flamewaker lieutenants",
    },
    "Onyxia's Lair": {
        "short": "Onyxia's Lair",
        "desc": "Onyxia's Lair is the brood-cave of the black dragon Onyxia, hidden beneath Dustwallow Marsh. "
                "In human guise she sat on Stormwind's council as Lady Katrana Prestor until she was unmasked.",
        "masters": "Onyxia, Broodmother of the black dragonflight",
    },
    "Blackwing Lair": {
        "short": "Blackwing Lair",
        "desc": "Blackwing Lair is Nefarian's seat at the peak of Blackrock Spire, where the son of "
                "Deathwing breeds the chromatic dragonflight from the eggs of every other flight.",
        "masters": "Nefarian and the lords of the black dragonflight",
    },
    "Zul'Gurub": {
        "short": "Zul'Gurub",
        "desc": "Zul'Gurub is the ancient capital of the Gurubashi trolls in Stranglethorn, where the "
                "Hakkari priesthood has succeeded in summoning the blood god Hakkar the Soulflayer and the "
                "high priests of the troll animal gods have fallen to him.",
        "masters": "Hakkar the Soulflayer and his high priests",
    },
    "Ruins of Ahn'Qiraj": {
        "short": "the Ruins of Ahn'Qiraj",
        "desc": "The Ruins of Ahn'Qiraj are the outer city of the qiraji in Silithus, opened when the Scarab "
                "Wall fell. Silithid and qiraji warriors swarm its courts under the prophet Ossirian the Unscarred.",
        "masters": "Ossirian the Unscarred and the qiraji generals",
    },
    "Ahn'Qiraj": {
        "short": "the Temple of Ahn'Qiraj",
        "desc": "The Temple of Ahn'Qiraj is the inner city of the qiraji, where the Twin Emperors rule in "
                "the name of the Old God C'Thun, who stirs beneath the temple floor.",
        "masters": "the Twin Emperors and C'Thun itself",
    },
    "Naxxramas": {
        "short": "Naxxramas",
        "desc": "Naxxramas is the floating necropolis of the lich Kel'Thuzad, anchored over the Eastern "
                "Plaguelands. Its wings hold the Scourge's plague works, spider breeders, the Four Horsemen "
                "and the frost wyrm Sapphiron.",
        "masters": "Kel'Thuzad and the Four Horsemen",
    },
}

# PEOPLES[descriptor] = sentences about a humanoid, undead, demonic or other group
PEOPLES = {
    "Defias brigands": "The Defias Brotherhood began as the Stonemasons' Guild, the men who rebuilt Stormwind "
                       "and were cheated of their pay. Under Edwin VanCleef they turned to banditry in Westfall "
                       "and Elwynn, and their red bandanas mark every highwayman and pillager between Moonbrook "
                       "and the Stockade.",
    "kobolds": "Kobolds are small, rat-like diggers who infest abandoned mines across the human and dwarven "
               "kingdoms, hoarding candles, ore and whatever travellers drop. They are cowards alone and "
               "dangerous in numbers.",
    "gnolls": "Gnolls are hyena-headed raiders who live by plunder; the Riverpaw and Redridge packs trouble "
              "Stormwind's lands, the Rot Hide serve the Scourge in Silverpine, and the Woodpaw and Palemane "
              "roam Kalimdor. What they steal they rarely keep in good repair.",
    "murlocs": "Murlocs are amphibious fish-folk who have spread along every coast of Azeroth in the last "
               "generation, for reasons no one has fathomed. They gather trinkets from the shallows and the "
               "drowned, and their oracles hoard the stranger finds.",
    "the Lost Ones": "The Lost Ones are draenei who came through the Dark Portal with the Horde's exodus and "
                     "were twisted by the journey, now scattered in the Swamp of Sorrows and the Blasted Lands.",
    "Dalaran wizards": "The mages of Dalaran, the Kirin Tor, keep agents and apprentices across Lordaeron's "
                       "ruins, studying the Scourge and the worgen curse at Ambermill and in Silverpine.",
    "trolls": "The trolls of Azeroth are an ancient people fallen from empire: the Gurubashi jungle tribes of "
              "Stranglethorn, the Amani and Witherbark forest trolls of the north, the Sandfury of Tanaris and "
              "the Frostmane of Dun Morogh. Save for the Darkspear, who joined the Horde, they are enemies of "
              "all, and their witch doctors and headhunters carry the fetishes and coins of their victims.",
    "harpies": "Harpies are winged, bird-footed women who nest on the cliffs of Kalimdor in matriarchal roosts, "
               "the Bloodfury, Witchwing and Windfury among them. They steal shiny things and carry them to "
               "their aeries.",
    "ogres": "Ogres came to Azeroth with the Horde and stayed when it fell, forming clans of their own: the "
             "Boulderfist and Crushridge in the north, the Dunemaul of Tanaris, the Gordunni of Feralas and the "
             "Stonemaul of Dustwallow. They are strong, dull and acquisitive, and their camps are heaped with loot.",
    "centaur": "The centaur are the half-horse children of the earth elemental Theradras and the demigod "
               "Zaetar, who have warred on the tauren and on each other for a thousand years. The Kolkar, "
               "Magram, Gelkis, Galak and Maraudine clans each carry the spoils of their raids.",
    "quilboar": "The quilboar are boar-like people who hold the thorny warrens of Razorfen and the bramble "
                "camps of the Barrens and Mulgore, worshipping the dead demigod Agamaggan from whose blood they "
                "say the thorns grew. The Razormane, Bristleback and Death's Head tribes raid the Horde constantly.",
    "furbolg": "Furbolg are great bear-folk of Kalimdor's forests, once gentle. The Legion's corruption during "
               "the Third War drove the Gnarlpine, Thistlefur, Foulweald and Deadwood tribes to savagery, and "
               "only the Timbermaw and the Stillpine remain sane.",
    "naga": "The naga are the Highborne who sank with Queen Azshara's palace and were transformed by the Old "
            "Gods into sea-serpent folk. They have begun to return to the coasts of Kalimdor and Lordaeron, "
            "and their sirens and myrmidons carry the salvage of ten thousand years under the sea.",
    "Dark Iron dwarves": "The Dark Iron dwarves broke from Ironforge in the War of the Three Hammers and, "
                         "losing, summoned Ragnaros into Blackrock Mountain. From Shadowforge City their "
                         "emperor's armies hold the Searing Gorge, the Badlands and the Depths, and their "
                         "smiths are the finest in Azeroth after the Firelord's own.",
    "Scarlet Crusaders": "The Scarlet Crusade is the order of zealots who rose from Lordaeron's ruin to purge the "
                         "undead, and in time any living person they suspect of taint. From the Monastery, "
                         "Hearthglen, Tyr's Hand and the Bastion of Stratholme they war with the Forsaken, the "
                         "Scourge and the Argent Dawn alike.",
    "Syndicate rogues": "The Syndicate is the remnant of the nobility of Alterac, the kingdom dissolved for "
                        "treason in the Second War, turned to brigandage. They hold Durnholde and the ruins of "
                        "Alterac and Stromgarde, and they rob with the manners of the gentry they once were.",
    "Twilight's Hammer cultists": "The Twilight's Hammer were once an orc clan and are now a cult of every race, "
                                  "worshipping the Old Gods and working for the end of the world. They gather "
                                  "in Silithus, in Blackfathom Deeps and wherever elemental lords stir.",
    "cultists": "The cults of the Burning Legion, the Burning Blade and the Shadow Council and the Cult of the "
                "Damned among them, draw the ambitious and the desperate from every race. Their acolytes carry "
                "the reagents and the stolen goods of their rites.",
    "pirates": "The Bloodsail Buccaneers and Southsea Freebooters are the pirate fleets of the South Seas, at "
               "feud with the Steamwheedle goblins over Booty Bay and the Tanaris coast. Their holds are full of "
               "everything the trade routes carry.",
    "bandits": "Bandits, highwaymen and marauders of every stripe plague the roads between settlements, and "
               "what they take from travellers they carry until someone takes it back.",
    "Venture Company workers": "The Venture Company is a goblin trading company that strips forests and mines "
                               "wherever it can plant a shredder, in Stonetalon, the Barrens, Mulgore and the "
                               "Hinterlands, with hired muscle of every race to guard the profits.",
    "Grimtotem tauren": "The Grimtotem are the tauren tribe under Magatha Grimtotem that rejects the Horde and "
                        "plots to rule Mulgore alone. Their camps in Stonetalon, Thousand Needles and Feralas "
                        "are hostile to everyone.",
    "Blackrock orcs": "The Blackrock clan was the backbone of the old Horde and never surrendered. Under Rend "
                      "Blackhand and the black dragon Nefarian they hold Blackrock Spire and raid the Burning "
                      "Steppes and Redridge.",
    "Dragonmaw orcs": "The Dragonmaw clan enslaved the red dragonflight in the Second War and still holds the "
                      "approaches to Grim Batol in the Wetlands, keeping to the old ways.",
    "Wastewander nomads": "The Wastewander are human bandits who hold the water holes of Tanaris against the "
                          "goblins of Gadgetzan, robbing caravans on the desert road.",
    "troggs": "Troggs are the stunted, brutish cousins of the dwarves, Titan-made things that burrowed up from "
              "the deep when Uldaman was opened and have overrun Gnomeregan and the mines of Khaz Modan.",
    "leper gnomes": "The leper gnomes are the survivors of Gnomeregan's irradiation, driven mad and loyal to "
                    "the usurper Thermaplugg, still tinkering in the ruined city's halls.",
    "worgen": "The worgen are wolf-men summoned from another world by the mage Arugal to fight the Scourge, "
              "who turned on their summoners and spread through Silverpine and Duskwood.",
    "townsfolk and militia": "Farmers, miners, militiamen and the ordinary folk of the frontier settlements, "
                             "some of them driven to violence by plague, possession or desperation.",
    "goblins": "The goblins of the Steamwheedle, Venture and other cartels are neutral in the great war and "
               "loyal only to profit, and their bruisers and tinkers are armed accordingly.",
    "elves": "The night elves of the Sentinels and the Highborne remnants of Azshara and Eldre'Thalas, and "
             "those elves who have fallen under the sway of the nightmare or the demons.",
    "dwarves": "The dwarves of Khaz Modan and the Wildhammer clans of the Hinterlands, stubborn, hardy and "
               "fond of good steel.",
    "orcs": "The orcs of the new Horde and the renegade clans, the Warsong and the Bleeding Hollow among them, "
            "warriors who carry the trophies of their fights.",
    "tauren": "The tauren of the plains, great horned nomads who honour the Earth Mother and carry the "
              "hides, totems and herbs of their craft.",
    "soldiers and mercenaries": "Soldiers, deserters and hired blades of every banner, whose kit is whatever "
                                "their last paymaster issued.",
    "spellcasters": "Mages, warlocks, shadow priests and witch doctors of a dozen orders and tribes, who carry "
                    "the reagents and curios of their art.",
    "sailors": "Sailors, dockhands and fishermen of the coasts, honest and otherwise.",
    "satyrs": "Satyrs are night elves corrupted by the Legion into horned, hooved demons, who haunt the ruins "
              "of Ashenvale, Felwood and Desolace and tempt others to the same fall.",
    "humanoid foes": "The foes of the civilised peoples are many: raiders, cultists, tribesmen and renegades "
                     "of every race.",
    # undead
    "the restless dead": "The dead of Lordaeron and the plagued lands do not rest; the Scourge raised them and "
                         "the Forsaken freed some, but most wander their old haunts carrying what they died with.",
    "ghouls": "Ghouls are the Scourge's shock troops, peasants raised with hunger and little else in their heads.",
    "skeletons": "The bones of old wars and plague pits, raised by necromancers to stand guard with rusted blades.",
    "zombies": "The shambling dead of plagued villages, still wearing the rags and carrying the pockets of "
               "their former lives.",
    "ghosts and spirits": "The spirits of the unquiet dead haunt their graves, their ruined homes and the "
                          "battlefields where they fell, and the ectoplasm and old coins they leave behind are "
                          "prized by alchemists and collectors.",
    "gargoyles": "Gargoyles are winged stone-skinned horrors of the Scourge's air arm.",
    "abominations": "Abominations are the Scourge's stitched giants, built in Naxxramas and Stratholme from "
                    "many corpses and the hooks and chains that bind them.",
    "the Scourge": "The Scourge is the Lich King's army of the dead, commanded from Naxxramas and Stratholme by "
                   "liches, death knights and the Cult of the Damned.",
    "the Scarlet Crusade's dead": "The fallen of the Scarlet Crusade, raised by the Scourge they hunted.",
    "undead dwarves": "Dwarves dead in the deep places and raised by the forces that haunt them.",
    # demons
    "demons": "Demons of the Burning Legion left behind by the Third War, or summoned since by the cults that "
              "serve it, haunt the Blasted Lands, Felwood, Desolace and Azshara.",
    "imps": "Imps are the smallest of demons, mischievous fire-flingers bound by warlocks and cultists.",
    "felhounds": "Felhounds are the Legion's mana-eating hunting beasts, loosed wherever demons gather.",
    "voidwalkers": "Voidwalkers are shadowy servitors drawn from the Twisting Nether by warlocks.",
    "succubi": "Succubi are the Legion's tempters, found in the company of cults and in the ruins of Azshara.",
    "infernals": "Infernals are burning stone giants hurled from the sky by the Legion's summoners.",
    "greater demons": "Doomguards, dreadlords and felguards, the Legion's officers and heavy infantry.",
    "fel beasts": "Beasts twisted by fel magic in the Legion's wake.",
    # dragonkin
    "dragonkin": "The dragonflights' lesser kin: whelps, drakes and the dragonspawn who serve the great wyrms.",
    "whelps": "Whelps are the hatchlings of the dragonflights, found in nesting grounds such as the Wyrmbog, "
              "Lethlor Ravine and the Wetlands marsh.",
    "drakes": "Drakes are young dragons, already deadly, that guard their flights' lairs.",
    "dragonspawn": "Dragonspawn are the dragons' serpent-bodied servitor race, the Blackrock Spire's and "
                   "Blackwing Lair's heavy guard.",
    "dragons": "The great dragons themselves: the black flight of Deathwing's children, the mad green drakes "
               "of the Sunken Temple, the blue of Azshara and the red of Grim Batol.",
    # elementals
    "elementals": "Elementals are spirits of earth, air, fire and water, bound or roused by the Old Gods' "
                  "servants, the Twilight's Hammer and the disturbance of the world.",
    "fire elementals": "Fire elementals rise wherever Ragnaros's influence is strong: Blackrock Mountain, the "
                       "Searing Gorge, the Burning Steppes and the fire pits of Un'Goro.",
    "earth elementals": "Earth elementals and their kin stir in the Badlands, Arathi and Silithus, and their "
                        "cores and shards are prized by alchemists and blacksmiths.",
    "air elementals": "Air elementals, dust devils and cyclones haunt the high and the dry places of Silithus, "
                      "Arathi and Desolace.",
    "water elementals": "Water elementals form from the pools of Azeroth where the elemental plane presses "
                        "close, and from the summonings of mages.",
    "oozes and slimes": "Oozes and slimes breed in the plague cauldrons of Lordaeron, the swamps of Un'Goro "
                        "and the Swamp of Sorrows, and the sewers of the Undercity, digesting whatever they engulf.",
    "treants and bog beasts": "Treants, bog beasts and the walking plants of the swamps and forests, kin to the "
                              "ancients.",
    "stone constructs": "Stone and Titan-forged constructs set to guard the ancient vaults.",
    # giants
    "giants": "Giants of stone, sea and hill, the Titans' abandoned workers, wander Feralas, Azshara, the "
              "Hinterlands and the coasts.",
    "golems": "Golems of stone and iron, built by dwarves and Titans to guard and to labour.",
    "ettins": "Two-headed ettins, cousins of the giants, who haunt the hills of Lordaeron.",
    "stone giants": "Stone giants, the Titans' first builders, who stand like boulders in Feralas and Azshara.",
    "sea giants": "Sea giants who wade the coasts of Feralas and Azshara, as old as the shore itself.",
    "mechanical constructs": "The machines of gnome and goblin engineering, harvest golems, shredders and "
                             "the defences of Gnomeregan.",
    "strange creatures": "The strange beasts of the deep places, the Old Gods' spawn and the things the "
                         "nightmare made.",
    "insects": "The giant insects of Silithus, Tanaris, Un'Goro and the Hive: silithid, scarabs and wasps "
               "bred by the qiraji.",
    "carnivorous plants": "The carnivorous lashers and bloodpetals of Un'Goro and Maraudon, which take in "
                          "whatever they catch.",
    "hydras": "Hydras, many-headed reptiles of the pools of Zul'Farrak and the Swamp of Sorrows.",
    "treants": "Treants, the walking trees of the ancient forests.",
    "sporebats": "Sporebats, strange fungal fliers of the deep caverns.",
    "deviate creatures": "The deviate creatures of the Wailing Caverns, beasts mutated by Naralex's nightmare.",
    "horrors": "The faceless horrors and eyes of the Old Gods, which should not exist above ground.",
    "totems": "Totems planted by shaman and witch doctors.",
    "critters": "The small animals of field and forest.",
}

# BEASTS[descriptor] = why these animals carry what they carry
BEASTS = {
    "beasts": "The wild beasts of Azeroth carry no purses, but their hides, teeth, meat and the undigested "
              "remains of their prey have fed and clothed every people on the continent.",
    "wolves": "Wolves hunt in packs across every forest and plain from Dun Morogh to Durotar; the orcs ride "
              "them, the Wildhammer hunt them, and their pelts and flanks are everywhere at market.",
    "great cats": "The great cats, from Elwynn's mountain lions to Stranglethorn's panthers and the sabres of "
                  "Teldrassil and Winterspring, are the most prized of hunters' quarry for their hides.",
    "spiders": "Giant spiders infest the dark woods and caves, from Duskwood's webwoods to the lava spiders of "
               "Searing Gorge, and their silk and venom sacs are traded by tailors and alchemists.",
    "bears": "Bears range the temperate forests and the hills of Lordaeron and Kalimdor, and their meat and "
             "warm pelts are staples of the frontier.",
    "boars": "Boars root through every lowland from Elwynn to Durotar and the Barrens, and their ribs, "
             "snouts and tusks are the first trophies most young hunters bring home.",
    "crocolisks": "Crocolisks lurk in the rivers and marshes of the Wetlands, Dustwallow and Stranglethorn, "
                  "and swallow whatever falls in the water.",
    "carrion birds": "Buzzards, vultures and condors wheel over the dry country of Westfall, the Barrens and "
                     "Tanaris, picking the bones of travellers and whatever those travellers carried.",
    "crabs": "Crabs scuttle along every beach and marsh, and their shells and meat are coastal staples.",
    "gorillas": "The apes of Stranglethorn and Un'Goro are strong, clever and territorial.",
    "raptors": "Raptors are swift pack-hunting lizards of the Barrens, the Wetlands and Stranglethorn, and "
               "their hides, teeth and eggs are much sought.",
    "plainstriders": "Plainstriders are the long-legged flightless birds of the Barrens and Mulgore, hunted "
                     "for meat and feathers.",
    "scorpids": "Scorpids are the great scorpions of Durotar, Tanaris and the Blasted Lands, whose stingers "
                "and venom the alchemists want.",
    "turtles": "Giant turtles haul out along the coasts and the swamps, and their meat and scales have uses "
               "in the kitchen and the forge.",
    "bats": "Bats roost in the caverns and ruins of Tirisfal, Silverpine and the Hinterlands, and the Forsaken "
            "have bred some for riding.",
    "hyenas": "Hyenas scavenge the Barrens, Thousand Needles and the Badlands in cackling packs.",
    "owls": "Owls hunt the night woods of Teldrassil and Duskwood, and their feathers are a reagent of the "
            "druids and the Darnassian craft.",
    "wind serpents": "Wind serpents are winged snakes of the Barrens, Thousand Needles and the Wailing Caverns, "
                     "whose scales and venom are traded by trolls and tauren.",
    "kodo beasts": "Kodo are the great grey beasts of burden of the tauren and the Horde, whose wild herds "
                   "roam Mulgore and the Barrens and whose hides are the stuff of tents and armour.",
    "stags": "Stags and deer browse the gentler forests of Elwynn, Teldrassil and Ashenvale.",
    "rabbits": "Rabbits and hares, the humblest of game.",
    "prairie dogs": "The prairie dogs of Mulgore and the Barrens.",
    "basilisks": "Basilisks are stone-skinned lizards of the deserts and badlands whose hides and eyes "
                 "are used in alchemy.",
    "hippogryphs": "Hippogryphs are the half-stag, half-raptor mounts of the night elves, found wild in Feralas "
                   "and Azshara.",
    "gryphons": "Gryphons nest on Aerie Peak in the Hinterlands, where the Wildhammer dwarves ride them.",
    "birds of prey": "Hawks and eagles of the high country.",
    "serpents": "Serpents of the jungles and swamps, whose venom fills the vials of rogues and alchemists.",
    "worms and grubs": "The grubs, larvae and leeches of the caves and swamps.",
    "silithid": "The silithid are the insect broods of the qiraji, swarming from their hives in Silithus, "
                "Tanaris, Un'Goro and the Barrens.",
    "beetles": "The great beetles and wasps of the deserts.",
    "sea creatures": "The threshers, sharks and makrura of the coasts and the deep.",
    "chimaera": "Chimaera are two-headed winged beasts of Winterspring and Feralas, bred long ago by the "
                "night elves for war.",
    "wildkin": "Owlkin and moonkin, the owl-bears sacred to Elune, haunt the forests of Kalimdor and the "
               "Hinterlands.",
    "yeti": "Yeti are the great shaggy apes of the Alterac and Hillsbrad hills, Feralas and Winterspring.",
    "hounds": "Core hounds are the two-headed lava-dogs of the Molten Core, Ragnaros's kennel.",
    "zhevra": "Zhevra are the striped horse-like grazers of the Barrens.",
    "primordial beasts": "Un'Goro's devilsaurs, stegodons, diemetradons and pterrordaxes are survivors of an "
                         "age before the Titans' ordering of the world.",
    "wyverns": "Wyverns are the winged lion-scorpions of Kalimdor's highlands, which the Horde tamed for riding.",
    "hydras": "Hydras of the pools and swamps.",
    "horses": "Horses, wild and strayed.",
    "winged creatures": "The birds, bats and fliers of Azeroth's skies.",
    "frogs": "Frogs and toads of the marshes.",
    "rams": "Rams of the dwarven hills, which the dwarves have ridden for centuries.",
    "critters": "The small creatures of field and forest.",
    "crawling vermin": "The crawling vermin of caves, swamps and ruins.",
    "a variety of creatures": "Creatures of many kinds.",
}
