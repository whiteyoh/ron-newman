local GameConfig = {}

GameConfig.Theme = "UK High School"

GameConfig.Levels = {
    { Name = "Ground Floor", MinY = 0, MaxY = 15, StudColor = Color3.fromRGB(70, 82, 99) },
    { Name = "First Floor", MinY = 16, MaxY = 31, StudColor = Color3.fromRGB(76, 99, 120) },
    { Name = "Second Floor", MinY = 32, MaxY = 47, StudColor = Color3.fromRGB(102, 127, 159) },
    { Name = "Third Floor", MinY = 48, MaxY = 63, StudColor = Color3.fromRGB(118, 145, 178) },
    { Name = "Rooftop", MinY = 64, MaxY = 79, StudColor = Color3.fromRGB(166, 188, 219) },
}

GameConfig.GridSize = 4
GameConfig.PlotSize = Vector3.new(100, 80, 100)

GameConfig.MaterialCatalog = {
    Brick = { Material = Enum.Material.Brick, Color = Color3.fromRGB(151, 108, 74), Cost = 0 },
    Plaster = { Material = Enum.Material.SmoothPlastic, Color = Color3.fromRGB(226, 231, 236), Cost = 0 },
    ClassroomTile = { Material = Enum.Material.Slate, Color = Color3.fromRGB(86, 97, 112), Cost = 0 },
    PremiumGlass = { Material = Enum.Material.Glass, Color = Color3.fromRGB(197, 232, 255), Cost = 5 },
    NeonTrim = { Material = Enum.Material.Neon, Color = Color3.fromRGB(255, 229, 120), Cost = 10 },
}

GameConfig.DeveloperProducts = {
    BuildTokensSmall = 0, -- Replace with your developer product id
    BuildTokensLarge = 0, -- Replace with your developer product id
}

GameConfig.Gamepasses = {
    PremiumBuilder = 0, -- Replace with your gamepass id
}

GameConfig.ProductRewards = {
    BuildTokensSmall = 100,
    BuildTokensLarge = 300,
}

GameConfig.PremiumBuilderMultiplier = 2

return GameConfig
