# Zeabur 部署

這個專案分成兩個服務。

## 服務 1：`glance`

### Image
`glanceapp/glance:latest`

### Port
- Port：`8080`
- Type：`HTTP`

### Volume
- Mount path：`/app/config`
- 內容：
  - `glance.yml`

### Environment
- `TZ=Asia/Taipei`
- `FEED_SERVICE_URL=https://<your-glance-feed-domain>`

`FEED_SERVICE_URL` 必須是 public URL，因為 Glance 會用 `iframe` 直接在瀏覽器讀內容。

## 服務 2：`glance-feed`

### Build
- 從這個 repo folder build
- Dockerfile：`feed-service/Dockerfile`

### Port
- Port：`8081`
- Type：`HTTP`

### Environment
- `PORT=8081`
- `TZ=Asia/Taipei`
- `KANBAN_SOURCE_PATH=/app/data/KANBAN.md`
- `DAILY_BRIEF_HTML_PATH=/app/data/daily-brief.html`

### Volume
- 第一版可以先不加額外資料 volume
- 如果你之後要讓這個服務吃真正的 Kanban / Daily Brief，直接把檔案放進 repo 的 `data/` 目錄，或改成掛 Zeabur volume

## 第一次部署順序

1. 先部署 `glance-feed`。
2. 複製它的 public URL。
3. 把 `FEED_SERVICE_URL` 填到 `glance`。
4. 再部署 `glance`。
5. 先打開 `glance-feed` 的 `/kanban` 和 `/daily-brief`。
6. 再打開 Glance 主頁，確認兩個 `iframe` widget 有正常載入。

## 備註

- Glance 原生的 `weather` 和 `markets` widget 不依賴 feed service。
- Kanban 和 Daily Brief 目前都設計成只讀。
- 如果之後想做更緊密的整合，可以把 `iframe` 改成 custom widget，後端還是同一個 feed service。
