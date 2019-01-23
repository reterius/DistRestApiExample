# DistRestApiExample
Distributed Rest Api Example

-Rest Api'yi çalıştırmak için DistRestApiExample dizini altındaki Api.py dosyasını çalıştırın

-CheckLogin adlı worker'ı ayağa kaldırmak için, terminalde DistRestApiExample klasörünün parent'ında aşağıdaki komutu çalıştırın  :
celery -A DistRestApiExample.CheckLoginWorker worker --loglevel=info


-Flower monitoring panelini ayağa kaldırmak için, terminalde DistRestApiExample klasörünün parent'ında aşağıdaki komutu çalıştırın  :
celery -A DistRestApiExample.CeleryApp.CeleryObj flower

## Api Dökümantasyonu

https://app.swaggerhub.com/organizations/Reterius-Software/projects/TasksManagementProject