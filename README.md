# EconGuiDonut

A DonutSMP-style `/shop` and `/sell` for [EconomyShopGUI](https://www.spigotmc.org/resources/economyshopgui.69927/), with prices for **every item in Minecraft 1.21.11**.

## Where the prices come from

| Part | Items | How accurate |
|---|---|---|
| `/shop`: End, Nether, Gear, Food | 36 | **Exact DonutSMP buy prices**, from the DonutSMP wiki's Shop page (the final version before Donut removed `/shop` on June 2, 2026). |
| `/sell` worth for everything else | ~1,320 | **Estimated.** DonutSMP has never published its `/sell` list. Raw items have hand-set values on Donut's scale, anchored to known Donut numbers (a dried kelp block sells for **$300** on Donut; here it's $299.97). Crafted items are priced from their recipes. |

The full list is in **[PRICES.md](PRICES.md)**.

Safety rules built into the prices:
- **No crafting profit.** A crafted item never sells for more than its ingredients, and a script checks every recipe in the game for this.
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
- **Older servers:** the item list targets 1.21.11. On an older version, EconomyShopGUI will warn about materials that don't exist yet (spears, nautilus armour, copper chests…) and skip them. Nothing else breaks.
- The main menu should be 3 rows. If yours is bigger, change the `slot:` values in `sections/*.yml`.

## Changing prices

- **One item:** edit its `buy:` / `sell:` in `shops/<Section>.yml`. `-1` turns that side off.
- **Re-balance everything:** edit the `BASE` values or `DONUT_SHOP` in `tools/generate.py`, then regenerate. Crafted items update to match automatically.
  ```bash
  npm pack minecraft-data && tar xzf minecraft-data-*.tgz
  python3 tools/generate.py package/minecraft-data/data/pc/1.21.11 EconomyShopGUI
  ```
  `prices.json` is the same list in machine-readable form, for other plugins.

## Not included
- **Shard Shop.** It used a second currency (shards), and its spawners were removed from Donut later. The free EconomyShopGUI only supports your Vault money.
- **Auction house / orders (`/ah`, `/orders`).** On Donut these are player-run markets. Use a separate plugin such as zAuctionHouse.
- **Sell multipliers.** Donut removed them in the June 2026 update.
