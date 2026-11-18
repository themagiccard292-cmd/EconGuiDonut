# EconGuiDonut

DonutSMP prices for **EconomyShopGUI**, in your server's own shop layout. Built for **Paper 26.3**.

## What's in the repo

| Folder / file | What it is |
|---|---|
| `EconomyShopGUI/sections/`, `EconomyShopGUI/shops/` | **Copy these to the server.** Your layout, with Donut prices. |
| `template/` | Your original files, untouched. The scripts read from here. |
| `PRICES.md` | Every item's buy/sell price and where it came from, file by file. |
| `prices.json` | Per-item price table (made by `tools/generate.py`). |
| `tools/` | The scripts that build everything. |

The layout matches your server exactly: the same 56 files, folders, titles, menu layouts and sub-sections. Only the `buy:` and `sell:` numbers changed.

```
sections/  and  shops/
├── building.yml   → Building/  decorative_blocks, natural, stone, wood
├── combat.yml     → Combat/    armor, redstone, tools, weapons
├── decoration.yml → Decoration/ decorative, dyes
├── farming.yml    → Farming/   crops, food
├── magic.yml      → Magic/     enchanting, potions
├── mobs.yml       → Mobs/      mob_drops, spawn_eggs, spawners
├── misc.yml, music.yml, resources.yml, storage.yml
└── Z_EverythingElse.yml   (hidden catch-all: 245 items your layout didn't have were added here, incl. all 26.x items)
```

## Where the prices come from

| Source | Items | Meaning |
|---|---|---|
| Donut /shop (exact) | 36 items | DonutSMP's real /shop buy prices (totem $1,500, end crystal $350, ender chest $2,500…), from the DonutSMP wiki |
| Donut /sell (exact) | 1 | Dried kelp block sells for $300 |
| Donut market | 42 | Real DonutSMP price-tracker prices, converted to /sell prices (× 300/1400, the dried kelp block ratio) |
| Crafted | ~1,020 | Sum of the ingredients' prices |
| Estimate | ~400 | No Donut data exists for these items; estimates scaled to the Donut figures above |
| Your template (rescaled) | ~330 | Potions, enchanted books, spawners, goat horns: your original prices × 31.8 to fit the same economy |

- **Sell** = the item's /sell value. **Buy** = the exact Donut price for Donut's /shop items, otherwise 4× the sell price.
- Prices cover the whole `stack-size` bundle (e.g. 4 carrots = 4 × $96).

### Exploit protection
- Crafting never makes money: no item sells for more than its ingredients (checked for every recipe in the game).
- Everything sells for less than it costs to buy (Donut items sell for at most 50% of buy, everything else 25%).
- **Potions, tipped arrows and enchanted books are buy-only.** Brewing makes 3 potions per brew, so selling them would be an infinite money loop.
- Spawners and spawn eggs keep your template's settings (spawners buy-only; spawn eggs disabled at 999999999).

## Install
1. Back up `plugins/EconomyShopGUI/`.
2. Copy `EconomyShopGUI/sections` and `EconomyShopGUI/shops` from this repo over the ones on your server (replace the files).
3. Run `/sreload` (or restart), then check the console for "invalid material" warnings. The 26.2/26.3 item IDs follow vanilla naming; a wrong one only skips that item.

## Changing prices
- **One item:** edit it in `EconomyShopGUI/shops/...`, or (better, so it survives a rebuild) change it in the scripts.
- **Rebuild everything:**
  ```bash
  npm pack minecraft-data && tar xzf minecraft-data-*.tgz
  python3 tools/generate.py package/minecraft-data/data/pc/26.1   # -> prices.json
  python3 tools/apply_prices.py                                    # template/ + prices.json -> EconomyShopGUI/ + PRICES.md
  ```
  - Donut /shop prices and base values: `DONUT_SHOP`, `BASE` and `DONUT_MARKET` in `tools/generate.py`
  - Buy markup (default 4×) and buy-only items: `BUY_MULTIPLIER` and `NO_SELL` in `tools/apply_prices.py`
  - Changed the layout on your server? Replace `template/` with your new files and run `apply_prices.py` again.
