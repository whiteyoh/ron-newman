local DataStoreService = game:GetService("DataStoreService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TextService = game:GetService("TextService")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local GameConfig = require(Shared:WaitForChild("GameConfig"))

local BUILD_DATASTORE = DataStoreService:GetDataStore("PlayerBuilds_v2")

local RemotesFolder = ReplicatedStorage:FindFirstChild("Remotes")
if not RemotesFolder then
    RemotesFolder = Instance.new("Folder")
    RemotesFolder.Name = "Remotes"
    RemotesFolder.Parent = ReplicatedStorage
end

local PlaceRequest = RemotesFolder:FindFirstChild("PlaceRequest") or Instance.new("RemoteEvent")
PlaceRequest.Name = "PlaceRequest"
PlaceRequest.Parent = RemotesFolder

local BuildStateRequest = RemotesFolder:FindFirstChild("BuildStateRequest") or Instance.new("RemoteFunction")
BuildStateRequest.Name = "BuildStateRequest"
BuildStateRequest.Parent = RemotesFolder

local BuildActionRequest = RemotesFolder:FindFirstChild("BuildActionRequest") or Instance.new("RemoteEvent")
BuildActionRequest.Name = "BuildActionRequest"
BuildActionRequest.Parent = RemotesFolder

local NpcDialogueEvent = RemotesFolder:FindFirstChild("NpcDialogueEvent") or Instance.new("RemoteEvent")
NpcDialogueEvent.Name = "NpcDialogueEvent"
NpcDialogueEvent.Parent = RemotesFolder

local BuildFeedbackEvent = RemotesFolder:FindFirstChild("BuildFeedbackEvent") or Instance.new("RemoteEvent")
BuildFeedbackEvent.Name = "BuildFeedbackEvent"
BuildFeedbackEvent.Parent = RemotesFolder

local plotsFolder = workspace:FindFirstChild("PlayerPlots")
if not plotsFolder then
    plotsFolder = Instance.new("Folder")
    plotsFolder.Name = "PlayerPlots"
    plotsFolder.Parent = workspace
end

local leaderboard = Instance.new("Folder")
leaderboard.Name = "HouseLeaderboard"
leaderboard.Parent = ReplicatedStorage

local spiritRank = Instance.new("IntValue")
spiritRank.Name = "TopSpirit"
spiritRank.Parent = leaderboard

local playerState = {}

local function snap(value)
    local g = GameConfig.GridSize
    return math.floor((value / g) + 0.5) * g
end

local function withinAnyLevel(y)
    for levelIndex, level in ipairs(GameConfig.Levels) do
        if y >= level.MinY and y <= level.MaxY then
            return true, levelIndex
        end
    end
    return false, nil
end

local function calculateHouseRating(spiritScore)
    return math.clamp(math.floor(spiritScore / 20) + 1, 1, 5)
end

local function serializePart(part)
    return {
        name = part.Name,
        position = { part.Position.X, part.Position.Y, part.Position.Z },
        size = { part.Size.X, part.Size.Y, part.Size.Z },
        color = { part.Color.R, part.Color.G, part.Color.B },
        material = part.Material.Name,
        orientation = { part.Orientation.X, part.Orientation.Y, part.Orientation.Z },
        text = part:GetAttribute("UserText"),
    }
end

local function materialFromName(materialName)
    local ok, material = pcall(function()
        return Enum.Material[materialName]
    end)

    if ok and material then
        return material
    end

    return Enum.Material.SmoothPlastic
end

local function determineTier(spiritScore)
    local unlockedTier = 1
    for tier, tierInfo in pairs(GameConfig.MaterialTiers) do
        if spiritScore >= tierInfo.RequiredSpirit then
            unlockedTier = math.max(unlockedTier, tier)
        end
    end
    return unlockedTier
end

local function getBounds(baseplate)
    local halfX = baseplate.Size.X / 2
    local halfZ = baseplate.Size.Z / 2
    return {
        minX = baseplate.Position.X - halfX,
        maxX = baseplate.Position.X + halfX,
        minZ = baseplate.Position.Z - halfZ,
        maxZ = baseplate.Position.Z + halfZ,
    }
end

local function isInsidePlot(baseplate, position, size)
    local bounds = getBounds(baseplate)
    local halfX = size.X / 2
    local halfZ = size.Z / 2

    return position.X - halfX >= bounds.minX
        and position.X + halfX <= bounds.maxX
        and position.Z - halfZ >= bounds.minZ
        and position.Z + halfZ <= bounds.maxZ
end

local function intersectsExisting(state, position, size)
    local padding = 0.1
    local min = position - (size / 2) + Vector3.new(padding, padding, padding)
    local max = position + (size / 2) - Vector3.new(padding, padding, padding)

    for _, other in ipairs(state.BuildParts:GetChildren()) do
        if other:IsA("Part") then
            local otherMin = other.Position - (other.Size / 2)
            local otherMax = other.Position + (other.Size / 2)
            local overlap = min.X < otherMax.X and max.X > otherMin.X
                and min.Y < otherMax.Y and max.Y > otherMin.Y
                and min.Z < otherMax.Z and max.Z > otherMin.Z

            if overlap then
                return true
            end
        end
    end

    return false
end

local function updateLeaderboard()
    local topSpirit = 0
    for _, state in pairs(playerState) do
        topSpirit = math.max(topSpirit, state.SpiritScore)
    end
    spiritRank.Value = topSpirit
end

local function createPartFromData(partData, parent)
    local part = Instance.new("Part")
    part.Name = partData.name or "Build_Restore"
    part.Position = Vector3.new(partData.position[1], partData.position[2], partData.position[3])
    part.Size = Vector3.new(partData.size[1], partData.size[2], partData.size[3])
    part.Color = Color3.new(partData.color[1], partData.color[2], partData.color[3])
    part.Material = materialFromName(partData.material)
    part.Orientation = Vector3.new((partData.orientation or { 0, 0, 0 })[1], (partData.orientation or { 0, 0, 0 })[2], (partData.orientation or { 0, 0, 0 })[3])
    part.Anchored = true
    part.TopSurface = Enum.SurfaceType.Smooth
    part.BottomSurface = Enum.SurfaceType.Smooth
    part.Parent = parent

    if type(partData.text) == "string" and partData.text ~= "" then
        part:SetAttribute("UserText", partData.text)
        local billboard = Instance.new("BillboardGui")
        billboard.Name = "TextBillboard"
        billboard.Size = UDim2.new(0, 200, 0, 50)
        billboard.StudsOffset = Vector3.new(0, 4, 0)
        billboard.AlwaysOnTop = true
        billboard.Parent = part

        local label = Instance.new("TextLabel")
        label.Size = UDim2.fromScale(1, 1)
        label.BackgroundTransparency = 0.25
        label.BackgroundColor3 = Color3.fromRGB(16, 20, 27)
        label.TextColor3 = Color3.fromRGB(255, 255, 255)
        label.TextScaled = true
        label.Font = Enum.Font.GothamBold
        label.Text = partData.text
        label.Parent = billboard
    end

    return part
end

local function pushUndo(state, action)
    table.insert(state.UndoStack, action)
    if #state.UndoStack > GameConfig.MaxUndoHistory then
        table.remove(state.UndoStack, 1)
    end
    state.RedoStack = {}
end

local function addSessionAwards(state)
    local steps = math.floor(state.SpiritScore / GameConfig.SessionAwardSpiritStep)
    if steps > state.SessionAwardSteps then
        local gained = (steps - state.SessionAwardSteps) * 5
        state.Tokens += gained
        state.SessionAwardSteps = steps
        BuildFeedbackEvent:FireClient(state.Player, string.format("Session award: +%d tokens for spirit milestones", gained))
    end
end

local function updateSpirit(state, delta)
    state.SpiritScore = math.max(0, state.SpiritScore + delta)
    state.HouseRating = calculateHouseRating(state.SpiritScore)
    state.UnlockedTier = determineTier(state.SpiritScore)
    addSessionAwards(state)
    updateLeaderboard()
end

local function spawnRoleplayNPC(plot, basePosition)
    local npcFolder = Instance.new("Folder")
    npcFolder.Name = "RoleplayNPCs"
    npcFolder.Parent = plot

    for _, npc in ipairs(GameConfig.RoleplayNPCs) do
        local body = Instance.new("Part")
        body.Name = npc.Name
        body.Size = Vector3.new(2, 5, 2)
        body.Position = basePosition + npc.PositionOffset
        body.Anchored = true
        body.Material = Enum.Material.SmoothPlastic
        body.Color = npc.Color
        body.Parent = npcFolder

        local prompt = Instance.new("ProximityPrompt")
        prompt.ActionText = "Talk"
        prompt.ObjectText = npc.Title
        prompt.HoldDuration = 0
        prompt.MaxActivationDistance = 10
        prompt.Parent = body

        prompt.Triggered:Connect(function(player)
            NpcDialogueEvent:FireClient(player, {
                title = npc.Title,
                dialogue = npc.Dialogue,
                objective = npc.Quest,
            })
        end)
    end
end

local function createPlotForPlayer(player)
    local plot = Instance.new("Model")
    plot.Name = player.Name .. "_Plot"
    plot.Parent = plotsFolder

    local baseplate = Instance.new("Part")
    baseplate.Name = "Baseplate"
    baseplate.Size = Vector3.new(GameConfig.PlotSize.X, 1, GameConfig.PlotSize.Z)
    baseplate.Position = Vector3.new((player.UserId % 8) * (GameConfig.PlotSize.X + 20), 0, 0)
    baseplate.Anchored = true
    baseplate.Material = Enum.Material.Concrete
    baseplate.Color = Color3.fromRGB(92, 92, 92)
    baseplate.Parent = plot

    for i, level in ipairs(GameConfig.Levels) do
        local marker = Instance.new("Part")
        marker.Name = "LevelMarker_" .. i
        marker.Size = Vector3.new(GameConfig.PlotSize.X, 0.5, GameConfig.PlotSize.Z)
        marker.Position = Vector3.new(baseplate.Position.X, level.MinY, baseplate.Position.Z)
        marker.Anchored = true
        marker.CanCollide = false
        marker.Transparency = 0.85
        marker.Color = level.StudColor
        marker.Parent = plot
    end

    local builds = Instance.new("Folder")
    builds.Name = "BuildParts"
    builds.Parent = plot

    playerState[player] = {
        Player = player,
        Plot = plot,
        Baseplate = baseplate,
        BuildParts = builds,
        Tokens = 50,
        SpiritScore = 0,
        HouseRating = 1,
        UnlockedTier = 1,
        UndoStack = {},
        RedoStack = {},
        SessionAwardSteps = 0,
        NextPartId = 0,
    }

    spawnRoleplayNPC(plot, baseplate.Position)
end

local function migrateData(data)
    if type(data) ~= "table" then
        return nil
    end

    local version = tonumber(data.version) or 1
    if version < 2 then
        data.inventoryTier = data.inventoryTier or 1
        version = 2
    end

    data.version = version
    return data
end

local function restoreParts(parts, parent)
    for _, partData in ipairs(parts or {}) do
        createPartFromData(partData, parent)
    end
end

local function savePlayerBuild(player)
    local state = playerState[player]
    if not state then
        return
    end

    local buildParts = {}
    for _, part in ipairs(state.BuildParts:GetChildren()) do
        if part:IsA("Part") then
            table.insert(buildParts, serializePart(part))
        end
    end

    local payload = {
        version = GameConfig.DataVersion,
        tokens = state.Tokens,
        spiritScore = state.SpiritScore,
        inventoryTier = state.UnlockedTier,
        buildParts = buildParts,
    }

    pcall(function()
        BUILD_DATASTORE:SetAsync(tostring(player.UserId), payload)
    end)
end

local function loadPlayerBuild(player)
    local state = playerState[player]
    if not state then
        return
    end

    local success, data = pcall(function()
        return BUILD_DATASTORE:GetAsync(tostring(player.UserId))
    end)

    if not success then
        return
    end

    data = migrateData(data)
    if not data then
        return
    end

    state.Tokens = tonumber(data.tokens) or state.Tokens
    state.SpiritScore = tonumber(data.spiritScore) or 0
    state.HouseRating = calculateHouseRating(state.SpiritScore)
    state.UnlockedTier = math.max(tonumber(data.inventoryTier) or 1, determineTier(state.SpiritScore))
    state.SessionAwardSteps = math.floor(state.SpiritScore / GameConfig.SessionAwardSpiritStep)

    restoreParts(data.buildParts, state.BuildParts)
    state.NextPartId = #state.BuildParts:GetChildren()
    updateLeaderboard()
end

local function removePlot(player)
    savePlayerBuild(player)

    local state = playerState[player]
    if state and state.Plot then
        state.Plot:Destroy()
    end
    playerState[player] = nil
    updateLeaderboard()
end

local function spawnPlacedPart(state, catalogInfo, snappedPos, snappedSize, placementType, levelIndex, rotationY, filteredText)
    state.NextPartId += 1
    local partData = {
        name = string.format("%s_%d_%d", placementType, levelIndex, state.NextPartId),
        position = { snappedPos.X, snappedPos.Y, snappedPos.Z },
        size = { snappedSize.X, snappedSize.Y, snappedSize.Z },
        color = { catalogInfo.Color.R, catalogInfo.Color.G, catalogInfo.Color.B },
        material = catalogInfo.Material.Name,
        orientation = { 0, rotationY, 0 },
        text = filteredText,
    }

    return createPartFromData(partData, state.BuildParts)
end

BuildStateRequest.OnServerInvoke = function(player)
    local state = playerState[player]
    if not state then
        return nil
    end

    return {
        tokens = state.Tokens,
        theme = GameConfig.Theme,
        materialCatalog = GameConfig.MaterialCatalog,
        propCatalog = GameConfig.PropCatalog,
        levels = GameConfig.Levels,
        spiritScore = state.SpiritScore,
        houseRating = state.HouseRating,
        inventoryTier = state.UnlockedTier,
        maxParts = GameConfig.MaxPlacedParts,
    }
end

BuildActionRequest.OnServerEvent:Connect(function(player, action)
    local state = playerState[player]
    if not state or type(action) ~= "string" then
        return
    end

    if action == "Undo" then
        local item = table.remove(state.UndoStack)
        if not item then
            return
        end

        local latest = state.BuildParts:FindFirstChild(item.partName)
        if latest then
            latest:Destroy()
        end
        updateSpirit(state, -(item.spiritDelta or 0))
        state.Tokens += item.costPaid or 0
        table.insert(state.RedoStack, item)
    elseif action == "Redo" then
        local item = table.remove(state.RedoStack)
        if not item then
            return
        end

        if state.Tokens < (item.costPaid or 0) then
            return
        end

        state.Tokens -= item.costPaid or 0
        local created = createPartFromData(item.partData, state.BuildParts)
        item.partName = created.Name
        updateSpirit(state, item.spiritDelta or 0)
        table.insert(state.UndoStack, item)
    end
end)

PlaceRequest.OnServerEvent:Connect(function(player, payload)
    local state = playerState[player]
    if not state then
        return
    end

    if type(payload) ~= "table" then
        return
    end

    if #state.BuildParts:GetChildren() >= GameConfig.MaxPlacedParts then
        BuildFeedbackEvent:FireClient(player, "Part limit reached for better performance")
        return
    end

    local materialKey = payload.material
    local propKey = payload.prop
    local position = payload.position
    local size = payload.size
    local placementType = payload.placementType or "Structure"
    local rotationY = snap(tonumber(payload.rotationY) or 0)

    if typeof(position) ~= "Vector3" then
        return
    end

    local catalogInfo = nil
    if placementType == "Prop" then
        catalogInfo = GameConfig.PropCatalog[propKey]
        if catalogInfo then
            size = catalogInfo.Size
        end
    else
        if typeof(size) ~= "Vector3" then
            return
        end
        catalogInfo = GameConfig.MaterialCatalog[materialKey]
    end

    if not catalogInfo then
        return
    end

    if (catalogInfo.Tier or 1) > state.UnlockedTier then
        BuildFeedbackEvent:FireClient(player, "Item tier locked: earn more spirit to unlock")
        return
    end

    local snappedPos = Vector3.new(snap(position.X), snap(position.Y), snap(position.Z))
    local snappedSize = Vector3.new(math.max(4, snap(size.X)), math.max(4, snap(size.Y)), math.max(4, snap(size.Z)))

    if not isInsidePlot(state.Baseplate, snappedPos, snappedSize) then
        BuildFeedbackEvent:FireClient(player, "Placement outside your plot is blocked")
        return
    end

    local insideLevel, levelIndex = withinAnyLevel(snappedPos.Y)
    if not insideLevel then
        return
    end

    if intersectsExisting(state, snappedPos, snappedSize) then
        BuildFeedbackEvent:FireClient(player, "Cannot overlap another placed object")
        return
    end

    local cost = catalogInfo.Cost or 0
    if state.Tokens < cost then
        return
    end

    local filteredText
    if catalogInfo.SupportsText and type(payload.text) == "string" and payload.text ~= "" then
        local success, result = pcall(function()
            local filterResult = TextService:FilterStringAsync(payload.text, player.UserId)
            return filterResult:GetNonChatStringForBroadcastAsync()
        end)

        if success and result then
            filteredText = string.sub(result, 1, 40)
        else
            filteredText = "[Filtered]"
        end
    end

    state.Tokens -= cost

    local part = spawnPlacedPart(state, catalogInfo, snappedPos, snappedSize, placementType, levelIndex, rotationY, filteredText)
    updateSpirit(state, catalogInfo.Spirit or 1)

    local partData = serializePart(part)
    pushUndo(state, {
        partName = part.Name,
        partData = partData,
        costPaid = cost,
        spiritDelta = catalogInfo.Spirit or 1,
    })
end)

Players.PlayerAdded:Connect(function(player)
    local leaderstats = Instance.new("Folder")
    leaderstats.Name = "leaderstats"
    leaderstats.Parent = player

    local spirit = Instance.new("IntValue")
    spirit.Name = "Spirit"
    spirit.Parent = leaderstats

    local rating = Instance.new("IntValue")
    rating.Name = "HouseRating"
    rating.Parent = leaderstats

    createPlotForPlayer(player)
    loadPlayerBuild(player)

    local state = playerState[player]
    if state then
        spirit.Value = state.SpiritScore
        rating.Value = state.HouseRating

        task.spawn(function()
            while player.Parent and playerState[player] do
                spirit.Value = playerState[player].SpiritScore
                rating.Value = playerState[player].HouseRating
                task.wait(1)
            end
        end)
    end
end)

Players.PlayerRemoving:Connect(removePlot)

game:BindToClose(function()
    for _, player in ipairs(Players:GetPlayers()) do
        savePlayerBuild(player)
    end
end)

for _, player in ipairs(Players:GetPlayers()) do
    createPlotForPlayer(player)
    loadPlayerBuild(player)
end
