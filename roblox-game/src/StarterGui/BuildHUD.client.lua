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
panel.Size = UDim2.new(0, 430, 0, 260)
panel.Position = UDim2.new(0, 16, 1, -276)
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
createLabel("ControlsLabel", 7, "Q/E level | 1-3 structures | 4-6 props | F place")
createLabel("StoreLabel", 8, "R buy Tokens (Robux) | T Premium Pass")
