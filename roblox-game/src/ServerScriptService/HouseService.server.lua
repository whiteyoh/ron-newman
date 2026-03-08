local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local GameConfig = require(Shared:WaitForChild("GameConfig"))

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
        BuildParts = builds,
        Tokens = 50,
    }
end

local function removePlot(player)
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
        levels = GameConfig.Levels,
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
    local position = payload.position
    local size = payload.size

    if typeof(position) ~= "Vector3" or typeof(size) ~= "Vector3" then
        return
    end

    local materialInfo = GameConfig.MaterialCatalog[materialKey]
    if not materialInfo then
        return
    end

    local snappedPos = Vector3.new(snap(position.X), snap(position.Y), snap(position.Z))
    local snappedSize = Vector3.new(math.max(4, snap(size.X)), math.max(4, snap(size.Y)), math.max(4, snap(size.Z)))

    local insideLevel, levelIndex = withinAnyLevel(snappedPos.Y)
    if not insideLevel then
        return
    end

    local cost = materialInfo.Cost
    if state.Tokens < cost then
        return
    end

    state.Tokens -= cost

    local part = Instance.new("Part")
    part.Name = string.format("Build_%d", levelIndex)
    part.Size = snappedSize
    part.Position = snappedPos
    part.Material = materialInfo.Material
    part.Color = materialInfo.Color
    part.Anchored = true
    part.TopSurface = Enum.SurfaceType.Smooth
    part.BottomSurface = Enum.SurfaceType.Smooth
    part.Parent = state.BuildParts
end)

Players.PlayerAdded:Connect(createPlotForPlayer)
Players.PlayerRemoving:Connect(removePlot)

for _, player in ipairs(Players:GetPlayers()) do
    createPlotForPlayer(player)
end
