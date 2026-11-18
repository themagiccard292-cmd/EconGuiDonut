#!/usr/bin/env python3
"""
Writes the DonutSMP prices into the server's own EconomyShopGUI layout.

  python3 tools/apply_prices.py            (reads template/ + prices.json, writes EconomyShopGUI/ + PRICES.md)

template/ is an untouched copy of the server's plugins/EconomyShopGUI/{sections,shops}. Everything in it
(titles, layouts, sub-sections, potions, books, spawners) is kept exactly; only the `buy:` and `sell:`
numbers are replaced:

  sell  = the item's /sell value from prices.json (x stack-size)
  buy   = exact DonutSMP /shop price for the 36 Donut items, otherwise sell x BUY_MULTIPLIER
  Potions, enchanted books, spawners and other items prices.json can't price keep the template's
  price, rescaled to the same money scale. Spawn eggs (buy 999999999) and sell: -1 are left alone.
  Items the template doesn't have are added to the hidden Z_EverythingElse shop.
"""
import json, os, re, shutil, statistics

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
TEMPLATE = os.path.join(ROOT, "template")
OUT = os.path.join(ROOT, "EconomyShopGUI")
BUY_MULTIPLIER = 4          # non-Donut items cost 4x what they sell for
DISABLED_BUY = 999999999    # template's "can't buy" marker (spawn eggs)
NO_SELL = {"potion", "splash_potion", "lingering_potion", "tipped_arrow", "enchanted_book"}

data = json.load(open(os.path.join(ROOT, "prices.json")))
SELL, SOURCE, DONUT_BUY = data["sell"], data["source"], data["donut_buy"]

ITEM_RE = re.compile(r"^      ([^\s#][^:]*):\s*$")
FIELD_RE = re.compile(r"^        ([a-z-]+):\s*(.*?)\s*$")
LIST_RE = re.compile(r"^        - (.*?)\s*$")


def fmt(v):
    v = round(v, 2)
    return str(int(v)) if float(v).is_integer() else f"{v:.2f}".rstrip("0").rstrip(".")


def nice(v):
    """Round to 3 significant figures (7154816.05 -> 7150000)."""
    if v <= 0:
        return v
    from math import floor, log10
    d = 3 - int(floor(log10(v))) - 1
    return round(v, d)


def parse_blocks(lines):
    """Yield (start, end, fields) for every item block (6-space key, 8-space fields)."""
    i = 0
    while i < len(lines):
        if ITEM_RE.match(lines[i].rstrip("\r\n")):
            j = i + 1
            fields, last = {}, None
            while j < len(lines):
                raw = lines[j].rstrip("\r\n")
                if raw.strip() == "" or not raw.startswith("        "):
                    break
                m = FIELD_RE.match(raw)
                if m:
                    last = m.group(1)
                    fields[last] = m.group(2).strip("'\"")
                elif LIST_RE.match(raw) and last:
                    fields.setdefault(last + "[]", []).append(LIST_RE.match(raw).group(1))
                j += 1
            yield i, j, fields
            i = j
        else:
            i += 1


def template_scale():
    """Ratio between our prices and the template's, used to rescale items we can't price."""
    ratios = []
    for dirpath, _, files in os.walk(os.path.join(TEMPLATE, "shops")):
        for f in files:
            lines = open(os.path.join(dirpath, f), newline="").readlines()
            for _, _, fl in parse_blocks(lines):
                mat = fl.get("material", "").lower()
                if mat in SELL and "sell" in fl and not any(k in fl for k in ("potiontypes", "enchantments", "spawnertype")):
                    try:
                        s = float(fl["sell"]) / float(fl.get("stack-size", 1) or 1)
                    except ValueError:
                        continue
                    if s > 0:
                        ratios.append(SELL[mat] / s)
    return statistics.median(ratios)


SCALE = template_scale()
seen = set()
report = []  # (file, display, buy, sell, source)


def new_prices(fl):
    mat = fl.get("material", "").lower()
    stack = float(fl.get("stack-size", 1) or 1)
    old_buy, old_sell = float(fl.get("buy", -1)), float(fl.get("sell", -1))
    special = any(k in fl for k in ("potiontypes", "enchantments", "spawnertype", "instrument"))
    potions = [p.lower() for p in fl.get("potiontypes[]", [])]

    if mat == "tipped_arrow" and "slow_falling" in potions and "tipped_arrow" in DONUT_BUY:
        buy, sell, src = DONUT_BUY["tipped_arrow"] * stack, old_sell * SCALE if old_sell > 0 else -1, "donut-shop"
    elif mat in SELL and not special:
        sell = SELL[mat] * stack
        if mat in DONUT_BUY:
            buy, src = DONUT_BUY[mat] * stack, "donut-shop"
        else:
            buy, src = sell * BUY_MULTIPLIER, SOURCE.get(mat, "estimate")
        if old_buy < 0:
            buy = -1
        if old_sell < 0:
            sell = -1
    else:  # potions, books, spawners, eggs, items prices.json doesn't cover
        buy = old_buy if old_buy < 0 or old_buy >= DISABLED_BUY else nice(old_buy * SCALE)
        sell = old_sell if old_sell < 0 else nice(old_sell * SCALE)
        src = "template-rescaled"
    # Brewing (3 potions per brew) and enchanting (bought XP bottles) would turn shop purchases into
    # profit, and Donut's /sell doesn't take these anyway: buy-only.
    if mat in NO_SELL:
        sell = -1
    return buy, sell, src


