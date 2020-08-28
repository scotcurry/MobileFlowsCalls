#!/bin/zsh
cd ~/PycharmProjects/ServiceNow
az webapp up --sku F1 --name "snmobileflows" -l "northcentralus" --resource-group "AppServices" --plan "appservicesplan" --subscription "d8a86ded-b25e-48ff-873a-bf101b435edd"
az webapp config appsettings set --resource-group "AppServices" --name "snmobileflows" --settings WEBSITES_PORT=8000
az webapp config appsettings set --resource-group "AppServices" --name "snmobileflows" --settings GOOGLE_APPLICATION_CREDENTIALS="/home/site/wwwroot"
az webapp config set --resource-group "AppServices" --name "snmobileflows" --linux-fx-version "PYTHON|3.8"
az webapp config set --resource-group "AppServices" --name "snmobileflows" --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app"