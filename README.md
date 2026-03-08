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

1. Open your place in Roblox Studio.
2. Create these services/folders if missing:
   - `ReplicatedStorage/Shared`
   - `ReplicatedStorage/Remotes`
   - `ServerScriptService`
   - `StarterPlayer/StarterPlayerScripts`
   - `StarterGui`
3. Copy scripts from this repo:
   - `roblox-game/src/ReplicatedStorage/Shared/GameConfig.lua`
   - `roblox-game/src/ServerScriptService/HouseService.server.lua`
   - `roblox-game/src/ServerScriptService/MonetizationService.server.lua`
   - `roblox-game/src/StarterPlayer/StarterPlayerScripts/BuildController.client.lua`
   - `roblox-game/src/StarterGui/BuildHUD.client.lua`
4. In `GameConfig.lua`, replace all placeholder IDs (`0`) for developer products/gamepasses with your real Roblox IDs.
5. Enable **Studio API Services** in Game Settings if you are testing DataStore behavior in Studio.
6. Use **Test > Start Server** with multiple players to validate multiplayer placement and purchases.

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

---

## Monetization notes

- Robux payments must be configured in Creator Dashboard.
- `MarketplaceService.ProcessReceipt` grants token boosts on successful developer product purchases.
- `UserOwnsGamePassAsync` is used to check Premium Builder ownership.
- Keep product IDs and gamepass IDs in `GameConfig.lua` only, so they are easy to rotate per environment.

---

## Additional improvements roadmap (next 10)

1. **Delete/select tool** for precise removal and editing of existing placed parts.
2. **Plot visiting mode** so players can tour classmates' builds without edit permissions.
3. **Blueprint save slots** (multiple named layouts per player).
4. **Advanced snapping** (surface/edge snap + smart alignment guides).
5. **Collaborative co-build permissions** for invited friends on a plot.
6. **Quest progression tracking** with reward claims and daily objectives.
7. **Build replay/timelapse mode** from saved placement history.
8. **Config-driven seasonal events** for time-limited props and rewards.
9. **Admin moderation dashboard** for live cleanup/restore and player reports.
10. **Telemetry export hooks** for balancing economy, retention, and funnel metrics.

---

## Suggested longer-term upgrades

- Add classroom-themed furniture bundles and seasonal events.
- Add social mechanics (visit other plots, vote, school competitions).
- Add admin tools for live ops (boost events, cleanup, balancing).
- Add analytics events for placement flow and monetization conversion.
