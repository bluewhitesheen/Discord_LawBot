# Discord_LawBot

## 版本更迭
### version 2.4.0
* 將機器人推到 Heroku 上，惟需要讓機器人自己喚醒自己，目前先用 Uptime Bot 撐著

### version 2.5.2
* 支援 「！刑法227『條』」、「！釋字813『號』」
* 民法不再會誤判成國民法官法

### version 2.5.3
* 將使用說明移動至 usage.md，使用者現在只要輸入「!?」, 「!使用說明」,「！說明」即可

### version 2.6.0
* 新增管理員指令，輸入!!set [法條]，即可設定預設法條
* 將尋找法條之程式碼函數化

### version 2.7.0
* 如法條並不在 source code 內部，則自動去網站尋找第一個可以點的法條並搜尋

### version 2.7.1
* 解決與 MEE6 的 ! 指令前綴衝突

### version 2.7.2
* 修正其他法規的搜尋演算法（尋找 DOM element 是否包含 lebal-fei，故目前演算法暫不支援已廢棄法規
* 修正 Error 的回傳訊息，以及修改 usage.md

### version 2.7.5
* 修正 requests 連線數過高之問題
* 將 lawDict 文件化，並修改查詢函數邏輯