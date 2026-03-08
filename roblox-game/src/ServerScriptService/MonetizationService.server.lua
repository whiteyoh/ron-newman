local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local GameConfig = require(Shared:WaitForChild("GameConfig"))

local Remotes = ReplicatedStorage:WaitForChild("Remotes")

local PurchaseRequest = Remotes:FindFirstChild("PurchaseRequest") or Instance.new("RemoteEvent")
PurchaseRequest.Name = "PurchaseRequest"
PurchaseRequest.Parent = Remotes

local MonetizationStateRequest = Remotes:FindFirstChild("MonetizationStateRequest") or Instance.new("RemoteFunction")
MonetizationStateRequest.Name = "MonetizationStateRequest"
MonetizationStateRequest.Parent = Remotes

local playerTokenBoosts = {}

local function resolveProductNameById(productId)
    for productName, configuredId in pairs(GameConfig.DeveloperProducts) do
        if configuredId == productId and configuredId ~= 0 then
            return productName
        end
    end
    return nil
end

local function grantProduct(player, productName)
    local reward = GameConfig.ProductRewards[productName]
    if not reward then
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    playerTokenBoosts[player] = (playerTokenBoosts[player] or 0) + reward
    return Enum.ProductPurchaseDecision.PurchaseGranted
end

MarketplaceService.ProcessReceipt = function(receiptInfo)
    local player = Players:GetPlayerByUserId(receiptInfo.PlayerId)
    if not player then
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    local productName = resolveProductNameById(receiptInfo.ProductId)
    if not productName then
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    return grantProduct(player, productName)
end

PurchaseRequest.OnServerEvent:Connect(function(player, purchaseType, purchaseName)
    if purchaseType == "DeveloperProduct" then
        local productId = GameConfig.DeveloperProducts[purchaseName]
        if productId and productId ~= 0 then
            MarketplaceService:PromptProductPurchase(player, productId)
        end
    elseif purchaseType == "Gamepass" then
        local gamepassId = GameConfig.Gamepasses[purchaseName]
        if gamepassId and gamepassId ~= 0 then
            MarketplaceService:PromptGamePassPurchase(player, gamepassId)
        end
    end
end)

MonetizationStateRequest.OnServerInvoke = function(player)
    local hasPremiumBuilder = false
    local gamepassId = GameConfig.Gamepasses.PremiumBuilder

    if gamepassId and gamepassId ~= 0 then
        local success, ownsPass = pcall(function()
            return MarketplaceService:UserOwnsGamePassAsync(player.UserId, gamepassId)
        end)

        hasPremiumBuilder = success and ownsPass
    end

    return {
        tokenBoost = playerTokenBoosts[player] or 0,
        premiumMultiplier = hasPremiumBuilder and GameConfig.PremiumBuilderMultiplier or 1,
        hasPremiumBuilder = hasPremiumBuilder,
    }
end

Players.PlayerRemoving:Connect(function(player)
    playerTokenBoosts[player] = nil
end)
