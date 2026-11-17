#!/usr/bin/env python3
"""
Generates the EconomyShopGUI sections/ and shops/ folders for the DonutSMP-style shop.

  python3 tools/generate.py <path-to-minecraft-data/data/pc/1.21.11> [output-dir]

minecraft-data:  npm pack minecraft-data && tar xzf minecraft-data-*.tgz
                 -> package/minecraft-data/data/pc/1.21.11

How prices are decided
  1. DONUT_SHOP   - the real DonutSMP /shop buy prices (last version before /shop was removed).
  2. BASE         - hand-set /sell values for raw / farmable / mob-drop items, anchored to known
                    Donut numbers (e.g. dried kelp block sells for $300 on Donut -> dried kelp $33).
  3. Recipes      - every craftable item is priced at the cheapest sum of its ingredients / output,
                    so crafting can never create money.
  4. Fallbacks    - oxidised copper variants and coloured shulkers/bundles copy their base item.
  Items in the Donut shop always sell for at most 50% of their buy price (no buy->sell loop).
"""
import json, os, re, sys
from collections import OrderedDict

DATA = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "..", "EconomyShopGUI")

# --------------------------------------------------------------------------------------------
# 1. Real DonutSMP /shop (buy prices in $). Source: DonutSMP wiki "Shop" page (final version).
# --------------------------------------------------------------------------------------------
DONUT_SHOP = OrderedDict([
    # name, menu slot, icon, colour, small-caps title, lore, items [(material, buy, extra-yaml)]
    ("End", (11, "END_STONE", "&d", "ᴇɴᴅ", ["&7Blocks and items", "&7from the End."], [
        ("ENDER_CHEST", 2500, None), ("ENDER_PEARL", 75, None), ("END_STONE", 8, None),
        ("DRAGON_BREATH", 1000, None), ("END_ROD", 100, None), ("CHORUS_FRUIT", 108, None),
        ("POPPED_CHORUS_FRUIT", 24, None), ("SHULKER_SHELL", 350, None), ("SHULKER_BOX", 800, None),
    ])),
    ("Nether", (12, "NETHERRACK", "&c", "ɴᴇᴛʜᴇʀ", ["&7Blocks and items", "&7from the Nether."], [
        ("BLAZE_ROD", 150, None), ("NETHER_WART", 96, None), ("GLOWSTONE_DUST", 15, None),
        ("MAGMA_CREAM", 96, None), ("GHAST_TEAR", 350, None), ("QUARTZ", 30, None),
        ("SOUL_SAND", 50, None), ("MAGMA_BLOCK", 35, None), ("CRYING_OBSIDIAN", 150, None),
    ])),
    ("Gear", (13, "TOTEM_OF_UNDYING", "&b", "ɢᴇᴀʀ", ["&7PvP and combat", "&7essentials."], [
        ("OBSIDIAN", 100, None), ("END_CRYSTAL", 350, None), ("RESPAWN_ANCHOR", 1000, None),
        ("GLOWSTONE", 100, None), ("TOTEM_OF_UNDYING", 1500, None), ("ENDER_PEARL", 75, None),
        ("GOLDEN_APPLE", 250, None), ("EXPERIENCE_BOTTLE", 100, None),
        ("TIPPED_ARROW", 500, "potiontypes: SLOW_FALLING"),
    ])),
    ("Food", (14, "COOKED_BEEF", "&6", "ꜰᴏᴏᴅ", ["&7Food to keep", "&7you going."], [
        ("POTATO", 96, None), ("SWEET_BERRIES", 50, None), ("MELON_SLICE", 36, None),
        ("CARROT", 96, None), ("APPLE", 25, None), ("COOKED_CHICKEN", 48, None),
        ("COOKED_BEEF", 35, None), ("GOLDEN_CARROT", 120, None), ("GOLDEN_APPLE", 250, None),
    ])),
])

# --------------------------------------------------------------------------------------------
# 2. Base /sell values ($ per item) for things that are mined, farmed, dropped or smelted.
# --------------------------------------------------------------------------------------------
B = {}
def base(v, *names):
    for n in names:
        B[n] = v

WOODS = ["oak", "spruce", "birch", "jungle", "acacia", "cherry", "dark_oak", "pale_oak", "mangrove"]
COLORS = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "light_gray",
          "cyan", "purple", "blue", "brown", "green", "red", "black"]

