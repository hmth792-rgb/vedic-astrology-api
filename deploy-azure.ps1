# Azure Deployment Script for Astrology D1 Chart API

# Login to Azure (if not already logged in)
# az login

# Set variables
$resourceGroup = "bakulalApp"
$appName = "chartsapi"
$location = "centralindia"

# Deploy the app
Write-Host "Deploying Astrology D1 Chart API to Azure App Service..." -ForegroundColor Green

# Create a zip file of the application
Write-Host "Creating deployment package..." -ForegroundColor Yellow
Compress-Archive -Path * -DestinationPath deploy.zip -Force

# Deploy to Azure App Service
Write-Host "Uploading to Azure..." -ForegroundColor Yellow
az webapp deployment source config-zip --resource-group $resourceGroup --name $appName --src deploy.zip

# Set startup command
Write-Host "Configuring startup command..." -ForegroundColor Yellow
az webapp config set --resource-group $resourceGroup --name $appName --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app"

# Restart the app
Write-Host "Restarting app service..." -ForegroundColor Yellow
az webapp restart --resource-group $resourceGroup --name $appName

Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Your API is available at: https://$appName.azurewebsites.net" -ForegroundColor Cyan

# Clean up
Remove-Item deploy.zip