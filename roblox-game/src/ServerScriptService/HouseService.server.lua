local DataStoreService = game:GetService("DataStoreService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local GameConfig = require(Shared:WaitForChild("GameConfig"))

local BUILD_DATASTORE = DataStoreService:GetDataStore("PlayerBuilds_v1")

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

local plotsFolder = workspace:FindFirstChild("PlayerPlots")
if not plotsFolder then
    plotsFolder = Instance.new("Folder")
    plotsFolder.Name = "PlayerPlots"
    plotsFolder.Parent = workspace
end

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
            print(string.format("[RoleplayNPC] %s -> %s: %s", player.Name, npc.Title, npc.Dialogue))
        end)
    end
end

local function updateSpirit(state, delta)
    state.SpiritScore = math.max(0, state.SpiritScore + delta)
    state.HouseRating = calculateHouseRating(state.SpiritScore)
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
        Plot = plot,
        Baseplate = baseplate,
        BuildParts = builds,
        Tokens = 50,
        SpiritScore = 0,
        HouseRating = 1,
    }

    spawnRoleplayNPC(plot, baseplate.Position)
end

local function restoreParts(parts, parent)
    for _, partData in ipairs(parts or {}) do
        local part = Instance.new("Part")
        part.Name = partData.name or "Build_Restore"
        part.Position = Vector3.new(partData.position[1], partData.position[2], partData.position[3])
        part.Size = Vector3.new(partData.size[1], partData.size[2], partData.size[3])
        part.Color = Color3.new(partData.color[1], partData.color[2], partData.color[3])
        part.Material = materialFromName(partData.material)
        part.Anchored = true
        part.TopSurface = Enum.SurfaceType.Smooth
        part.BottomSurface = Enum.SurfaceType.Smooth
        part.Parent = parent
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
        tokens = state.Tokens,
        spiritScore = state.SpiritScore,
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

    if not success or type(data) ~= "table" then
        return
    end

    state.Tokens = tonumber(data.tokens) or state.Tokens
    state.SpiritScore = tonumber(data.spiritScore) or 0
    state.HouseRating = calculateHouseRating(state.SpiritScore)
    restoreParts(data.buildParts, state.BuildParts)
end

local function removePlot(player)
    savePlayerBuild(player)

    local state = playerState[player]
    if state and state.Plot then
        state.Plot:Destroy()
    end
    playerState[player] = nil
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
    }
end

PlaceRequest.OnServerEvent:Connect(function(player, payload)
    local state = playerState[player]
    if not state then
        return
    end

    if type(payload) ~= "table" then
        return
    end

    local materialKey = payload.material
    local propKey = payload.prop
    local position = payload.position
    local size = payload.size
    local placementType = payload.placementType or "Structure"

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

    local snappedPos = Vector3.new(snap(position.X), snap(position.Y), snap(position.Z))
    local snappedSize = Vector3.new(math.max(4, snap(size.X)), math.max(4, snap(size.Y)), math.max(4, snap(size.Z)))

    local insideLevel, levelIndex = withinAnyLevel(snappedPos.Y)
    if not insideLevel then
        return
    end

    local cost = catalogInfo.Cost or 0
    if state.Tokens < cost then
        return
    end

    state.Tokens -= cost

    local part = Instance.new("Part")
    part.Name = string.format("%s_%d", placementType, levelIndex)
    part.Size = snappedSize
    part.Position = snappedPos
    part.Material = catalogInfo.Material
    part.Color = catalogInfo.Color
    part.Anchored = true
    part.TopSurface = Enum.SurfaceType.Smooth
    part.BottomSurface = Enum.SurfaceType.Smooth
    part.Parent = state.BuildParts

    updateSpirit(state, catalogInfo.Spirit or 1)
end)

Players.PlayerAdded:Connect(function(player)
    createPlotForPlayer(player)
    loadPlayerBuild(player)
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