# terrain
base(1, "cobblestone", "dirt", "netherrack", "cobbled_deepslate", "snowball")
base(2, "stone", "deepslate", "calcite", "tuff", "sand", "gravel", "mud", "rooted_dirt", "basalt",
     "blackstone", "pointed_dripstone", "short_grass", "fern", "seagrass", "leaf_litter")
base(3, "grass_block", "podzol", "red_sand", "crimson_nylium", "warped_nylium", "ice", "smooth_basalt",
     "glass", "brick", "nether_brick", "smooth_stone", "clay_ball", "moss_block", "pale_moss_block",
     "vine", "weeping_vines", "twisting_vines", "glow_lichen", "pink_petals", "wildflowers",
     "brown_mushroom_block", "red_mushroom_block", "mushroom_stem", "flint")
base(4, "end_stone", "cracked_stone_bricks", "cracked_deepslate_bricks", "cracked_deepslate_tiles",
     "cracked_nether_bricks", "cracked_polished_blackstone_bricks")
base(5, "mycelium", "soul_sand", "soul_soil", "sculk", "egg", "blue_egg", "brown_egg", "lily_pad",
     "mangrove_roots", "azalea", "big_dripleaf", "small_dripleaf", "hanging_roots", "pale_hanging_moss",
     "poisonous_potato", "crimson_roots", "warped_roots", "nether_sprouts", "bush", "dead_bush",
     "short_dry_grass", "tall_dry_grass", "tall_grass", "large_fern")
base(6, "terracotta", *[f"{c}_concrete" for c in COLORS])
base(8, "flowering_azalea", "bamboo", "charcoal", "sunflower", "lilac", "rose_bush", "peony",
     *[f"{c}_glazed_terracotta" for c in COLORS], "smooth_sandstone")
base(10, "brown_mushroom", "red_mushroom", "crimson_fungus", "warped_fungus", "feather", "cactus_flower",
     "firefly_bush", "resin_brick", "apple", "cod", "smooth_red_sandstone")
base(1, *[f"{w}_leaves" for w in WOODS], "azalea_leaves", "flowering_azalea_leaves")
base(5, *[f"{w}_sapling" for w in WOODS if w != "mangrove"], "mangrove_propagule",
     "dandelion", "poppy", "blue_orchid", "allium", "azure_bluet", "red_tulip", "orange_tulip",
     "white_tulip", "pink_tulip", "oxeye_daisy", "cornflower", "lily_of_the_valley",
     "open_eyeblossom", "closed_eyeblossom")
base(20, "torchflower", "pitcher_plant", "cobweb", "sea_pickle", "cocoa_beans", "ink_sac", "pufferfish",
     "tropical_fish", "chicken", "cooked_cod", "honeycomb", "amethyst_shard")
base(300, "dragon_breath")
base(30, "spore_blossom", "chorus_flower")
base(15, *[f"{w}_log" for w in WOODS], *[f"stripped_{w}_log" for w in WOODS],
     "crimson_stem", "warped_stem", "stripped_crimson_stem", "stripped_warped_stem",
     "shroomlight", "beef", "porkchop", "glow_berries", "sweet_berries", "copper_ingot")
base(65, "smooth_quartz")
base(6, "glowstone_dust")
base(15, "white_wool")
base(10, "resin_clump")
base(2, "sculk_vein")
base(5, "warped_wart_block")
base(72, "stripped_bamboo_block")
base(50, "wither_rose", "ochre_froglight", "verdant_froglight", "pearlescent_froglight", "magma_cream")
# coral
for c in ["tube", "brain", "bubble", "fire", "horn"]:
    base(15, f"{c}_coral_block"); base(8, f"{c}_coral", f"{c}_coral_fan")
    base(3, f"dead_{c}_coral_block", f"dead_{c}_coral", f"dead_{c}_coral_fan")
base(5, "small_amethyst_bud"); base(8, "medium_amethyst_bud"); base(12, "large_amethyst_bud")
base(20, "amethyst_cluster")
base(500, "sponge", "wet_sponge", "sculk_catalyst", "sculk_shrieker", "bell", "name_tag", "iron_horse_armor",
     "iron_nautilus_armor")
base(300, "sculk_sensor", "turtle_egg", "trial_key", "dried_ghast")

# farming (Donut anchor: dried kelp block /sell = $300 -> 9 dried kelp)
base(30, "kelp", "wheat", "carrot", "potato", "beetroot", "sugar_cane", "nether_wart", "chorus_fruit",
     "honey_bottle", "string")
