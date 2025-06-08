# python_StockNotify
股價資訊通知


使用 GCP 中的 Cloud Scheduler 達到批次排程作業～

 ## 作法：

1. 建立『Pub/Sub』，並增加觸發條件『Cloud Functions』

2. 將程式放進『Cloud Functions』

3. 增加『Cloud Scheduler』，設定執行作業為『Pub/Sub』，主題要使用剛剛建好的

### 記得要放 token 上 GCP 
### local 需使用 .env