# Multibagger Scout（台股潛力股偵察員）

**Multibagger Scout: A Point-in-Time AI Agent for Identifying Potential High-Return Stocks in Taiwan**

使用者輸入一家台灣上市公司，Agent 只使用「當時已公告」的公開資料，判斷它未來 5 年是否具備「暴漲股」特徵，並用歷史相似案例與財報證據說明理由。

> **免責聲明**：本專題為大學課程的研究與教學用途，所有輸出皆不構成任何投資建議。投資有風險，請自行判斷。

完整系統設計請見 **[DESIGN.md](DESIGN.md)**。

---

## 專題狀態：提案階段

### 已完成

- [x] 資料可行性驗證（`verify_data.py`）：抽樣 30 檔（上市中 20、已下市 10），確認 7 種資料的可得性、起始年份、研究樣本量
- [x] 用「每日股價＋除權息結果」自行計算 5 年含息報酬（免費 API 不提供還原股價）
- [x] 台積電 4 季 EPS 與收盤價，與券商 App 核對 5/5 一致
- [x] 系統設計文件（`DESIGN.md`）與規劃中程式的骨架

### 規劃中

- [ ] 全市場資料收集（`collect_data.py`）
- [ ] Point-in-Time「公司 × 年份」資料集建構（`build_dataset.py`）
- [ ] LightGBM 與邏輯迴歸模型訓練（`train.py`）
- [ ] 三輪 walk-forward 回測與 Baseline 比較（`evaluate.py`）
- [ ] 領域規則與知識庫（`rules.py`、`knowledge/`）
- [ ] LLM Agent：任務規劃、案例檢索、報告生成與數字核對（`agent.py`）
- [ ] Streamlit 網站（`app.py`）
- [ ] 實驗 E1–E5 與使用者評估（`results/`）

---

## 快速開始

1. 安裝 **Python 3.10 以上**
2. 下載專案並安裝套件：

   ```bash
   git clone https://github.com/yui000130/AIoT-FinalProject.git
   cd AIoT-FinalProject
   pip install -r requirements.txt
   ```

3. （選用）設定 API Token：把 `.env.example` 複製成 `.env`，填入 FinMind Token。
   不註冊也能執行（免費額度約每小時 300 次）；註冊後約每小時 600 次。

   ```bash
   cp .env.example .env      # Windows PowerShell：Copy-Item .env.example .env
   ```

   > `.env` 已被 `.gitignore` 排除，**請勿上傳到 GitHub**。

4. 執行資料驗證：

   ```bash
   python verify_data.py
   ```

   約使用 215 次 API。抓過的資料會快取在 `cache/`，重跑不會再花次數；如果中途次數用完，一小時後重跑會接著抓。

### `verify_data.py` 輸出檔案（`output/`）

| 檔案 | 內容 |
|---|---|
| `1_sample_coverage.csv` | 30 檔抽樣股票 × 7 種資料：是否抓到、筆數、最早與最晚日期 |
| `2_dataset_summary.csv` | 各資料集在上市中與已下市公司的抓取率、最早日期 |
| `3_sample_size_estimate.csv` | 每個視窗起始年的樣本量推估（現存公司數與含下市公司的上限） |
| `3_delisting_by_year.csv` | 2012 年後每年下市櫃家數 |
| `4_five_year_returns.csv` | 抽樣股票的 5 年價格報酬與含息報酬示範 |
| `4_tsmc_total_return.png` | 台積電 2019-04 → 2024-04 價格指數與含息報酬指數比較圖 |
| `5_tsmc_crosscheck.csv` | 台積電 EPS、月營收、收盤價核對表（空欄位供填入看盤 App 數值） |
| `summary.md` | 以上結果的 Markdown 總結 |

---

## 資料來源與授權

| 來源 | 用途 | 說明 |
|---|---|---|
| [FinMind](https://finmindtrade.com/) | 財報、月營收、股價、本益比、除權息、上市與下市名單 | 免費方案**限非商業用途**；本專題僅用於課程研究 |
| 臺灣證券交易所 OpenAPI | 補充市場資料（規劃中） | 政府公開資料 |
| 公開資訊觀測站 | 公告日期與財報補充（規劃中） | 政府公開資料 |

- FinMind 免費版**不提供還原股價與市值**：含息報酬由「每日股價＋除權息結果」自行計算；市值規劃由股價與股本自行計算。
- `cache/` 與 `output/` 為 API 原始資料與衍生結果，已排除於版本控制之外，不在 repo 中重新散布。

---

## 目錄結構

```
.
├── README.md                 # 本檔案
├── DESIGN.md                 # 系統設計文件
├── requirements.txt          # Python 套件
├── .env.example              # 環境變數範本（Token、API 端點）
├── .gitignore
├── verify_data.py            # 已完成：資料可行性驗證
├── collect_data.py           # 規劃中：全市場資料收集
├── build_dataset.py          # 規劃中：Point-in-Time 特徵與標記資料表
├── train.py                  # 規劃中：LightGBM 與邏輯迴歸訓練
├── evaluate.py               # 規劃中：walk-forward 回測與 Baseline 比較
├── rules.py                  # 規劃中：領域規則檢查
├── agent.py                  # 規劃中：LLM Agent
├── app.py                    # 規劃中：Streamlit 網站
├── knowledge/                # 規劃中：投資知識文件（RAG 用）
│   └── README.md
├── results/                  # 規劃中：實驗結果
│   └── README.md
├── cache/                    # 執行後產生：API 回應快取（不上傳）
└── output/                   # 執行後產生：驗證結果（不上傳）
```

---

## 組員與分工

| 組員 | 提案階段 | 期末負責 |
|---|---|---|
| A | 動機與文獻 | Agent（LLM）與 Streamlit 網站 |
| B | 領域研究 | 領域規則、知識庫、使用者評估、簡報與影片統籌 |
| C | 技術與資料 | 資料收集、資料集、模型與回測 |