def rewrite(path, rel):
    lines = open(path, newline="").readlines()
    nl = "\r\n" if lines and lines[0].endswith("\r\n") else "\n"
    edits = {}
    for start, end, fl in parse_blocks(lines):
        if "buy" not in fl and "sell" not in fl:
            continue  # sub-section link button
        buy, sell, src = new_prices(fl)
        if "potiontypes" not in fl and "enchantments" not in fl and "spawnertype" not in fl:
            seen.add(fl.get("material", "").lower())
        label = ITEM_RE.match(lines[start].rstrip("\r\n")).group(1)
        report.append((rel, label, buy, sell, src))
        for k in range(start + 1, end):
            raw = lines[k].rstrip("\r\n")
            if raw.startswith("        buy:"):
                edits[k] = f"        buy: {fmt(buy)}{nl}"
            elif raw.startswith("        sell:"):
                edits[k] = f"        sell: {fmt(sell)}{nl}"
    for k, v in edits.items():
        lines[k] = v
    return lines, nl


if os.path.exists(OUT):
    shutil.rmtree(OUT)
shutil.copytree(os.path.join(TEMPLATE, "sections"), os.path.join(OUT, "sections"))
for dirpath, _, files in os.walk(os.path.join(TEMPLATE, "shops")):
    for f in sorted(files):
        src = os.path.join(dirpath, f)
        rel = os.path.relpath(src, os.path.join(TEMPLATE, "shops"))
        dst = os.path.join(OUT, "shops", rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        lines, _ = rewrite(src, rel)
        open(dst, "w", newline="").writelines(lines)

# add everything the template is missing to the hidden Z_EverythingElse shop
missing = [m for m in SELL if m not in seen]
missing += [m for m in DONUT_BUY if m not in seen and m not in SELL and m != "tipped_arrow"]
z = os.path.join(OUT, "shops", "Z_EverythingElse.yml")
zlines = open(z, newline="").readlines()
nl = "\r\n" if zlines and zlines[0].endswith("\r\n") else "\n"
pages = [int(m.group(1)) for m in (re.match(r"^  page(\d+):", l) for l in zlines) if m]
nxt = max(pages) + 1 if pages else 1
add = []
for i in range(0, len(missing), 45):
    add.append(f"{nl}  page{nxt}:{nl}    items:{nl}")
    for m in missing[i:i + 45]:
        sell = SELL.get(m, -1)
        buy = DONUT_BUY.get(m, sell * BUY_MULTIPLIER if sell > 0 else -1)
        add.append(f"      {m}:{nl}        material: {m.upper()}{nl}        buy: {fmt(buy)}{nl}        sell: {fmt(sell)}{nl}")
        report.append(("Z_EverythingElse.yml", m, buy, sell, "donut-shop" if m in DONUT_BUY else SOURCE.get(m, "estimate")))
    nxt += 1
if zlines and not zlines[-1].endswith(("\n", "\r")):
    zlines[-1] += nl
open(z, "w", newline="").writelines(zlines + add)

# PRICES.md
LABEL = {"donut-shop": "Donut /shop (exact)", "donut-sell": "Donut /sell (exact)", "donut-market": "Donut market",
         "crafted": "Crafted", "estimate": "Estimate", "template-rescaled": "Your template (rescaled)"}
by_file = {}
for rel, label, buy, sell, src in report:
    by_file.setdefault(rel, []).append((label, buy, sell, src))
with open(os.path.join(ROOT, "PRICES.md"), "w") as f:
    f.write("# Price list\n\nGenerated by `tools/apply_prices.py`; edit the scripts, not this file. "
            "Prices are for the item's stack size where the shop sells a bundle.\n\n")
    f.write("| Source | Meaning |\n|---|---|\n"
            "| Donut /shop (exact) | DonutSMP's real /shop buy price |\n"
            "| Donut /sell (exact) | DonutSMP's real /sell value |\n"
            "| Donut market | DonutSMP price-tracker price, converted to /sell |\n"
            "| Crafted | Sum of the ingredients' prices |\n"
            "| Estimate | No Donut data exists; scaled estimate |\n"
            "| Your template (rescaled) | Potions, books, spawners etc.: your original price, rescaled |\n\n")
    for rel in sorted(by_file):
        f.write(f"## shops/{rel}\n\n| Item | Buy | Sell | Source |\n|---|---:|---:|---|\n")
        for label, buy, sell, src in by_file[rel]:
            b = "-" if buy < 0 else ("disabled" if buy >= DISABLED_BUY else f"${fmt(buy)}")
            s = "-" if sell < 0 else f"${fmt(sell)}"
            f.write(f"| {label} | {b} | {s} | {LABEL[src]} |\n")
        f.write("\n")

counts = {}
for *_, src in report:
    counts[src] = counts.get(src, 0) + 1
print(f"template scale x{SCALE:.3f}; items: {len(report)}; added to Z_EverythingElse: {len(missing)}")
print(counts)
