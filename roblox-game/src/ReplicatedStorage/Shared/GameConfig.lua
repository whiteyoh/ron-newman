local GameConfig = {}

GameConfig.Theme = "UK High School"
GameConfig.DataVersion = 2

GameConfig.Levels = {
    { Name = "Ground Floor", MinY = 0, MaxY = 15, StudColor = Color3.fromRGB(70, 82, 99) },
    { Name = "First Floor", MinY = 16, MaxY = 31, StudColor = Color3.fromRGB(76, 99, 120) },
    { Name = "Second Floor", MinY = 32, MaxY = 47, StudColor = Color3.fromRGB(102, 127, 159) },
    { Name = "Third Floor", MinY = 48, MaxY = 63, StudColor = Color3.fromRGB(118, 145, 178) },
    { Name = "Rooftop", MinY = 64, MaxY = 79, StudColor = Color3.fromRGB(166, 188, 219) },
}

GameConfig.GridSize = 4
GameConfig.PlotSize = Vector3.new(100, 80, 100)
GameConfig.MaxPlacedParts = 300
GameConfig.MaxUndoHistory = 30
GameConfig.SessionAwardSpiritStep = 25

GameConfig.MaterialCatalog = {
    Brick = { Material = Enum.Material.Brick, Color = Color3.fromRGB(151, 108, 74), Cost = 0, Spirit = 1, Tier = 1 },
    Plaster = { Material = Enum.Material.SmoothPlastic, Color = Color3.fromRGB(226, 231, 236), Cost = 0, Spirit = 1, Tier = 1 },
    ClassroomTile = { Material = Enum.Material.Slate, Color = Color3.fromRGB(86, 97, 112), Cost = 0, Spirit = 2, Tier = 1 },
    PremiumGlass = { Material = Enum.Material.Glass, Color = Color3.fromRGB(197, 232, 255), Cost = 5, Spirit = 3, Tier = 2 },
    NeonTrim = { Material = Enum.Material.Neon, Color = Color3.fromRGB(255, 229, 120), Cost = 10, Spirit = 4, Tier = 3 },
}

GameConfig.PropCatalog = {
    StudentDesk = { Material = Enum.Material.Wood, Color = Color3.fromRGB(140, 96, 60), Size = Vector3.new(8, 4, 4), Cost = 2, Spirit = 3, Tier = 1 },
    Blackboard = { Material = Enum.Material.Slate, Color = Color3.fromRGB(26, 51, 33), Size = Vector3.new(12, 8, 1), Cost = 3, Spirit = 4, Tier = 1 },
    TrophyCase = { Material = Enum.Material.Metal, Color = Color3.fromRGB(214, 177, 73), Size = Vector3.new(4, 8, 4), Cost = 5, Spirit = 6, Tier = 2 },
    PrefectBoard = { Material = Enum.Material.SmoothPlastic, Color = Color3.fromRGB(49, 63, 95), Size = Vector3.new(8, 8, 1), Cost = 3, Spirit = 5, Tier = 2 },
    SpiritSign = { Material = Enum.Material.WoodPlanks, Color = Color3.fromRGB(131, 97, 74), Size = Vector3.new(8, 6, 1), Cost = 4, Spirit = 5, Tier = 2, SupportsText = true },
}

GameConfig.MaterialTiers = {
    [1] = { RequiredSpirit = 0, Name = "Foundation" },
    [2] = { RequiredSpirit = 25, Name = "Decorative" },
    [3] = { RequiredSpirit = 60, Name = "Elite" },
}

GameConfig.RoleplayNPCs = {
    {
        Name = "TeacherNPC",
        Title = "Teacher",
        Dialogue = "Keep your classroom tidy and your spirit score high.",
        Quest = "Place 3 structures on this level.",
        PositionOffset = Vector3.new(-16, 3, -16),
        Color = Color3.fromRGB(209, 176, 147),
    },
    {
        Name = "PrefectNPC",
        Title = "Prefect",
        Dialogue = "Top house rating gets the honor board spotlight!",
        Quest = "Reach House Rating 3 to earn bonus tokens.",
        PositionOffset = Vector3.new(0, 3, -16),
        Color = Color3.fromRGB(123, 160, 207),
    },
    {
        Name = "CaretakerNPC",
        Title = "Caretaker",
        Dialogue = "No running in the corridors. Decorate responsibly!",
        Quest = "Keep your part count below the performance cap.",
        PositionOffset = Vector3.new(16, 3, -16),
        Color = Color3.fromRGB(117, 137, 111),
    },
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
