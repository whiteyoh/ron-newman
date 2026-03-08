local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local player = Players.LocalPlayer
local Remotes = ReplicatedStorage:WaitForChild("Remotes")

local PlaceRequest = Remotes:WaitForChild("PlaceRequest")
local BuildStateRequest = Remotes:WaitForChild("BuildStateRequest")
local MonetizationStateRequest = Remotes:WaitForChild("MonetizationStateRequest")
local PurchaseRequest = Remotes:WaitForChild("PurchaseRequest")
local BuildActionRequest = Remotes:WaitForChild("BuildActionRequest")
local NpcDialogueEvent = Remotes:WaitForChild("NpcDialogueEvent")
local BuildFeedbackEvent = Remotes:WaitForChild("BuildFeedbackEvent")
local DeleteRequest = Remotes:WaitForChild("DeleteRequest")
local VisitPlotRequest = Remotes:WaitForChild("VisitPlotRequest")

local selectedMaterial = "Brick"
local selectedProp = "StudentDesk"
local selectedLevel = 1
local placementType = "Structure"
local ghostSize = Vector3.new(8, 8, 8)
local rotationY = 0

local ghostPart
local selectedPlacedPart
local highlightBox
local visitIndex = 1
local refreshHUD

local function getGuiPanel()
    local gui = player:WaitForChild("PlayerGui"):FindFirstChild("BuildHUD")
    if not gui then
        return nil, nil
    end
    return gui:FindFirstChild("Panel"), gui:FindFirstChild("DialoguePanel")
end

local function getMouseWorldPosition()
    local mouse = player:GetMouse()
    if mouse and mouse.Hit then
        return mouse.Hit.Position
    end
    return Vector3.new(0, 4, 0)
end

local function updateGhostPart()
    local worldPos = getMouseWorldPosition()
    local y = (selectedLevel - 1) * 16 + 4
    local size = placementType == "Prop" and ghostSize or ghostSize

    if not ghostPart then
        ghostPart = Instance.new("Part")
        ghostPart.Name = "BuildGhost"
        ghostPart.Anchored = true
        ghostPart.CanCollide = false
        ghostPart.Transparency = 0.5
        ghostPart.Material = Enum.Material.ForceField
        ghostPart.Color = Color3.fromRGB(85, 170, 255)
        ghostPart.Parent = workspace
    end

    ghostPart.Size = size
    ghostPart.Position = Vector3.new(worldPos.X, y, worldPos.Z)
    ghostPart.Orientation = Vector3.new(0, rotationY, 0)
end


local function getOwnBuildFolder()
    local plots = workspace:FindFirstChild("PlayerPlots")
    if not plots then
        return nil
    end

    local plot = plots:FindFirstChild(player.Name .. "_Plot")
    if not plot then
        return nil
    end

    return plot:FindFirstChild("BuildParts")
end

local function updateSelectionVisual()
    if selectedPlacedPart and selectedPlacedPart.Parent then
        if not highlightBox then
            highlightBox = Instance.new("SelectionBox")
            highlightBox.Name = "SelectedBuildPart"
            highlightBox.LineThickness = 0.05
            highlightBox.Color3 = Color3.fromRGB(255, 210, 90)
            highlightBox.SurfaceColor3 = Color3.fromRGB(255, 210, 90)
            highlightBox.SurfaceTransparency = 0.75
            highlightBox.Parent = workspace
        end
        highlightBox.Adornee = selectedPlacedPart
    elseif highlightBox then
        highlightBox.Adornee = nil
    end
end

local function selectPartUnderCursor()
    local target = player:GetMouse().Target
    local ownBuildFolder = getOwnBuildFolder()
    if target and ownBuildFolder and target.Parent == ownBuildFolder then
        selectedPlacedPart = target
        refreshHUD("Selected: " .. target.Name)
    else
        selectedPlacedPart = nil
        refreshHUD("Selection cleared (target your own placed part)")
    end
    updateSelectionVisual()
end

local function deleteSelectedPart()
    if selectedPlacedPart and selectedPlacedPart.Parent then
        DeleteRequest:FireServer(selectedPlacedPart.Name)
    else
        refreshHUD("No selected part to delete")
    end
end