base(33.33, "dried_kelp")
base(25, "cactus", "green_dye", "leather", "rabbit_hide")
base(40, "pumpkin", "carved_pumpkin", "bone", "spider_eye", "slime_ball", "glow_ink_sac", "prismarine_crystals",
     "experience_bottle")
base(12, "melon_slice", "mutton", "rabbit", "salmon", "popped_chorus_fruit", "lapis_lazuli")
base(2, "wheat_seeds", "beetroot_seeds", "torchflower_seeds", "pitcher_pod")
base(17, "cooked_beef", "cooked_porkchop")
base(18, "cooked_mutton", "cooked_rabbit", "cooked_salmon", "baked_potato")
base(24, "cooked_chicken")

# mob / spawner drops
base(15, "rotten_flesh")
base(60, "gunpowder")
base(30, "ender_pearl", "prismarine_shard")
base(50, "blaze_rod")
base(100, "rabbit_foot", "phantom_membrane", "armadillo_scute")
base(120, "ghast_tear")
base(150, "shulker_shell", "turtle_scute", "breeze_rod", "gilded_blackstone")
base(1000, "nautilus_shell", "goat_horn")
base(112, "disc_fragment_5")
base(5000, "heart_of_the_sea", "wither_skeleton_skull", "trident")
base(2000, "skeleton_skull", "zombie_head", "creeper_head", "sniffer_egg", "echo_shard", "netherite_scrap",
     "ancient_debris", "ominous_trial_key")
base(3000, "piglin_head")
base(100000, "dragon_head")
base(50000, "nether_star", "elytra")
base(500000, "dragon_egg")
base(20000, "enchanted_golden_apple", "heavy_core")
base(200, "ominous_bottle", "copper_horse_armor", "copper_nautilus_armor", "copper_golem_statue",
     "bee_nest", "chipped_anvil")
base(600, "totem_of_undying", "golden_horse_armor", "golden_nautilus_armor")
base(2000, "diamond_horse_armor", "diamond_nautilus_armor")
base(100, "damaged_anvil")

# ores, ingots, gems
base(10, "coal"); base(8, "redstone"); base(60, "iron_ingot"); base(80, "gold_ingot")
base(300, "diamond"); base(150, "emerald"); base(15, "quartz")
base(50, "raw_iron"); base(70, "raw_gold"); base(12, "raw_copper")
base(15, "coal_ore"); base(18, "deepslate_coal_ore"); base(70, "iron_ore"); base(75, "deepslate_iron_ore")
base(20, "copper_ore"); base(22, "deepslate_copper_ore"); base(90, "gold_ore"); base(95, "deepslate_gold_ore")
base(50, "redstone_ore"); base(55, "deepslate_redstone_ore"); base(200, "emerald_ore")
base(220, "deepslate_emerald_ore"); base(60, "lapis_ore"); base(65, "deepslate_lapis_ore")
base(400, "diamond_ore"); base(450, "deepslate_diamond_ore"); base(30, "nether_gold_ore")
base(25, "nether_quartz_ore")
base(50, "obsidian"); base(75, "crying_obsidian")

# chainmail
base(300, "chainmail_helmet"); base(500, "chainmail_chestplate"); base(400, "chainmail_leggings")
base(250, "chainmail_boots")

# music discs, sherds, patterns, templates
MANUAL_PATTERNS = [
    (r"^music_disc_", 1000), (r"_pottery_sherd$", 300), (r"^(globe|piglin|flow|guster)_banner_pattern$", 500),
    (r"^netherite_upgrade_smithing_template$", 2000), (r"_armor_trim_smithing_template$", 2000),
]

# smithing: netherite gear = diamond version + netherite ingot
SMITH = ["sword", "shovel", "pickaxe", "axe", "hoe", "helmet", "chestplate", "leggings", "boots", "spear",
         "horse_armor", "nautilus_armor"]

# buckets (bucket + contents)
BUCKET_EXTRA = {"water_bucket": 1, "lava_bucket": 20, "milk_bucket": 5, "powder_snow_bucket": 5,
                "pufferfish_bucket": 25, "salmon_bucket": 15, "cod_bucket": 15, "tropical_fish_bucket": 25,
                "axolotl_bucket": 100, "tadpole_bucket": 10}

