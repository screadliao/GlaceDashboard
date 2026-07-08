# Glance Dashboard

目標：把 `glanceapp/glance` 部署到 Zeabur，當成一個只讀 dashboard，用來顯示：

- 天氣
- 關注股票
- Claude Code Kanban
- Daily Brief 結果

## 建議架構

建議拆成兩個服務：

1. `glance`
   - 用 repo 內的 `glance/Dockerfile` 自建 image
   - `glance.yml` 會在 build 時 copy 進 `/app/config/glance.yml`
   - 對外 HTTP port `8080`

2. `glance-feed`
   - 一個很小的 companion service
   - 提供 HTML 頁面與 JSON summary
   - 供 Glance 嵌入 Kanban 和 Daily Brief 內容

Glance 只負責展示，feed service 負責資料整理。

## 為什麼要拆開

- 天氣和股票本來就是 Glance 原生 widget，直接用最省事。
- Kanban 和 Daily Brief 是你自己的專案內容，之後一定會改。
- 拆開可以避免每次內容調整都要碰 Glance 本體。

## 第一階段接法

- 天氣：Glance 原生 `weather` widget
- 股票：Glance 原生 `markets` widget
- Kanban：用 `iframe` 指到 `/kanban`
- Daily Brief：用 `iframe` 指到 `/daily-brief`

這樣第一版最穩，也最好驗證。

## 環境變數

### Glance
- `FEED_SERVICE_URL`：companion service 的公開 URL
- `TZ`：`Asia/Taipei`

### Feed service
- `KANBAN_SOURCE_PATH`：`KANBAN.md` 路徑，預設 `./data/KANBAN.md`
- `DAILY_BRIEF_HTML_PATH`：最新 Daily Brief HTML 檔案路徑，預設 `./data/daily-brief.html`
- `PORT`：HTTP port，預設 `8081`
- `TZ`：`Asia/Taipei`

## 本地開發

這個專案刻意維持輕量，feed service 只用 Python standard library。

### 本地啟動

```bash
cd AI-agent-basic-setting/300_Project/Glance-Dashboard
docker compose up --build
```

- Glance：`http://localhost:8080`
- Feed service：`http://localhost:8081`

### 資料流

```text
KANBAN.md -> feed service -> Glance iframe
Daily Brief HTML -> feed service -> Glance iframe
```

如果你還沒放真實內容，可以先讓這兩個檔案不存在，feed service 會顯示提示，不會直接壞掉。

## 部署說明

精確設定請看 [ZEABUR.md](./ZEABUR.md)。

簡化流程如下：

1. 建立 `glance-feed` 服務。
2. 取得它的 public URL。
3. 把 `FEED_SERVICE_URL` 填回 `glance`。
4. 建立 `glance` 服務，使用 `glance/Dockerfile` build。
5. 確認 `iframe` widget 能讀到公開的 feed URL。

## 後續擴充

- 改成 JSON-backed custom widget，整合會更緊。
- 加上 Claude Code task board 的只讀狀態提示。
- 如果 Daily Brief 未來要在同一個部署裡即時重生，再補一個 refresh 路徑。
