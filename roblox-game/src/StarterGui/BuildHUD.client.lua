local Players = game:GetService("Players")

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

local existing = playerGui:FindFirstChild("BuildHUD")
if existing then
    existing:Destroy()
end

local screenGui = Instance.new("ScreenGui")
screenGui.Name = "BuildHUD"
screenGui.ResetOnSpawn = false
screenGui.Parent = playerGui

local panel = Instance.new("Frame")
panel.Name = "Panel"
panel.Size = UDim2.new(0, 500, 0, 390)
panel.Position = UDim2.new(0, 16, 1, -406)
panel.BackgroundColor3 = Color3.fromRGB(36, 44, 62)
panel.BackgroundTransparency = 0.1
panel.Parent = screenGui

local uiCorner = Instance.new("UICorner")
uiCorner.CornerRadius = UDim.new(0, 10)
uiCorner.Parent = panel

local function createLabel(name, order, text)
    local label = Instance.new("TextLabel")
    label.Name = name
    label.Size = UDim2.new(1, -20, 0, 24)
    label.Position = UDim2.new(0, 10, 0, 8 + (order * 25))
    label.BackgroundTransparency = 1
    label.TextXAlignment = Enum.TextXAlignment.Left
    label.TextColor3 = Color3.fromRGB(231, 238, 252)
    label.Font = Enum.Font.GothamSemibold
    label.TextSize = 16
    label.Text = text
    label.Parent = panel
    return label
end

createLabel("ThemeLabel", 0, "Theme: UK High School")
createLabel("TokensLabel", 1, "Tokens: 0")
createLabel("LevelLabel", 2, "Current Level: Ground Floor")
createLabel("MaterialLabel", 3, "Structure: Brick")
createLabel("PropLabel", 4, "Prop: StudentDesk")
createLabel("ModeLabel", 5, "Placement Mode: Structure")
createLabel("SpiritLabel", 6, "School Spirit: 0 | House Rating: 1/5")
createLabel("TierLabel", 7, "Inventory Tier: 1")
createLabel("GhostLabel", 8, "Ghost Size: 8x8x8 | Rotation: 0")
createLabel("SelectionLabel", 9, "Selected Part: None")
createLabel("ControlsLabel", 10, "Q/E level | 1-3 structures | 4-7 props | F place")
createLabel("BuildToolsLabel", 11, "Z/X resize | C rotate | U undo | Y redo")
createLabel("EditToolsLabel", 12, "G select part | Backspace delete | J/K visit plots")
createLabel("StoreLabel", 13, "R buy Tokens (Robux) | T Premium Pass")

local signInput = Instance.new("TextBox")
signInput.Name = "SignInput"
signInput.Size = UDim2.new(1, -20, 0, 28)
signInput.Position = UDim2.new(0, 10, 0, 8 + (14 * 25))
signInput.BackgroundColor3 = Color3.fromRGB(23, 29, 42)
signInput.TextColor3 = Color3.fromRGB(231, 238, 252)
signInput.PlaceholderText = "Sign text (used for SpiritSign prop, filtered on server)"
signInput.Text = ""
signInput.ClearTextOnFocus = false
signInput.Font = Enum.Font.Gotham
signInput.TextSize = 14
signInput.Parent = panel

local feedbackLabel = Instance.new("TextLabel")
feedbackLabel.Name = "FeedbackLabel"
feedbackLabel.Size = UDim2.new(1, -20, 0, 24)
feedbackLabel.Position = UDim2.new(0, 10, 0, 8 + (15 * 25))
feedbackLabel.BackgroundTransparency = 1
feedbackLabel.TextXAlignment = Enum.TextXAlignment.Left
feedbackLabel.TextColor3 = Color3.fromRGB(255, 215, 114)
feedbackLabel.Font = Enum.Font.GothamSemibold
feedbackLabel.TextSize = 14
feedbackLabel.Text = ""
feedbackLabel.Parent = panel

local dialoguePanel = Instance.new("Frame")
dialoguePanel.Name = "DialoguePanel"
dialoguePanel.Size = UDim2.new(0, 420, 0, 120)
dialoguePanel.Position = UDim2.new(1, -436, 1, -136)
dialoguePanel.BackgroundColor3 = Color3.fromRGB(22, 26, 34)
dialoguePanel.Visible = false
dialoguePanel.Parent = screenGui

local dialogueCorner = Instance.new("UICorner")
dialogueCorner.CornerRadius = UDim.new(0, 10)
dialogueCorner.Parent = dialoguePanel

local npcTitle = Instance.new("TextLabel")
npcTitle.Name = "NpcTitle"
npcTitle.Size = UDim2.new(1, -16, 0, 24)
npcTitle.Position = UDim2.new(0, 8, 0, 8)
npcTitle.BackgroundTransparency = 1
npcTitle.TextXAlignment = Enum.TextXAlignment.Left
npcTitle.TextColor3 = Color3.fromRGB(146, 196, 255)
npcTitle.Font = Enum.Font.GothamBold
npcTitle.TextSize = 18
npcTitle.Parent = dialoguePanel

local npcDialogue = Instance.new("TextLabel")
npcDialogue.Name = "NpcDialogue"
npcDialogue.Size = UDim2.new(1, -16, 0, 40)
npcDialogue.Position = UDim2.new(0, 8, 0, 34)
npcDialogue.BackgroundTransparency = 1
npcDialogue.TextWrapped = true
npcDialogue.TextXAlignment = Enum.TextXAlignment.Left
npcDialogue.TextYAlignment = Enum.TextYAlignment.Top
npcDialogue.TextColor3 = Color3.fromRGB(235, 240, 255)
npcDialogue.Font = Enum.Font.Gotham
npcDialogue.TextSize = 14
npcDialogue.Parent = dialoguePanel

local npcObjective = Instance.new("TextLabel")
npcObjective.Name = "NpcObjective"
npcObjective.Size = UDim2.new(1, -16, 0, 36)
npcObjective.Position = UDim2.new(0, 8, 0, 78)
npcObjective.BackgroundTransparency = 1
npcObjective.TextWrapped = true
npcObjective.TextXAlignment = Enum.TextXAlignment.Left
npcObjective.TextYAlignment = Enum.TextYAlignment.Top
npcObjective.TextColor3 = Color3.fromRGB(180, 231, 180)
npcObjective.Font = Enum.Font.GothamSemibold
npcObjective.TextSize = 13
npcObjective.Parent = dialoguePanel