# never sellable: creative-only, NBT-dependent or exploit-prone
EXCLUDE_RE = re.compile(r"(_spawn_egg$|^infested_|command_block|^structure_|^jigsaw$|^test_|^light$|^barrier$|"
                        r"^bedrock$|^air$|^debug_stick$|^knowledge_book$|^petrified_oak_slab$|^reinforced_deepslate$|"
                        r"^end_portal_frame$|^farmland$|^dirt_path$|^budding_amethyst$|^chorus_plant$|"
                        r"^spawner$|^trial_spawner$|^vault$|^player_head$|^suspicious_|^frogspawn$|^filled_map$|"
                        r"^written_book$|^potion$|^splash_potion$|^lingering_potion$|^tipped_arrow$|"
                        r"^enchanted_book$|^firework_star$|^bundle$|_bundle$|^ominous_banner$)")

# --------------------------------------------------------------------------------------------
items = json.load(open(os.path.join(DATA, "items.json")))
recipes = json.load(open(os.path.join(DATA, "recipes.json")))
name_of = {i["id"]: i["name"] for i in items}
all_names = [i["name"] for i in items]

price = {}
for n in all_names:
    if EXCLUDE_RE.search(n):
        continue
    if n in B:
        price[n] = float(B[n])
    else:
        for pat, v in MANUAL_PATTERNS:
            if re.search(pat, n):
                price[n] = float(v)

def ingredients(rec):
    if "ingredients" in rec:
        return rec["ingredients"]
    return [c for row in rec["inShape"] for c in row if c is not None]

def recipe_cost(rec):
    tot = 0.0
    for i in ingredients(rec):
        n = name_of[i]
        if n not in price:
            return None
        tot += price[n]
    return tot / rec["result"]["count"]

fixed = set(price)
changed = True
while changed:
    changed = False
    for rid, recs in recipes.items():
        out = name_of[int(rid)]
        if out in fixed or EXCLUDE_RE.search(out):
            continue
        costs = [c for c in (recipe_cost(r) for r in recs) if c is not None]
        if not costs:
            continue
        c = min(costs)
        if out not in price or c < price[out] - 1e-9:
            price[out] = c
            changed = True
    # smithing / buckets once their inputs are known
    for part in SMITH:
        d, n = f"diamond_{part}", f"netherite_{part}"
        if n in all_names and n not in price and d in price and "netherite_ingot" in price:
            price[n] = price[d] + price["netherite_ingot"]; changed = True
    if "bucket" in price:
        for b, extra in BUCKET_EXTRA.items():
            if b not in price:
                price[b] = price["bucket"] + extra; changed = True

# fallbacks: oxidised / waxed copper and coloured variants
for n in all_names:
    if n in price or EXCLUDE_RE.search(n):
        continue
    stripped = re.sub(r"^(waxed_)?(exposed_|weathered_|oxidized_)", "", n)
    stripped = re.sub(r"^waxed_", "", stripped)
    stripped = {"copper": "copper_block", "stripped_bamboo_block": "bamboo_block"}.get(stripped, stripped)
    if stripped in price:
        price[n] = price[stripped]
        continue
    for c in COLORS:
        rest = n[len(c) + 1:]
        if n.startswith(c + "_"):
            for cand in (rest, "white_" + rest):
                if cand in price:
                    price[n] = price[cand]
                    break
            break

unpriced = [n for n in all_names if n not in price and not EXCLUDE_RE.search(n)]

# --------------------------------------------------------------------------------------------
# shop items: sell for at most 50% of buy; also make sure nothing craftable purely from shop
# items sells for more than it costs to buy the ingredients.
# --------------------------------------------------------------------------------------------
shop_buy = {}
for sec, (_, _, _, _, _, its) in DONUT_SHOP.items():
    for mat, buy, _ in its:
        shop_buy[mat.lower()] = min(buy, shop_buy.get(mat.lower(), buy))
for n, b in shop_buy.items():
    if n in price:
        price[n] = min(price[n], b * 0.5)

for rid, recs in recipes.items():
    out = name_of[int(rid)]
    if out not in price:
        continue
    for r in recs:
        ings = [name_of[i] for i in ingredients(r)]
        if ings and all(i in shop_buy for i in ings):
            cost = sum(shop_buy[i] for i in ings)
            if price[out] * r["result"]["count"] > cost:
                price[out] = cost / r["result"]["count"] * 0.5

# --------------------------------------------------------------------------------------------
# write files
# --------------------------------------------------------------------------------------------
def num(v):
    v = round(v, 2)
    return str(int(v)) if float(v).is_integer() else f"{v:.2f}".rstrip("0").rstrip(".")

