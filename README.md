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
- **Structure materials** with different spirit values and token costs:
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
- **School Spirit + House Rating system** that increases as players decorate.
- **Roleplay NPCs** (Teacher, Prefect, Caretaker) with interaction prompts.
- **DataStore persistence** for tokens, spirit score, and placed parts.
- **Monetization hooks** for:
  - Developer Products (token bundles)
  - Gamepass (Premium Builder)
- **In-game HUD** showing theme, tokens, level, selected structure/prop, placement mode, spirit, and rating.

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
- `4 / 5 / 6`: Select prop.
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

## How to get "developer status" for this project

Depending on what you mean by developer status, these are the common Roblox paths:

1. **Project collaborator status (team dev)**
   - Experience owner adds you under **Creator Dashboard > Experience > Collaborators**.
   - You are granted a role (e.g., edit scripts/build/upload assets).
   - For group-owned experiences, assign the role via the group's roles/permissions.

2. **Verified creator account readiness**
   - Create Roblox account and verify email (and phone where available).
   - Enable 2-Step Verification for account security.
   - Complete ID verification if your workflow needs features gated by verification/age.

3. **Monetization-ready developer (if earning Robux/USD is required)**
   - Configure payout/tax details in Creator Dashboard where required.
   - Enroll in Roblox programs needed for your region/use case (e.g., DevEx eligibility requirements).

---

## What you need from Roblox before publishing

Before setting the game to public, make sure you have:

- **Experience metadata**
  - Name, description, icon, and thumbnails.
- **Policy compliance**
  - Content aligns with Roblox Community Standards.
  - Correct age/content questionnaire selections.
- **Permissions and ownership**
  - Correct owner (personal or group) and collaborator permissions.
- **Monetization assets**
  - Created Developer Products and Gamepasses in Creator Dashboard.
  - IDs copied into `GameConfig.lua`.
- **Operational checks**
  - Live server test with 2+ players.
  - Placement, save/load, and purchase prompt flows validated.
- **Release configuration**
  - Set discoverability/access (private/friends/public) intentionally.
  - Confirm spawn, camera behavior, and mobile controls are acceptable.

---

## Additional improvements roadmap (next 10)

1. **Plot bounds validation** to block building outside owned plot extents.
2. **Server-side collision checks** to stop overlapping objects and exploit placement.
3. **Undo/redo stack** per player for better building UX.
4. **Rotate and resize controls** in build mode with visual ghost previews.
5. **Persistent inventory system** for unlockable props/material tiers.
6. **Leaderboard + session awards** tied to House Rating and Spirit gain.
7. **NPC dialogue UI panel** instead of print logs, with quests/objectives.
8. **Data versioning + migration layer** for safe updates to saved builds.
9. **Moderation-safe text filtering pipeline** for any user-entered signs/names.
10. **Performance pass** (streaming-friendly plots, part count limits, pooling).

---

## Suggested longer-term upgrades

- Add classroom-themed furniture bundles and seasonal events.
- Add social mechanics (visit other plots, vote, school competitions).
- Add admin tools for live ops (boost events, cleanup, balancing).
- Add analytics events for placement flow and monetization conversion.