local function cycleVisit(direction)
    local buildState = BuildStateRequest:InvokeServer()
    if not buildState or type(buildState.players) ~= "table" or #buildState.players == 0 then
        refreshHUD("No active plots to visit")
        return
    end

    visitIndex = ((visitIndex - 1 + direction) % #buildState.players) + 1
    local target = buildState.players[visitIndex]
    if not target then
        return
    end

    VisitPlotRequest:FireServer(target.userId)
    refreshHUD("Visiting: " .. tostring(target.name))
end

refreshHUD = function(feedbackMessage)
    local buildState = BuildStateRequest:InvokeServer()
    local monetizationState = MonetizationStateRequest:InvokeServer()

    local panel = getGuiPanel()
    if panel and buildState and monetizationState then
        panel.ThemeLabel.Text = "Theme: " .. tostring(buildState.theme)
        panel.TokensLabel.Text = string.format("Tokens: %s (+%s)", tostring(buildState.tokens), tostring(monetizationState.tokenBoost))
        panel.LevelLabel.Text = "Current Level: " .. tostring(buildState.levels[selectedLevel].Name)
        panel.MaterialLabel.Text = "Structure: " .. selectedMaterial
        panel.PropLabel.Text = "Prop: " .. selectedProp
        panel.ModeLabel.Text = "Placement Mode: " .. placementType
        panel.SpiritLabel.Text = string.format("School Spirit: %d | House Rating: %d/5", buildState.spiritScore, buildState.houseRating)
        panel.TierLabel.Text = string.format("Inventory Tier: %d | Max Parts: %d", buildState.inventoryTier or 1, buildState.maxParts or 0)
        panel.GhostLabel.Text = string.format("Ghost Size: %dx%dx%d | Rotation: %d", ghostSize.X, ghostSize.Y, ghostSize.Z, rotationY)
        local selectionName = selectedPlacedPart and selectedPlacedPart.Parent and selectedPlacedPart.Name or "None"
        panel.SelectionLabel.Text = "Selected Part: " .. selectionName

        if feedbackMessage then
            panel.FeedbackLabel.Text = feedbackMessage
        end
    end
end

local function placeCurrentPart()
    local worldPos = getMouseWorldPosition()
    local panel = getGuiPanel()

    local payload = {
        placementType = placementType,
        position = Vector3.new(worldPos.X, (selectedLevel - 1) * 16 + 4, worldPos.Z),
        rotationY = rotationY,
    }

    if placementType == "Prop" then
        payload.prop = selectedProp
        if selectedProp == "SpiritSign" and panel and panel.SignInput then
            payload.text = panel.SignInput.Text
        end
    else
        payload.material = selectedMaterial
        payload.size = ghostSize
    end

    PlaceRequest:FireServer(payload)

    refreshHUD()
end

BuildFeedbackEvent.OnClientEvent:Connect(function(message)
    refreshHUD(message)
    if selectedPlacedPart and not selectedPlacedPart.Parent then
        selectedPlacedPart = nil
    end
    updateSelectionVisual()
end)

NpcDialogueEvent.OnClientEvent:Connect(function(payload)
    local _, dialoguePanel = getGuiPanel()
    if not dialoguePanel or type(payload) ~= "table" then
        return
    end

    dialoguePanel.Visible = true
    dialoguePanel.NpcTitle.Text = tostring(payload.title or "NPC")
    dialoguePanel.NpcDialogue.Text = tostring(payload.dialogue or "...")
    dialoguePanel.NpcObjective.Text = "Objective: " .. tostring(payload.objective or "No objective")

    task.delay(8, function()
        if dialoguePanel.Parent then
            dialoguePanel.Visible = false
        end
    end)
end)

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
        placementType = "Structure"
        refreshHUD()
    elseif input.KeyCode == Enum.KeyCode.Two then
        selectedMaterial = "Plaster"
        placementType = "Structure"
        refreshHUD()
    elseif input.KeyCode == Enum.KeyCode.Three then
        selectedMaterial = "ClassroomTile"
        placementType = "Structure"
        refreshHUD()
    elseif input.KeyCode == Enum.KeyCode.Four then
        selectedProp = "StudentDesk"
        placementType = "Prop"
        ghostSize = Vector3.new(8, 4, 4)
        refreshHUD()
    elseif input.KeyCode == Enum.KeyCode.Five then
        selectedProp = "Blackboard"
        placementType = "Prop"
        ghostSize = Vector3.new(12, 8, 4)
        refreshHUD()
    elseif input.KeyCode == Enum.KeyCode.Six then
        selectedProp = "TrophyCase"
        placementType = "Prop"
        ghostSize = Vector3.new(4, 8, 4)
        refreshHUD()
    elseif input.KeyCode == Enum.KeyCode.Seven then
        selectedProp = "SpiritSign"
        placementType = "Prop"
        ghostSize = Vector3.new(8, 6, 4)
        refreshHUD()
    elseif input.KeyCode == Enum.KeyCode.Z and placementType == "Structure" then
        ghostSize += Vector3.new(4, 0, 4)
        refreshHUD()
    elseif input.KeyCode == Enum.KeyCode.X and placementType == "Structure" then
        ghostSize = Vector3.new(math.max(4, ghostSize.X - 4), ghostSize.Y, math.max(4, ghostSize.Z - 4))
        refreshHUD()
    elseif input.KeyCode == Enum.KeyCode.C then
        rotationY = (rotationY + 90) % 360
        refreshHUD()
    elseif input.KeyCode == Enum.KeyCode.U then
        BuildActionRequest:FireServer("Undo")
        refreshHUD()
    elseif input.KeyCode == Enum.KeyCode.Y then
        BuildActionRequest:FireServer("Redo")
        refreshHUD()
    elseif input.KeyCode == Enum.KeyCode.F then
        placeCurrentPart()
    elseif input.KeyCode == Enum.KeyCode.R then
        PurchaseRequest:FireServer("DeveloperProduct", "BuildTokensSmall")
    elseif input.KeyCode == Enum.KeyCode.T then
        PurchaseRequest:FireServer("Gamepass", "PremiumBuilder")
    elseif input.KeyCode == Enum.KeyCode.G then
        selectPartUnderCursor()
    elseif input.KeyCode == Enum.KeyCode.Backspace then
        deleteSelectedPart()
    elseif input.KeyCode == Enum.KeyCode.J then
        cycleVisit(-1)
    elseif input.KeyCode == Enum.KeyCode.K then
        cycleVisit(1)
    end
end)

RunService.RenderStepped:Connect(function()
    updateGhostPart()
    if selectedPlacedPart and not selectedPlacedPart.Parent then
        selectedPlacedPart = nil
    end
    updateSelectionVisual()
end)

task.wait(1)
refreshHUD()
