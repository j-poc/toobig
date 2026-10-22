# toobig

Every US company filing 10-Qs gets a next-quarter revenue forecast with an 80% range, written down before the actual is filed.

Site: https://j-poc.github.io/toobig/

This branch is the published site. It is replaced once a day, after the build from that morning's SEC data.

## Check that no forecast was changed after the fact

`ledger/forecasts.jsonl` holds one forecast per line, in the order they were written.
- Each line's `hash` is the sha256 of its other fields, serialized as JSON with sorted keys and no spaces.
- Each line's `prev` is the `hash` of the line before it. For the first line, `prev` is 64 zeros.
- So changing, removing or reordering any past line breaks every hash after it.

```sh
curl -sO https://j-poc.github.io/toobig/verify.py
mkdir -p ledger && curl -s https://j-poc.github.io/toobig/ledger/forecasts.jsonl -o ledger/forecasts.jsonl
python3 verify.py ledger/forecasts.jsonl     # recomputes every hash; prints the head
```

Keep that file. On a later day, download the ledger again and run `python3 verify.py ledger/forecasts.jsonl old.jsonl` (where `old.jsonl` is the file you kept). It checks that today's ledger starts with your copy byte for byte, so nothing in it was edited or dropped.

To also check the anchors, clone this repository and run `python3 verify.py ledger/forecasts.jsonl` inside it. You need the clone because Pages does not list directories.

## Check when the ledger existed

`ledger/anchors/<seq>.json` is the 2-field file `{"seq":N,"hash":H}`, where H is the hash of entry N. `verify.py` checks that each anchor matches the ledger.

`<seq>.json.ots` is an [OpenTimestamps](https://opentimestamps.org) proof that the anchor file existed by a Bitcoin block's time. Because entry N's hash commits to entries 0 to N, the proof dates every one of them. To check a proof, use either:
- `ots verify ledger/anchors/<seq>.json.ots`. This needs a Bitcoin node.
- [opentimestamps.org](https://opentimestamps.org): drop in both the `.ots` and its `.json`.

A new proof stays pending until a Bitcoin block confirms it, usually within a few hours. The daily run upgrades pending proofs to complete ones. When the client upgrades a proof, it keeps the pending version as `<seq>.json.ots.bak`.

## What counts

A forecast is scored only if its actual was first filed after the day the forecast was written. Each scored forecast gets a tier:
- **gold:** written before its quarter ended;
- **silver:** written after its quarter ended, but before the actual was filed.

A forecast whose actual was filed on or before its writing day is void and never scored, because a date alone cannot show which came first.
