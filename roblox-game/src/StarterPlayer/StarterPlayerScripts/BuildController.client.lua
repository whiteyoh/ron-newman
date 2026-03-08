local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local player = Players.LocalPlayer
local Remotes = ReplicatedStorage:WaitForChild("Remotes")

local PlaceRequest = Remotes:WaitForChild("PlaceRequest")
local BuildStateRequest = Remotes:WaitForChild("BuildStateRequest")
local MonetizationStateRequest = Remotes:WaitForChild("MonetizationStateRequest")
local PurchaseRequest = Remotes:WaitForChild("PurchaseRequest")

local selectedMaterial = "Brick"
local selectedLevel = 1
local ghostSize = Vector3.new(8, 8, 8)

local function getMouseWorldPosition()
    local mouse = player:GetMouse()
    if mouse and mouse.Hit then
        return mouse.Hit.Position
    end
    return Vector3.new(0, 4, 0)
end

local function refreshHUD()
    local buildState = BuildStateRequest:InvokeServer()
    local monetizationState = MonetizationStateRequest:InvokeServer()

    local gui = player:WaitForChild("PlayerGui"):FindFirstChild("BuildHUD")
    if gui then
        local panel = gui:FindFirstChild("Panel")
        if panel then
            panel.ThemeLabel.Text = "Theme: " .. tostring(buildState.theme)
            panel.TokensLabel.Text = string.format("Tokens: %s (+%s)", tostring(buildState.tokens), tostring(monetizationState.tokenBoost))
            panel.LevelLabel.Text = "Current Level: " .. tostring(buildState.levels[selectedLevel].Name)
            panel.MaterialLabel.Text = "Material: " .. selectedMaterial
        end
    end
end

local function placeCurrentPart()
    local worldPos = getMouseWorldPosition()

    PlaceRequest:FireServer({
        material = selectedMaterial,
        position = Vector3.new(worldPos.X, (selectedLevel - 1) * 16 + 4, worldPos.Z),
        size = ghostSize,
    })

    refreshHUD()
end

UserInputService.InputBegan:Connect(function(input, processed)
    if processed then
        return
    end

    if input.KeyCode == Enum.KeyCode.E then
        selectedLevel = math.clamp(selectedLevel + 1, 1, 5)
        refreshHUD()
    elseif input.KeyCode == Enum.KeyCode.Q then
        selectedLevel = math.clamp(selectedLevel - 1, 1, 5)
        refreshHUD()
    elseif input.KeyCode == Enum.KeyCode.One then
        selectedMaterial = "Brick"
        refreshHUD()
    elseif input.KeyCode == Enum.KeyCode.Two then
        selectedMaterial = "Plaster"
        refreshHUD()
    elseif input.KeyCode == Enum.KeyCode.Three then
        selectedMaterial = "ClassroomTile"
        refreshHUD()
    elseif input.KeyCode == Enum.KeyCode.F then
        placeCurrentPart()
    elseif input.KeyCode == Enum.KeyCode.R then
        PurchaseRequest:FireServer("DeveloperProduct", "BuildTokensSmall")
    elseif input.KeyCode == Enum.KeyCode.T then
        PurchaseRequest:FireServer("Gamepass", "PremiumBuilder")
    end
end)

task.wait(1)
refreshHUD()