def write_section(name, slot, icon, col, title, lore, hidden):
    with open(os.path.join(OUT, "sections", f"{name}.yml"), "w") as f:
        f.write(f"# DonutSMP-style '{name}' section. The file name must match shops/{name}.yml\n")
        f.write(f"enable: true\nslot: {slot}\ntitle: '&8ꜱʜᴏᴘ » {title}'\nhidden: {str(hidden).lower()}\n")
        f.write("sub-section: false\nfill-item:\n  material: BLACK_STAINED_GLASS_PANE\n  name: ' '\n")
        f.write(f"nav-bar:\n  mode: INHERIT\nitem:\n  material: {icon}\n  name: '{col}&l{title}'\n  lore:\n")
        for l in lore + ["", "&7ᴄʟɪᴄᴋ ᴛᴏ ᴏᴘᴇɴ"]:
            f.write(f"  - '{l}'\n")

def write_shop(name, header, pages):
    with open(os.path.join(OUT, "shops", f"{name}.yml"), "w") as f:
        f.write(header)
        f.write("pages:\n")
        idx = 1
        for p, (rows, entries) in enumerate(pages, 1):
            f.write(f"  page{p}:\n    gui-rows: {rows}\n    items:\n")
            for slot, mat, buy, sell, extra in entries:
                f.write(f"      '{idx}':\n        material: {mat}\n        buy: {num(buy)}\n"
                        f"        sell: {num(sell)}\n        slot: {slot}\n")
                if extra:
                    f.write(f"        {extra}\n")
                idx += 1

os.makedirs(os.path.join(OUT, "sections"), exist_ok=True)
os.makedirs(os.path.join(OUT, "shops"), exist_ok=True)
for d in ("sections", "shops"):
    for f in os.listdir(os.path.join(OUT, d)):
        os.remove(os.path.join(OUT, d, f))

# visible Donut shop: 3 content rows + nav bar, items centred in the middle rows like Donut
CENTER = [10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25]
in_shop_sell = set()
for name, (slot, icon, col, title, lore, its) in DONUT_SHOP.items():
    write_section(name, slot, icon, col, title, lore, False)
    entries = []
    # 9 items -> one centred row of 7 + 2 centred below, Donut-like
    slots = CENTER[:7] + [21, 23] if len(its) == 9 else CENTER
    for (mat, buy, extra), s in zip(its, slots):
        n = mat.lower()
        sell = -1
        if extra is None and n in price and n not in in_shop_sell:
            sell = price[n]
            in_shop_sell.add(n)
        entries.append((s, mat, buy, sell, extra))
    write_shop(name, f"# Exact DonutSMP /shop prices for '{name}'. buy/sell -1 = disabled.\n", [(4, entries)])

# hidden sell-only sections (Donut /sell worth) for every other item in the game
def category(n):
    if re.search(r"(_ore$|^raw_|_ingot$|_nugget$|^diamond$|^emerald$|^coal$|^charcoal$|^redstone$|^lapis_lazuli$|"
                 r"^quartz$|amethyst|^netherite_scrap$|^ancient_debris$|^(iron|gold|diamond|emerald|coal|redstone|"
                 r"lapis|copper|netherite|raw_\w+)_block$|^echo_shard$)", n):
        return "SellOres"
    if re.search(r"(_sword$|_pickaxe$|_axe$|_shovel$|_hoe$|_helmet$|_chestplate$|_leggings$|_boots$|_spear$|"
                 r"^bow$|^crossbow$|^trident$|^mace$|^shield$|^elytra$|_horse_armor$|_nautilus_armor$|^fishing_rod$|"
                 r"^shears$|^flint_and_steel$|^brush$|^spyglass$|^compass$|^recovery_compass$|^clock$|"
                 r"^carrot_on_a_stick$|^warped_fungus_on_a_stick$|^lead$|^saddle$|^wolf_armor$|_harness$|_smithing_template$)", n):
        return "SellGear"
    if re.search(r"(^rotten_flesh$|^bone|^string$|^spider_eye$|^gunpowder$|^slime|^leather$|^feather$|^ink_sac$|"
                 r"^glow_ink_sac$|^prismarine_(shard|crystals)$|^rabbit_(hide|foot)$|^phantom_membrane$|^blaze_|"
                 r"^ghast_tear$|^ender_(pearl|eye)$|^shulker_shell$|_scute$|^breeze_rod$|^wind_charge$|_head$|_skull$|"
                 r"^nether_star$|^dragon_|^heart_of_the_sea$|^nautilus_shell$|^honey|^egg$|_egg$|^magma_cream$|"
                 r"^totem_of_undying$|^arrow$|^spectral_arrow$|^heavy_core$|^trial_key$|^ominous_|^goat_horn$|^music_disc|"
                 r"^disc_fragment|_pottery_sherd$|_banner_pattern$|^name_tag$|^experience_bottle$)", n):
        return "SellMobs"
    if re.search(r"(wheat|carrot|potato|beetroot|melon|pumpkin|sugar|cactus|kelp|bamboo|cocoa|berries|apple|"
                 r"^bread$|^cookie$|^cake$|_pie$|_stew$|_soup$|^beef$|^porkchop$|^chicken$|^mutton$|^rabbit$|^cod$|"
                 r"^salmon$|^tropical_fish$|^pufferfish$|^cooked_|^nether_wart|^chorus_|_seeds$|^pitcher_pod$|"
                 r"^hay_block$|_sapling$|_propagule$|_mushroom$|_fungus$|^dried_kelp|^sea_pickle$|^lily_pad$|^vine$|"
                 r"_leaves$|^torchflower$|^pitcher_plant$|^dandelion$|^poppy$|_tulip$|^blue_orchid$|^allium$|"
                 r"^azure_bluet$|^oxeye_daisy$|^cornflower$|^lily_of_the_valley$|^wither_rose$|^sunflower$|^lilac$|"
                 r"^rose_bush$|^peony$|eyeblossom$|_dye$|^bone_meal$)", n):
        return "SellFarming"
    if re.search(r"(redstone|piston|repeater|comparator|observer|dropper|dispenser|hopper|lever|_button$|"
                 r"pressure_plate|tripwire|daylight|target|^tnt|rail$|minecart$|_lamp$|^crafter$|lightning_rod|note_block|"
                 r"^jukebox$|sculk_sensor|^bell$|^trapped_chest$)", n):
        return "SellRedstone"
    return "SellBlocks"

