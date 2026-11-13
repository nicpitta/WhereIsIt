# Hand-written encyclopedia accounts for notable items. Keyed by item ID; the
# expected name is checked against the database at build time so a wrong ID is
# skipped with a warning rather than attached to the wrong item.
# Value: (name, text) where text is paragraphs joined by "\n", or a dict
# {"A": text, "H": text} for faction-specific accounts.

BESPOKE = {
    19019: ("Thunderfury, Blessed Blade of the Windseeker",
            "Thunderfury is the sword of Prince Thunderaan, son of Al'Akir the Windlord, who was slain and "
            "devoured by Ragnaros when the Firelord betrayed his elemental allies. What the Firelord could not "
            "consume he bound into two talismans and gave to his lieutenants Garr and Baron Geddon to keep.\n"
            "Whoever recovers both Bindings of the Windseeker from the Molten Core and brings them, with a "
            "measure of the Firelord's own essence and the labour of the Hydraxian Waterlords' smiths, to "
            "Highlord Demitrian in Silithus may call the prince's spirit back and have the blade reforged. It "
            "crackles with his lightning still."),
    17182: ("Sulfuras, Hand of Ragnaros",
            "Sulfuras is the hammer of Ragnaros the Firelord, with which he shattered the dwarven kingdom's "
            "hopes when the Dark Irons summoned him and sank Thaurissan's city into Blackrock Mountain. Its head "
            "is a core of living fire set in Sulfuron steel.\n"
            "The Firelord lets go of it only when he is driven back into the lava of the Molten Core, and even "
            "then only the Eye, its burning heart, survives. A smith who has mastered the Black Anvil and the "
            "Thorium Brotherhood's secret of Sulfuron can set the Eye into a hammer of their own making and "
            "call the weapon whole."),
    17204: ("Eye of Sulfuras",
            "The Eye of Sulfuras is the fiery core of the Firelord's hammer, all that remains of Sulfuras "
            "when Ragnaros is banished back into the Molten Core. It burns without fuel and cannot be quenched.\n"
            "A smith who can forge the Sulfuron Hammer, a secret the Thorium Brotherhood sells only to its "
            "most trusted friends and which demands dark iron, Sulfuron ingots, fiery cores and the Black "
            "Anvil itself, may set the Eye into it and remake the Hand of Ragnaros."),
    18563: ("Bindings of the Windseeker",
            "When Ragnaros devoured Prince Thunderaan, the Windseeker, he could not consume the prince entire. "
            "He bound what was left into two talismans and gave one each to his lieutenants to keep apart, so "
            "that the prince could never be whole again.\n"
            "Garr, the lord of the lava elementals, holds this binding in the Molten Core. Only those who "
            "recover both and carry them to Silithus, where the prince's last servant waits, can begin the "
            "reforging of Thunderfury."),
    18564: ("Bindings of the Windseeker",
            "When Ragnaros devoured Prince Thunderaan, the Windseeker, he could not consume the prince entire. "
            "He bound what was left into two talismans and gave one each to his lieutenants to keep apart, so "
            "that the prince could never be whole again.\n"
            "Baron Geddon, the Firelord's lieutenant, holds this binding in the Molten Core. Only those who "
            "recover both and carry them to Silithus, where the prince's last servant waits, can begin the "
            "reforging of Thunderfury."),
    18816: ("Perdition's Blade",
            "Perdition's Blade is a dagger of the Firelord's court, its edge tempered in the lava of the "
            "Molten Core so that it carries the fire into every cut. Rogues have gone to Blackrock Mountain for "
            "a generation in the hope of it.\n"
            "It is held by Ragnaros himself, deepest in the Core, and surrendered only when the Firelord is "
            "beaten back into the fire."),
    17076: ("Bonereaver's Edge",
            "Bonereaver's Edge is a greatsword of the Molten Core, forged by the Firelord's flamewaker smiths "
            "from Sulfuron steel. It bites through armour as if it were cloth.\n"
            "Ragnaros holds it in his court at the heart of Blackrock Mountain, and warriors of the Horde and "
            "the Alliance alike have made the Core's deadliest descent for it."),
    17103: ("Azuresong Mageblade",
            "The Azuresong Mageblade is a sword that hums with the blue dragonflight's arcane song, carried into "
            "the Molten Core by some mage who did not come out. It is now in the keeping of the Firelord's giants.\n"
            "Golemagg the Incinerator, the fire giant who guards the Core's inner reaches with his core hounds, "
            "holds it."),
    17073: ("Earthshaker",
            "Earthshaker is a great hammer of the elemental lords, so heavy that each blow shakes the ground "
            "and staggers everything nearby. It was wielded in the elementals' own wars long before the Dark "
            "Irons woke Ragnaros.\n"
            "It lies in the Molten Core with Garr, the lord of the lava elementals and keeper of one of the "
            "Windseeker's bindings."),
    18814: ("Choker of the Fire Lord",
            "The Choker of the Fire Lord is a collar of Sulfuron steel and fire-hardened gems from the "
            "Firelord's own regalia, wanted above all other things by the spellcasters who brave the Core.\n"
            "Ragnaros surrenders it only when he is driven back into the lava of the Molten Core."),
    18805: ("Core Hound Tooth",
            "A core hound's tooth, as long as a dagger and as hard as obsidian, set into a hilt by the "
            "Firelord's flamewaker smiths. The core hounds are Ragnaros's kennel, two-headed lava-dogs that "
            "rise again if their packmates still live.\n"
            "It is held by Magmadar, the pack's alpha, in the kennels of the Molten Core."),
    19364: ("Ashkandi, Greatsword of the Brotherhood",
            "Ashkandi is a greatsword of the Brotherhood of the Horse, the knightly order of old Stormwind, "
            "its blade worked with the Brotherhood's device. How it came into the hoard of Nefarian at the top "
            "of Blackrock Spire no bard has agreed on.\n"
            "The son of Deathwing keeps it in Blackwing Lair, and only those who break the chromatic flight "
            "and the black dragon himself have carried it out."),
    19352: ("Chromatically Tempered Sword",
            "A sword tempered in the breath of Chromaggus, Nefarian's two-headed chromatic hound, which "
            "breathes the fire, frost, lightning, poison and shadow of every dragonflight. The tempering left "
            "it iridescent and nearly unbreakable.\n"
            "Chromaggus guards it in the laboratories of Blackwing Lair."),
    19346: ("Dragonfang Blade",
            "A dagger ground from the fang of a black dragon, the Dragonfang Blade is one of the prizes of "
            "Blackwing Lair.\n"
            "It is held by Vaelastrasz the Corrupt, the red dragon whom Nefarian broke and turned, who begs "
            "his slayers to free him from his torment."),
    19335: ("Spineshatter",
            "Spineshatter is a mace of the black dragonflight's dragonspawn champions, heavy enough to break "
            "a knight's back through his plate.\n"
            "Broodlord Lashlayer, the dragonspawn who commands Blackwing Lair's lower halls, carries it."),
    18608: ("Benediction",
            "Benediction is the staff of the Light reforged from the Eye of Divinity, a relic of the Molten "
            "Core's hoard, by a priest who passed the trial of Eris Havenfire in the Plaguelands: saving the "
            "doomed peasants of Stratholme's shadow with nothing but faith and healing.\n"
            "It carries both faces of the priesthood, and can be turned in a moment into its shadow, Anathema. "
            "The Eye itself is held by Majordomo Executus in the Firelord's court."),
    18609: ("Anathema",
            "Anathema is the shadow of Benediction, the priest's staff of the Molten Core's Eye of Divinity, "
            "turned to the Forgotten Shadow. The same staff is both; a word changes it.\n"
            "Its making begins when Majordomo Executus yields the Eye of Divinity in the Firelord's court and "
            "ends in the Eastern Plaguelands, where Eris Havenfire tests the priest who would carry it."),
    18646: ("The Eye of Divinity",
            "The Eye of Divinity is a relic of the old priesthoods, carried into the Molten Core by some "
            "zealot of the Light and kept since in the court of the Firelord. It is the heart of the staff "
            "Benediction.\n"
            "Majordomo Executus, Ragnaros's steward, keeps it in his cache, and surrenders it only to those who "
            "scatter his flamewaker guard."),
    18713: ("Rhok'delar, Longbow of the Ancient Keepers",
            "Rhok'delar is the bow of the ancients, the great tree-spirits of the night elves, carved from the "
            "wood of an ancient and strung by the Keepers themselves for a hunter they judged worthy.\n"
            "The judging is the thing: the hunter must carry the Ancient Petrified Leaf out of the Molten Core, "
            "where Majordomo Executus keeps it, and then face the Keepers' four demonic trials alone across "
            "Azeroth before the ancients of Felwood will string the bow."),
    18715: ("Lok'delar, Stave of the Ancient Keepers",
            "Lok'delar is the companion stave to the longbow Rhok'delar, carved by the ancients of Felwood for "
            "a hunter who has proved themselves in the Keepers' trials.\n"
            "It is given with the bow to the hunter who brings the Ancient Petrified Leaf from the Molten Core "
            "and defeats the four demons the Keepers set as tests."),
    18703: ("Ancient Petrified Leaf",
            "A leaf fallen from one of the ancients, the tree-spirits of the night elves, turned to stone with "
            "age, and carried into the Molten Core by someone who never left. The ancients of Felwood will know "
            "it for their own.\n"
            "Majordomo Executus holds it in his cache in the Firelord's court, and a hunter who carries it to "
            "the Irontree Woods of Felwood begins the trials that end with Rhok'delar."),
    18348: ("Quel'Serrar",
            "Quel'Serrar, the High Blade, is a sword of the night elves' ancient wars, its unfinished blade "
            "found in the Shen'dralar libraries of Dire Maul in the pages of a foreign tome. It can only be "
            "finished in dragonfire.\n"
            "The warrior who finds the tome must carry the unfired blade into Onyxia's Lair, lay it before the "
            "Broodmother's breath to temper it, and drive it into her corpse to quench it."),
    15138: ("Onyxia Scale Cloak",
            "A cloak of the Broodmother's own scales, sewn by a leatherworker who has learned the pattern from "
            "the heroes of Dustwallow. It turns the shadow flame of the black dragonflight, which no other "
            "cloth will.\n"
            "The scales come from Onyxia herself, in her lair beneath Dustwallow Marsh, and the pattern is given "
            "only to those who have faced her."),
    18422: ("Head of Onyxia",
            "The head of Onyxia, Broodmother of the black dragonflight, who sat on the throne council of "
            "Stormwind in the guise of Lady Katrana Prestor and schemed the kingdom nearly to ruin before "
            "she was unmasked.\n"
            "It is carried from her lair beneath Dustwallow Marsh to Stormwind, where King Varian's regents hang "
            "it from the gates of the city and the Light's blessing falls on all who see it."),
    18423: ("Head of Onyxia",
            "The head of Onyxia, Broodmother of the black dragonflight, who meddled in the courts of men and "
            "whose brood threatened Theramore and the Horde's holdings in Dustwallow alike.\n"
            "It is carried from her lair beneath Dustwallow Marsh to Orgrimmar, where Thrall has it hung from "
            "the gates of the Valley of Strength and the shaman bless all who gather there."),
    19002: ("Head of Nefarian",
            "The head of Nefarian, Lord of Blackwing Lair, son of Deathwing and master of the Blackrock orcs, "
            "who bred the chromatic dragonflight from the stolen eggs of the other flights.\n"
            "It is carried from the peak of Blackrock Spire to Stormwind, where it is raised over the city and "
            "the Light's blessing falls on all who see it."),
    19003: ("Head of Nefarian",
            "The head of Nefarian, Lord of Blackwing Lair, son of Deathwing and master of the Blackrock orcs, "
            "whose warchief Rend Blackhand claimed the Horde's name for a generation.\n"
            "It is carried from the peak of Blackrock Spire to Orgrimmar, where Thrall raises it over the Valley "
            "of Strength and the spirits bless all who gather."),
    13505: ("Runeblade of Baron Rivendare",
            "The runeblade of Baron Rivendare, the nobleman of Stratholme who gave his city to the Scourge "
            "and rose as a death knight to rule its eastern half. Runeblades are forged by the Scourge for its "
            "knights alone and carry a rune of the Lich King's own.\n"
            "The Baron keeps it in the Slaughter Square of Stratholme, and gives it up only with his unlife."),
    13335: ("Deathcharger's Reins",
            "The reins of a deathcharger, the skeletal warhorse of the Scourge's death knights. Baron Rivendare "
            "rides one through the streets of Stratholme, and the rare slayer who can master the beast rides it "
            "out.\n"
            "The Baron yields it in the Slaughter Square of Stratholme, and seldom; many hundreds have taken "
            "the city and left on foot."),
    13340: ("Cape of the Black Baron",
            "The cloak of Baron Rivendare, the death knight of Stratholme, cut from the black cloth of the "
            "Scourge's court.\n"
            "The Baron gives it up in the Slaughter Square of Stratholme."),
    11684: ("Ironfoe",
            "Ironfoe is a hammer of the Dark Iron dwarves' Shadowforge, so well-balanced that it strikes again "
            "of itself. It was the pride of the Shadowforge smiths.\n"
            "Emperor Dagran Thaurissan holds it in the Iron Hall of Blackrock Depths, and it is accounted one of "
            "the rarest prizes of that city."),
    12590: ("Felstriker",
            "Felstriker is a dagger of the Blackrock orcs' warlocks, its edge sharpened on fel so that every "
            "wound it opens, for an instant, is mortal.\n"
            "Warchief Rend Blackhand keeps it in the Hall of Blackhand at the top of Blackrock Spire."),
    12592: ("Blackblade of Shahram",
            "The Blackblade of Shahram holds the shade of Shahram, an ancient warrior bound into the steel, who "
            "comes forth to fight beside its wielder with the curses and blessings of his age.\n"
            "General Drakkisath, the dragonspawn commander of Blackrock Spire's upper halls, carries it."),
    12587: ("Eye of Rend",
            "The Eye of Rend is a helm of Blackrock make, named for the warchief Rend Blackhand and worked with "
            "the clan's black and red.\n"
            "Rend himself keeps it in the Hall of Blackhand in Blackrock Spire, where he holds court for Nefarian."),
    12940: ("Dal'Rend's Sacred Charge",
            "Dal'Rend's Sacred Charge is one of the two swords of Rend Blackhand, warchief of the Blackrock "
            "clan under Nefarian. Together with the Tribal Guardian it makes the Arms of Dal'Rend, a pair "
            "warriors seek across Azeroth.\n"
            "Rend carries it into the Hall of Blackhand at the top of Blackrock Spire."),
    12939: ("Dal'Rend's Tribal Guardian",
            "Dal'Rend's Tribal Guardian is the off-hand blade of Rend Blackhand's pair, the Arms of Dal'Rend, "
            "worked in the Blackrock clan's tribal style.\n"
            "Rend carries it in the Hall of Blackhand at the top of Blackrock Spire."),
    7717: ("Ravager",
           "Ravager is the great axe of Herod, the Scarlet Champion, which whirls of its own accord in the "
           "hands of a strong enough wielder, as it does in his.\n"
           "Herod holds the Armory of the Scarlet Monastery in Tirisfal, and gives up his axe with his life."),
    1482: ("Shadowfang",
           "Shadowfang is the sword that gave the keep its name, a blade of Silverpine's barons forged with "
           "shadow in the steel so that it bites the spirit as well as the flesh.\n"
           "The worgen lords of Shadowfang Keep hold it, and the Sons of Arugal are loath to part with it."),
    7734: ("Six Demon Bag",
           "A bag containing, by the maker's account, six demons: or at least six spells of fire, frost and "
           "lightning that it hurls at random when shaken. It is a curio of the Sunken Temple's Atal'ai priests.\n"
           "The Shade of Eranikus and the Atal'ai high priests of the Temple of Atal'Hakkar hold it."),
    9240: ("Mallet of Zul'Farrak",
           "The Mallet of Zul'Farrak is the Sandfury trolls' ceremonial hammer, with which they strike the "
           "gong that wakes the hydra Gahz'rilla in their sacred pool. It is made by setting the Sacred Mallet "
           "of the Hinterlands' trolls into the altar of Jintha'Alor.\n"
           "The Sacred Mallet is carried by Qiaga the Keeper, high priestess of the Vilebranch at Jintha'Alor "
           "in the Hinterlands, and the altar is at the top of her city."),
    8529: ("Noggenfogger Elixir",
           "Noggenfogger Elixir is the brew of Marin Noggenfogger of Gadgetzan, who promised it would make the "
           "drinker light as a feather and could not say exactly what else. It shrinks some, makes skeletons "
           "of others, and lets the rest drift gently to the ground.\n"
           "Marin sells it in Gadgetzan to anyone who has fetched him the ingredients for his first batch: "
           "the spring water of a Tanaris oasis, the dust of a Caverns of Time dragon and the sacred candle of "
           "a Zul'Farrak troll."),
    6657: ("Savory Deviate Delight",
           "Savory Deviate Delight is deviate fish of the Wailing Caverns cooked to a recipe that keeps the "
           "nightmare's twist in the flesh: the eater becomes, for an hour, a pirate or a ninja, to the "
           "merriment of everyone in the Crossroads.\n"
           "The recipe is a rare find on the Barrens' creatures and the Wailing Caverns' deviate beasts, and the "
           "fish are caught in the oases of the Barrens and the caverns' pools."),
    1973: ("Orb of Deception",
           "The Orb of Deception is a Highborne artefact that lays a glamour over its holder, so that an orc "
           "appears a human, a tauren a night elf, a dwarf a troll, and so on across the old enmities. "
           "The glamour fools the eye and nothing else.\n"
           "It turns up in the hoards of the great foes and the chests of the deep places across both "
           "continents, with no one owner."),
    4984: ("Skull of Impending Doom",
           "The Skull of Impending Doom is a cursed skull that fills its bearer with such dread that they run "
           "faster than they have ever run, at the cost of their strength and their health draining with every step.\n"
           "It is among the rewards the Argent Dawn's and the frontier's questgivers offer for grim errands."),
    9449: ("Manual Crowd Pummeler",
           "The Manual Crowd Pummeler is a gnomish device for keeping order in a crowd: a mace with a crank "
           "that, wound up, makes its wielder strike with inhuman speed for a few seconds.\n"
           "Crowd Pummeler 9-60, the machine Gnomeregan's gnomes built to do the same job, carries the model "
           "in the Dormitory of Gnomeregan."),
    11815: ("Hand of Justice",
           "The Hand of Justice is a trinket of the Dark Iron senate, a gavel-charm that lends its holder a "
           "second blow when the first lands.\n"
           "Emperor Dagran Thaurissan keeps it in the Iron Hall of Blackrock Depths."),
    2820: ("Nifty Stopwatch",
           "A gnomish stopwatch that, when its button is pressed, lets its bearer run very fast indeed for a "
           "few seconds. The mechanism is not well understood by anyone who did not build it.\n"
           "It is given as a reward for a chain of errands in the Wetlands and Loch Modan on behalf of the "
           "dwarves of Menethil Harbor."),
    11122: ("Carrot on a Stick",
           "A carrot on a stick, the goblins' time-honoured method of persuading a mount to go faster. It works "
           "on horses, rams, wolves, raptors and kodo alike, which tells you something about mounts.\n"
           "It is a prize of the Shimmering Flats' Mirage Raceway in Thousand Needles, given for a chain of "
           "errands on behalf of the gnome and goblin racers."),
    13209: ("Seal of the Dawn",
           "The Seal of the Dawn is the Argent Dawn's badge of service, given to those who fight the Scourge in "
           "its name. It lends strength against the undead in the Plaguelands, Stratholme and Scholomance.\n"
           "The Argent Dawn's quartermasters at Light's Hope Chapel give it to those who have earned the Dawn's "
           "trust."),
    12846: ("Argent Dawn Commission",
           "The Argent Dawn Commission is the Dawn's token of service, which lets its wearer collect the "
           "Scourgestones from the undead they slay and turn them in at Light's Hope for the Dawn's favour.\n"
           "The Argent Dawn's officers at Light's Hope Chapel and Chillwind Camp give it to anyone who will "
           "fight the Scourge."),
    13382: ("Cannonball Runner",
           "The Cannonball Runner is a goblin cannon on wheels that deploys itself, fires at anything hostile "
           "for a few seconds and then falls apart, as goblin devices do.\n"
           "It is held by Cannon Master Willey of the Scarlet Crusade in the Bastion of Stratholme, who uses "
           "the real thing."),
    5956: ("Blacksmith Hammer",
           "The blacksmith's hammer, sold by every blacksmithing supplier and trade goods merchant, and the one "
           "tool without which no smith can work at the anvil.\n"
           "It can be had in every settlement with a forge."),
    6256: ("Fishing Pole",
           "A plain fishing pole, the first and only weapon of the angler, sold by every fishing supplier and "
           "general goods merchant on the coasts and lakes of Azeroth.\n"
           "It can be had in every settlement with water nearby."),
    6367: ("Big Iron Fishing Pole",
           "The Big Iron Fishing Pole is the heavy pole of the Shimmering Flats' anglers, better than the plain "
           "pole and found nowhere in a shop.\n"
           "It turns up in the shellfish traps of the Shimmering Flats in Thousand Needles, and anglers wade "
           "the salt flats for it."),
    19970: ("Arcanite Fishing Pole",
           "The Arcanite Fishing Pole is the finest fishing pole in Azeroth, forged of arcanite and strung with "
           "the best line, and the prize of the Stranglethorn Fishing Extravaganza.\n"
           "It is given to the winner of the Extravaganza, held every week off the coast of Stranglethorn Vale "
           "by the Steamwheedle goblins of Booty Bay."),
    19902: ("Swift Zulian Tiger",
           "The Swift Zulian Tiger is one of the great tigers of Zul'Gurub, bred by the Gurubashi as the "
           "mounts of their high priests and ridden out by the rare hero who can master one.\n"
           "High Priest Thekal, whose aspect is the tiger god Shirvallah, keeps the tigers in Zul'Gurub, and "
           "seldom gives one up."),
    19872: ("Swift Razzashi Raptor",
           "The Swift Razzashi Raptor is one of the raptors of Zul'Gurub, bred by the Gurubashi from the jungle "
           "stock and ridden by their priests of the raptor god.\n"
           "Bloodlord Mandokir, the Gurubashi champion, keeps the raptors in Zul'Gurub and yields one seldom."),
    21176: ("Black Qiraji Resonating Crystal",
           "The Black Qiraji Resonating Crystal is the mount-crystal of the qiraji battle tanks, the great "
           "insect steeds of Ahn'Qiraj, and the only one of its kind that will carry its rider outside the "
           "temple's walls.\n"
           "It is given to the champion who gathers the Scepter of the Shifting Sands and rings the gong at the "
           "Scarab Wall to open Ahn'Qiraj, and to no one else."),
    22589: ("Atiesh, Greatstaff of the Guardian",
           "Atiesh is the staff of the Guardians of Tirisfal, carried by Medivh, the last Guardian, through "
           "whom Sargeras opened the Dark Portal. After Medivh's death the staff was shattered and its pieces "
           "scattered into Naxxramas by the Scourge, who could not destroy it.\n"
           "Whoever gathers the forty splinters from the necropolis, recovers the base and the head from its "
           "masters, and cleanses the staff of the shade that haunts it in Stratholme may take it to "
           "Karazhan, where Medivh's servant will restore it."),
    20725: ("Nexus Crystal",
            "Nexus crystals are the enchanters' greatest reagent, drawn only from the epic items of the great "
            "dungeons when they are disenchanted, and needed for the enchantments of the heroes.\n"
            "Enchanters distil them from the epic prizes of the Molten Core, Blackwing Lair, Zul'Gurub and "
            "Ahn'Qiraj."),
    19183: ("Hourglass Sand",
            "Hourglass sand is the sand of the Caverns of Time, carried by the brood of Nozdormu's children; a "
            "pinch of it breaks the brood affliction that Nefarian's chromatic dragons lay on their foes.\n"
            "It is gathered from the brood of the Caverns of Time in Tanaris, in whose hourglass the sands of "
            "all time run."),
    2244: ("Krol Blade",
           "The Krol Blade is a sword of the old world's wars, its hilt worked in a style no living smith "
           "claims, that turns up in the hoards of the great foes across Azeroth.\n"
           "It has no one home; it is a rare prize of the middle dungeons and the chests of the deep places."),
    2243: ("Hand of Edward the Odd",
           "The Hand of Edward the Odd is a mace named for an eccentric mage of old Lordaeron, who wished for a "
           "weapon that would let him cast as he struck. It does.\n"
           "It is a rare world drop, found in the hoards of the great foes across both continents."),
    1728: ("Teebu's Blazing Longsword",
           "Teebu's Blazing Longsword is a sword that burns without being consumed, named for a goblin "
           "duelist who wanted a weapon no one could miss seeing. It is one of the rarest swords in Azeroth.\n"
           "It has no home; it is a world drop of the rarest kind, found once in a generation in the hoards "
           "of the great foes."),
    13964: ("Witchblade",
            "The Witchblade is a dagger of the Scourge's necromancers, forged in Scholomance to channel shadow "
            "and frost into the wielder's spells.\n"
            "Rattlegore, the bone golem of Scholomance, carries it in the Great Ossuary."),
    13183: ("Venomspitter",
            "Venomspitter is a mace of Maraudon's corrupted earth, its head weeping poison from the stone.\n"
            "Princess Theradras, the earth elemental who is the centaur's ancestress, holds it in the heart of "
            "Maraudon."),
    13246: ("Argent Avenger",
            "The Argent Avenger is a sword of the Argent Dawn, blessed against the undead, which the Dawn "
            "gives to those who take the fight to the Scourge in its name.\n"
            "The Argent Dawn's quartermasters at Light's Hope Chapel give it to those who have earned the "
            "Dawn's trust."),
    5976: ("Guild Tabard",
           "The guild tabard is the badge of a guild, bought from the guild masters of the capitals and "
           "worked with the guild's own device and colours.\n"
           "It is sold by the guild masters of Stormwind, Ironforge, Darnassus, Orgrimmar, Thunder Bluff and "
           "the Undercity to any member of a guild."),
    7005: ("Skinning Knife",
           "The skinning knife, sold by every trade goods merchant, is the one tool of the skinner, who takes "
           "the hides of the hunt for the leatherworkers.\n"
           "It can be had in every settlement."),
    2901: ("Mining Pick",
           "The mining pick, sold by every trade goods and mining supplier, is the one tool of the miner.\n"
           "It can be had in every settlement with a mine nearby."),
    6218: ("Runed Copper Rod",
           "The runed copper rod is the enchanter's first rod, a copper rod from the blacksmith enchanted with "
           "strange dust and lesser magic essence, without which no enchantment can be laid.\n"
           "Enchanters make it themselves from a copper rod bought from any trade goods merchant."),
    13444: ("Major Mana Potion",
            "The major mana potion is the greatest of the alchemists' mana draughts, brewed from dreamfoil and "
            "icecap, and the staple of every spellcaster who faces the great foes.\n"
            "Alchemists brew it, the Argent Dawn's and the war effort's quartermasters sell it, and the "
            "creatures of the Plaguelands, Silithus and the great dungeons carry it."),
    13446: ("Major Healing Potion",
            "The major healing potion is the greatest of the alchemists' healing draughts, brewed from golden "
            "sansam and mountain silversage, carried by every adventurer who means to come home.\n"
            "Alchemists brew it, and the creatures of the far country and the great dungeons carry it."),
    1179: ("Ice Cold Milk",
           "Ice cold milk, from the cows of Elwynn and Mulgore, sold by every innkeeper and drink vendor and the "
           "first drink of every new adventurer.\n"
           "It can be had at every inn."),
    159: ("Refreshing Spring Water",
          "Refreshing spring water, bottled from the springs of the starting lands and sold by every innkeeper "
          "and drink vendor to anyone with a thirst.\n"
          "It can be had at every inn."),
    4540: ("Tough Hunk of Bread",
           "A tough hunk of bread, the cheapest food in Azeroth, sold by every baker and innkeeper.\n"
           "It can be had at every inn."),
    2894: ("Rhapsody Malt",
           "Rhapsody Malt is a Dun Morogh malt beer of the dwarven brewers, sold by the barkeeps of Khaz Modan "
           "and Stormwind and, in friendlier times, Southshore.\n"
           "It can be had from the barkeeps of the Alliance's inns."),
    19979: ("Hook of the Master Angler",
            "The Hook of the Master Angler is a fishhook that lets its bearer breathe underwater and swim as "
            "fast as a fish, one of the prizes of the Stranglethorn Fishing Extravaganza.\n"
            "It is given to the winner of the Extravaganza, held each week off the coast of Stranglethorn by "
            "the goblins of Booty Bay."),
}
