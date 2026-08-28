# Bulk Product Import — from client reference file → stone.material

Reusable toolkit for loading a client's raw product-code reference file
(Excel, `master` + `attributes` pair) into this module's data model
(`stone.material` + Block/Slab/FG `product.template`). Built 2026-08-28
importing EMG-O's real 51-material list into `mbx-ee-dev` (Session 93 — see
`claude-knowledge/projects/emg-o/log.md` for the full narrative, including 2
real bugs found+fixed the first time this ran).

**Expect to run this again** on a fresh DB — per the 2026-08-28 plan, the
`mbx-ee-dev` run was a rehearsal, not the real target. The actual load is
meant to happen on a **new dedicated DB** (not `eg-tst`), because the
current dev DB is expected to be deleted eventually anyway (Enterprise
license is DB-locked). Do NOT assume `mbx-ee-dev`'s current data is the
canonical copy — treat it as disposable, same as the DB itself.

## What it does

1. **`1_parse_client_files.py`** (run on the HOST — needs `xlrd`+`openpyxl`,
   not available inside the Odoo container) — reads the client's 2 Excel
   files, groups rows into materials by shared code prefix, normalizes
   name/whitespace inconsistencies, maps Finish/Surface values onto this
   module's `product.attribute` values, flags anything that needs a human
   decision (missing rows, name conflicts), writes a clean JSON.
2. **`2_run_import.py`** (run inside `odoo shell`) — creates `stone.material`
   + Block/Slab/FG products from that JSON, plus any non-stone auxiliary
   products (cost-line/site-material rows). Always supports a `DRY_RUN`
   pass first.
3. **`3_set_placeholder_price_density.py`** (OPTIONAL, `odoo shell`) — only
   if told to fill in non-real price/density placeholders because a
   downstream flow needs non-zero values. Leaving things at 0/blank is the
   more honest default otherwise.

## Prerequisites before running

- [ ] `stone_slab_inventory` module up to date on the target DB (`-u` +
      container restart if you just edited `.py` files).
- [ ] The `Finish` `product.attribute` (`stone_slab_inventory.product_attribute_finish`)
      already has every value the source file references. Check
      `data/stone_finish_attribute_data.xml` in the module against step 1's
      printed Finish-value list — if the client's file introduces a name
      step 1 doesn't recognize (extend `FINISH_MAP` in step 1 first), add
      any genuinely new value to that XML file + `stone.bundle.finish`
      Selection + `stone.material._FINISH_ATTRIBUTE_VALUE_XMLIDS` in
      `models/stone_material.py`, same pattern as the existing 8 values.
- [ ] The FG product category (`Stone FG - Countertop` by default — change
      `FG_CATEGORY_NAME` in step 2 if this DB's real category has a
      different name) already exists with its Operations/Labor Cost set up
      (ADR-029). This script does not create it.
- [ ] Know the target container name + DB connection args (`--db_host
      --db_port --db_user --db_password`) — find the running container's
      real values with:
      `docker exec <container> ps aux | grep odoo` (shows the live
      `--db_host/--db_port/--db_user/--db_password` the container itself
      was started with).
- [ ] Know the bind-mount mapping for getting the step-1 JSON into the
      container (`docker inspect <container> --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'`)
      — copy the JSON into the host side of whatever maps to `/mnt/extra-addons`
      (or wherever), matching `JSON_PATH` in steps 2/3. **Delete the copy
      from the host addons dir again after the run** — it's scratch data,
      never commit it.

## Run order

```bash
# 1. Parse (on host)
python3 1_parse_client_files.py \
    /path/to/product-template-master.xls \
    /path/to/product-template-attributes.xlsx \
    /tmp/import_data.json

# review the printed summary — especially "skipped" and "name conflicts",
# both need a human decision, not a guess, before continuing

# 2. Copy into the container's mount, dry-run, review, then real run
cp /tmp/import_data.json <host-addons-dir>/.import_scratch.json
docker exec -i <container> odoo shell -d <db> \
    --db_host <host> --db_port <port> --db_user <user> --db_password '<pw>' \
    --no-http < 2_run_import.py
# (edit DRY_RUN=False in the script once the dry-run output looks right)

# 3. (optional) placeholder pricing
docker exec -i <container> odoo shell -d <db> \
    --db_host <host> --db_port <port> --db_user <user> --db_password '<pw>' \
    --no-http < 3_set_placeholder_price_density.py

# cleanup
rm <host-addons-dir>/.import_scratch.json
docker restart <container>  # only needed if you edited module .py files this session
```

## Always verify after, don't trust the script's own summary

The 2026-08-28 run genuinely had 2 real bugs that only surfaced on a full
post-import integrity check (comparing every created record's actual field
values against the source JSON, not just trusting "COMMITTED"). At minimum,
re-derive and check:

```python
for m in data['materials']:
    mat = env['stone.material'].search([('name', '=', m['name'])], limit=1)
    assert mat, m['name']
    assert mat.product_id.default_code == m['slab_code'], mat.name
    assert mat.product_id_block.default_code == m['block_code'], mat.name
    fg = env['product.template'].search([('stone_fg_material_id', '=', mat.id)], limit=1)
    assert fg.default_code == m['fg_code'], mat.name
```

Then eyeball at least one real record in the browser (Stone Slab app →
Configuration → Materials) — a passing script assertion is not the same as
a correctly-rendering record.

## Known real-world data quirks to expect (not code bugs — client-file issues)

- Rows with an incomplete BL/SL/FG triplet (e.g. no Slab row at all) —
  `stone.material.product_id` is required, so these get skipped. Needs the
  client to fill the gap, not a guess.
- Two rows landing on the *same* material name after normalization (e.g. a
  copy-paste error in the client's own file gave one material's Slab row a
  different stone name than its Block/FG rows) — step 1's majority-vote
  logic picks the 2-of-3 name and flags it as a `name_conflicts` entry, but
  if that chosen name collides with a *different*, real, separate material,
  the colliding one silently gets skipped in step 2 (shows up in "materials
  skipped (already exist)"). Always cross-reference that skip list against
  step 1's `name_conflicts` output — a real one needs client clarification,
  don't just assume it's a genuine dupe.