SELL_SECTIONS = OrderedDict([
    ("SellBlocks", "Building blocks"), ("SellFarming", "Crops, food and plants"),
    ("SellMobs", "Mob and spawner drops"), ("SellOres", "Ores, ingots and gems"),
    ("SellGear", "Tools, weapons and armour"), ("SellRedstone", "Redstone"),
])
groups = {k: [] for k in SELL_SECTIONS}
for n in all_names:
    if n in price and n not in shop_buy and price[n] > 0:
        groups[category(n)].append(n)

for sec, desc in SELL_SECTIONS.items():
    write_section(sec, 0, "CHEST", "&a", "ꜱᴇʟʟ", [f"&7{desc} (sell only)."], True)
    names = groups[sec]
    pages = []
    for i in range(0, len(names), 45):
        chunk = names[i:i + 45]
        pages.append((6, [(j, n.upper(), -1, price[n], None) for j, n in enumerate(chunk)]))
    write_shop(sec, f"# Sell-only /sell worth for {desc.lower()}. Hidden from /shop; used by /sellall and /sellgui.\n"
                    f"# Values estimated in DonutSMP scale (see README). buy: -1 = cannot be bought.\n", pages)

total = sum(len(v) for v in groups.values()) + len(shop_buy)
print(f"priced {len(price)} items, wrote {total} sellable materials")
print("unpriced (not sellable):", " ".join(unpriced) if unpriced else "none")
json.dump({k: round(v, 2) for k, v in sorted(price.items())}, open(os.path.join(OUT, "..", "prices.json"), "w"), indent=1)

# human-readable price list
def title(n):
    return n.replace("_", " ").title()
with open(os.path.join(OUT, "..", "PRICES.md"), "w") as f:
    f.write("# Price list\n\nGenerated by `tools/generate.py`. Edit the YAML files or the script, not this file.\n\n")
    f.write("## /shop (exact DonutSMP prices)\n\n")
    for name, (_, _, _, _, _, its) in DONUT_SHOP.items():
        f.write(f"### {name}\n\n| Item | Buy | Sell |\n|---|---:|---:|\n")
        for mat, buy, extra in its:
            n = mat.lower()
            label = "Arrow of Slow Falling" if extra else title(n)
            sell = "-" if extra or n not in price else f"${num(price[n])}"
            f.write(f"| {label} | ${num(buy)} | {sell} |\n")
        f.write("\n")
    f.write("## /sell only (estimated DonutSMP-scale worth)\n\n")
    for sec, desc in SELL_SECTIONS.items():
        f.write(f"### {desc}\n\n| Item | Sell |\n|---|---:|\n")
        for n in groups[sec]:
            f.write(f"| {title(n)} | ${num(price[n])} |\n")
        f.write("\n")
