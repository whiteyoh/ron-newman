# UK High School Builder (Roblox)

A Roblox Studio building game prototype where each player builds a house across **5 vertical levels** with a **UK high school** theme.

## Gameplay goals

- Every player gets their own plot.
- Building is snapped to a grid.
- Players can build on:
  1. Ground Floor
  2. First Floor
  3. Second Floor
  4. Third Floor
  5. Rooftop
- Theme styling uses school-like colors/materials (brick, plaster, classroom tile).
- Robux spending is supported via:
  - Developer Products (buy more build tokens)
  - Gamepass (Premium Builder perks)

## Roblox Studio setup

1. Open your place in Roblox Studio.
2. Create these services/folders if missing:
   - `ReplicatedStorage/Shared`
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
5. Press **Play** in Studio and test multiplayer behavior.

## Controls

- `Q / E`: Move down/up through building levels.
- `1 / 2 / 3`: Select material.
- `F`: Place a build part.
- `R`: Prompt Robux purchase for small token bundle.
- `T`: Prompt Robux purchase for Premium Builder gamepass.

## Notes on monetization

- Robux payments must be configured in your game creator dashboard.
- `MarketplaceService.ProcessReceipt` grants token boosts on successful purchases.
- Premium pass ownership is checked with `UserOwnsGamePassAsync`.

## Suggested next upgrades

- Add classroom-themed furniture and props.
- Save/load player builds with DataStore.
- Add house rating tied to school spirit score.
- Add roleplay NPCs (teacher, prefect, caretaker).
