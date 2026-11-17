# EconGuiDonut

A DonutSMP-style `/shop` and `/sell` for [EconomyShopGUI](https://www.spigotmc.org/resources/economyshopgui.69927/), with prices for **every item in Minecraft 26.3**, built for **Paper 26.3**.

## Where the prices come from

| Source (shown per item in [PRICES.md](PRICES.md)) | Items | What it means |
|---|---|---|
| **Donut /shop** | 36 | Exact DonutSMP buy prices, from the DonutSMP wiki's Shop page (the final version before Donut removed `/shop` on June 2, 2026). |
| **Donut /sell** | 1 | Exact Donut `/sell` value: a dried kelp block sells for **$300**. |
| **Donut market** | ~40 | Real DonutSMP player-market prices from Donut price trackers (donutsmp.finance, donutsmpterminal.com, donut.build, donut.today, donutstats.io), turned into `/sell` prices with the one ratio known for sure: a dried kelp block trades for about $1.4K and sells for $300, so `/sell` ≈ market × 0.214. Where trackers disagreed, the lowest believable figure was used. |
| **Crafted** | ~890 | Priced from the Donut figures above: the sum of the ingredients ÷ how many items the recipe makes. |
| **Estimate** | ~390 | No Donut data exists for these. Hand-set values, scaled (×3.57) to match the real Donut figures. |

Tracker prices left out on purpose: netherrack ($766), sand ($873) and red sand ($539). These blocks can be mined endlessly, and those prices came from thin, spiking markets. Using them would make `/sell` farming absurd.

Safety rules built into the prices:
- **No crafting profit.** No item sells for more than its ingredients, and the generator enforces this for every recipe in the game. Raw items and ores are also capped at the value of what they smelt or mine into.
- **No shop flipping.** Items you can buy in `/shop` sell for at most 50% of their buy price.
- **Not sellable:** creative-only items (spawn eggs, command blocks, bedrock, etc.) and items whose value depends on NBT data (potions, enchanted books, player heads, written books).

## What's in the shop

Main menu (3 rows), like Donut's: **ᴇɴᴅ · ɴᴇᴛʜᴇʀ · ɢᴇᴀʀ · ꜰᴏᴏᴅ** in slots 11–14 (0-based).

| End | Nether | Gear | Food |
|---|---|---|---|
| Ender Chest $2,500 | Blaze Rod $150 | Obsidian $100 | Potato $96 |
| Ender Pearl $75 | Nether Wart $96 | End Crystal $350 | Sweet Berries $50 |
| End Stone $8 ($128 / 16) | Glowstone Dust $15 | Respawn Anchor $1,000 | Melon Slice $36 |
| Dragon's Breath $1,000 | Magma Cream $96 | Glowstone $100 | Carrot $96 |
| End Rod $100 | Ghast Tear $350 | Totem of Undying $1,500 | Apple $25 |
| Chorus Fruit $108 | Nether Quartz $30 | Ender Pearl $75 | Cooked Chicken $48 |
| Popped Chorus Fruit $24 | Soul Sand $50 | Golden Apple $250 | Steak $35 |
| Shulker Shell $350 | Magma Block $35 | Bottle o' Enchanting $100 | Golden Carrot $120 |
| Shulker Box $800 | Crying Obsidian $150 | Arrow of Slow Falling $500 | Golden Apple $250 |

The sell-only items are in six **hidden** sections (`SellBlocks`, `SellFarming`, `SellMobs`, `SellOres`, `SellGear`, `SellRedstone`). They don't appear in `/shop`, but `/sellall` and `/sellgui` use them.

## Install

1. Install **EconomyShopGUI** (v6+ or Premium v5+), **Vault** and an economy plugin (EssentialsX, CMI, etc.). Start the server once, then stop it.
2. In `plugins/EconomyShopGUI/`, **back up and then delete** the default `sections/` and `shops/` folders.
3. Copy `EconomyShopGUI/sections` and `EconomyShopGUI/shops` from this repo into `plugins/EconomyShopGUI/`.
4. Start the server, or run `/sreload`.

### Make `/sell` open the sell GUI (as on Donut)
In the server's root `commands.yml`:
```yaml
aliases:
  sell:
  - sellgui
```

### Check after the first load
- **Arrow of Slow Falling** uses `potiontypes: SLOW_FALLING` (in `shops/Gear.yml`). If it shows up as a plain tipped arrow, fix that line to match your EconomyShopGUI version's potion format.
- **Server version:** built for **Paper 26.3** (Java 25), so use an EconomyShopGUI build that supports 26.3. It includes the 26.2 *Chaos Cubed* items (cinnabar and sulfur sets, potent sulfur, sulfur spike, the Bounce disc, sulfur cube bucket) and the 26.3 *Wilderness Bound* items (the poplar wood set, wool and concrete stairs and slabs, red shrub, shelf mushroom, straw bed). Their IDs follow vanilla naming. If one is spelled differently in-game, EconomyShopGUI will log a warning and skip only that item.
- The main menu should be 3 rows. If yours is bigger, change the `slot:` values in `sections/*.yml`.

## Changing prices

- **One item:** edit its `buy:` / `sell:` in `shops/<Section>.yml`. `-1` turns that side off.
- **Re-balance everything:** edit the `BASE` values or `DONUT_SHOP` in `tools/generate.py`, then regenerate. Crafted items update to match automatically.
  ```bash
  npm pack minecraft-data && tar xzf minecraft-data-*.tgz
  python3 tools/generate.py package/minecraft-data/data/pc/26.1 EconomyShopGUI   # 26.2/26.3 items are added by the script
  ```
  `prices.json` is the same list in machine-readable form, for other plugins.

## Not included
- **Shard Shop.** It used a second currency (shards), and its spawners were removed from Donut later. The free EconomyShopGUI only supports your Vault money.
- **Auction house / orders (`/ah`, `/orders`).** On Donut these are player-run markets. Use a separate plugin such as zAuctionHouse.
- **Sell multipliers.** Donut removed them in the June 2026 update.
