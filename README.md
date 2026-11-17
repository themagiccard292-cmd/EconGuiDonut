# EconGuiDonut

A shop for [EconomyShopGUI](https://www.spigotmc.org/resources/economyshopgui.69927/) set up to look and work like the DonutSMP `/shop`.

## What's included

| Category | Menu slot | Icon | What's in it |
|---|---|---|---|
| **ᴇɴᴅ** | 11 | End Stone | Ender chests, pearls, end stone, chorus, purpur, shulker shells/boxes, dragon's breath |
| **ɴᴇᴛʜᴇʀ** | 12 | Netherrack | Blaze rods, nether wart, glowstone dust, magma cream, ghast tears, quartz, soul sand, crying obsidian… |
| **ɢᴇᴀʀ** | 14 | Totem | Obsidian, end crystals, respawn anchors, glowstone, totems, gapples, XP bottles, cobwebs, TNT… |
| **ꜰᴏᴏᴅ** | 15 | Steak | Golden carrots, steak, pork, bread, baked potatoes, pie… |
| *Sell* (hidden) | — | — | Sell-only prices for crops, spawner/mob drops, ores and common blocks. It doesn't show in `/shop`, but `/sellall` and `/sellgui` use it, like Donut's `/sell`. |

Style: small-caps titles (`ꜱʜᴏᴘ » ɢᴇᴀʀ`), black glass filler, 4-row category pages (3 rows of items plus the nav bar), and a click-to-open line on every category icon.

## Install

1. Install **EconomyShopGUI** (v6+ or Premium v5+), **Vault** and an economy plugin (EssentialsX, CMI, etc.). Start the server once so it creates its files, then stop it.
2. In `plugins/EconomyShopGUI/`, **back up and then delete** the default `sections/` and `shops/` folders.
3. Copy `EconomyShopGUI/sections` and `EconomyShopGUI/shops` from this repo into `plugins/EconomyShopGUI/`.
4. Start the server, or run `/sreload`.

### Make `/sell` open the sell GUI (as on Donut)
Add this to the server's root `commands.yml`:
```yaml
aliases:
  sell:
  - sellgui
```

### Main menu size
The category icons sit in slots 11, 12, 14 and 15 (0-based), the middle row of a 3-row menu. If your `config.yml` sets the main menu to more rows, set it to 3, or move the `slot:` value in each `sections/*.yml`.

## Editing prices
- Every item in `shops/<Category>.yml` has `buy:` and `sell:`. `-1` turns that side off.
- A material should appear in only one shop file, so sell prices stay clear.
- Section file names must match their shop file names (`sections/Gear.yml` ↔ `shops/Gear.yml`).

## Not included
- **Auction house / "market" (`/ah`)**: on Donut this is a player auction house. EconomyShopGUI can't do it, so pair this with an auction plugin such as zAuctionHouse or AuctionHouse.
- **Shard Shop**: it uses a second currency (shards). The free EconomyShopGUI only uses your Vault economy, so it was left out.
- **Exact Donut prices**: DonutSMP doesn't publish its shop prices. The numbers here are balanced estimates in Donut's style, so change them to fit your economy.
