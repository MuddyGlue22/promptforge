# Gallery archive

Earlier runs of the gallery, kept for a future write-up on how the builder and the site evolved. Every image here is exactly as downloaded: never cropped, retouched or re-encoded.

## Run 1: Siray (21 November 2026)

- 12 characters generated through siray.ai on several models (FLUX, Seedream, GPT Image and others; see `characters.json`).
- The first gallery, built in commit `0671ca4`. Never went live: Siray's terms restrict commercial use and public display, which led to the switch to OpenMov.
- **The images are kept on the local machine only** (`run1-siray/images/` is in `.gitignore`), because their display rights were never cleared and this repository is public. `characters.json` and `prompts.md` are the versions from `0671ca4`.
- Notable lessons: FLUX added a D&D logo until game names were taken out of the prompt, and kept "signing" its oil paintings.

## Run 2: OpenMov (22 November 2026)

- 12 characters on Seedream 5 Pro, Nano Banana 2.1, Qwen Image Pro and WAN 2.7 Pro (three each), paid credits. Live from commit `89c621c`.
- Added the same day: the Dwarf Warrior comparisons (one prompt, four models; then the Painted miniature on two models) and character 13.
- `13-dwarf-warrior-miniature-first-try.png` is the first Painted miniature (Seedream). It was framed three-quarter, cropping the base, which led to the builder always asking for full body with that style. Its prompt and notes are in commit `07b254d`.
- Builder fixes that came out of this run, and prompted run 3: greataxes drawn as hand axes, Katari looking like house cats, the Daggerheart ancestry list and descriptions checked against the rulebook, giants that didn't look like giants.
- `characters.json` and `comparisons.json` are the live data at the end of the run; `prompts.md` is the run-2 prompt sheet.

## Run 3

In progress. Sources go in `gallery/run3/`; see `gallery/prompts.md`.
