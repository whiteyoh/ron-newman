# UK High School Builder (Roblox)

A Roblox Studio building game prototype where each player builds a house across **5 vertical levels** with a **UK high school** theme.

## Current feature set (implemented)

The prototype now includes:

- **Per-player build plots** created automatically at join.
- **Grid-snapped building** with level boundaries enforced across:
  1. Ground Floor
  2. First Floor
  3. Second Floor
  4. Third Floor
  5. Rooftop
- **Server-authoritative plot protection**:
  - Placement is blocked outside a player's own plot extents.
  - Placement is blocked when overlapping existing build objects.
- **Build UX upgrades**:
  - Undo/redo stack per player (`U` and `Y`).
  - Rotation (`C`) and structure resize (`Z`/`X`).
  - Local visual ghost preview while aiming placement.
- **Structure materials** with different spirit values and token costs (tier-gated inventory unlocks):
  - Brick
  - Plaster
  - ClassroomTile
  - PremiumGlass
  - NeonTrim
- **Placeable school props**:
  - StudentDesk
  - Blackboard
  - TrophyCase
  - PrefectBoard
  - SpiritSign (supports filtered player text)
- **Persistent inventory progression** based on Spirit unlock tiers.
- **School Spirit + House Rating system** that increases as players decorate.
- **Leaderboard stats + session awards**:
  - `leaderstats` for Spirit and HouseRating.
  - Session token awards for spirit milestones.
- **Roleplay NPC dialogue panel** with objectives/quests via UI.
- **Delete/select build tool** for precise cleanup of your own placed parts.
- **Plot visiting mode** to jump between active players' plots in-session.
- **DataStore persistence** for tokens, spirit score, inventory tier, and placed parts.
- **Save data versioning + migration** to support future schema evolution.
- **Moderation-safe text filtering** pipeline for sign text.
- **Performance safeguards**:
  - Max part cap per plot.
  - Reduced exploit risk via server validation checks.
- **Monetization hooks** for:
  - Developer Products (token bundles)
  - Gamepass (Premium Builder)
- **In-game HUD** showing theme, tokens, level, selected structure/prop, placement mode, spirit, rating, tier, ghost info, and feedback.

---

## Roblox Studio setup

### Option A (recommended): keep Studio pointed at this repo with Rojo sync

This repo now includes `roblox-game/default.project.json`, so Roblox Studio can continuously sync against the filesystem source.

1. Install **Rojo** (CLI) and the **Rojo Studio plugin**.
2. In a terminal, run:
   - `cd roblox-game`
   - `rojo serve`
3. In Roblox Studio, open your place, then start the Rojo plugin and connect to `localhost:34872`.
4. In the Rojo tree, use `default.project.json` from this folder. It maps:
   - `src/ReplicatedStorage` -> `ReplicatedStorage`
   - `src/ServerScriptService` -> `ServerScriptService`
   - `src/StarterGui` -> `StarterGui`
   - `src/StarterPlayer/StarterPlayerScripts` -> `StarterPlayer/StarterPlayerScripts`
5. Keep `rojo serve` running while editing. Changes in this repo will sync into Studio automatically.

### Option B: one-time manual import (no live sync)

1. Open your place in Roblox Studio.
2. Create these services/folders if missing:
   - `ReplicatedStorage/Shared`
   - `ReplicatedStorage/Remotes`
   - `ServerScriptService`
   - `StarterPlayer/StarterPlayerScripts`
   - `StarterGui`
3. Copy scripts from this repo into matching services:
   - `roblox-game/src/ReplicatedStorage/Shared/GameConfig.lua`
   - `roblox-game/src/ServerScriptService/HouseService.server.lua`
   - `roblox-game/src/ServerScriptService/MonetizationService.server.lua`
   - `roblox-game/src/StarterPlayer/StarterPlayerScripts/BuildController.client.lua`
   - `roblox-game/src/StarterGui/BuildHUD.client.lua`

### Required Studio settings/checklist

1. In `GameConfig.lua`, replace all placeholder IDs (`0`) for developer products/gamepasses with your real Roblox IDs.
2. Enable **Studio API Services** in Game Settings for DataStore testing in Studio.
3. Use **Test > Start Server** with multiple players to validate multiplayer placement and purchases.

---

## Roblox IDs you must provide

Set these in `roblox-game/src/ReplicatedStorage/Shared/GameConfig.lua`:

- `GameConfig.DeveloperProducts.BuildTokensSmall`
- `GameConfig.DeveloperProducts.BuildTokensLarge`
- `GameConfig.Gamepasses.PremiumBuilder`

### Where to get each ID (Creator Dashboard)

1. Open **https://create.roblox.com/** and choose the same experience/place you are testing in Studio.
2. For **developer product IDs**:
   - Go to **Monetization > Developer Products**.
   - Create products for "BuildTokensSmall" and "BuildTokensLarge" (or reuse existing ones).
   - Open each product and copy its numeric **Product ID**.
   - Paste into:
     - `BuildTokensSmall` -> `GameConfig.DeveloperProducts.BuildTokensSmall`
     - `BuildTokensLarge` -> `GameConfig.DeveloperProducts.BuildTokensLarge`
3. For the **gamepass ID**:
   - Go to **Monetization > Passes**.
   - Create/select your Premium Builder pass.
   - Open it and copy the numeric **Pass ID**.
   - Paste into `GameConfig.Gamepasses.PremiumBuilder`.

> Tip: IDs are numeric only. Do not paste full URLs.

---

## Controls

- `Q / E`: Move down/up through building levels.
- `1 / 2 / 3`: Select structure material.
- `4 / 5 / 6 / 7`: Select prop.
- `Z / X`: Resize structure footprint.
- `C`: Rotate placement by 90°.
- `U / Y`: Undo/redo last placement.
- `F`: Place currently selected structure/prop.
- `R`: Prompt Robux purchase for small token bundle.
- `T`: Prompt Robux purchase for Premium Builder gamepass.
- `G`: Select your placed part under cursor.
- `Backspace`: Delete selected part (server-validated, with token refund).
- `J / K`: Cycle plot visiting targets and teleport to view other players' builds.

---

## Monetization notes

- Robux payments must be configured in Creator Dashboard.
- `MarketplaceService.ProcessReceipt` grants token boosts on successful developer product purchases.
- `UserOwnsGamePassAsync` is used to check Premium Builder ownership.
- Keep product IDs and gamepass IDs in `GameConfig.lua` only, so they are easy to rotate per environment.

---

## Next recommendations / roadmap items

### Additional improvements roadmap (next 10)

1. ✅ **Delete/select tool** for precise removal and editing of existing placed parts.
2. ✅ **Plot visiting mode** so players can tour classmates' builds without edit permissions.
3. **Blueprint save slots** (multiple named layouts per player).
4. **Advanced snapping** (surface/edge snap + smart alignment guides).
5. **Collaborative co-build permissions** for invited friends on a plot.
6. **Quest progression tracking** with reward claims and daily objectives.
7. **Build replay/timelapse mode** from saved placement history.
8. **Config-driven seasonal events** for time-limited props and rewards.
9. **Admin moderation dashboard** for live cleanup/restore and player reports.
10. **Telemetry export hooks** for balancing economy, retention, and funnel metrics.

### Suggested longer-term upgrades

- Add classroom-themed furniture bundles and seasonal events.
- Add social mechanics (visit other plots, vote, school competitions).
- Add admin tools for live ops (boost events, cleanup, balancing).
- Add analytics events for placement flow and monetization conversion.
