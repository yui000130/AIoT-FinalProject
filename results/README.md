# results/ －實驗結果（規劃中）

這個資料夾之後會放 `evaluate.py` 與 `agent.py` 產生的實驗結果。**目前尚無任何實驗結果。**

## 已放入的檔案

| 檔案 | 內容 |
|---|---|
| `tsmc_crosscheck.csv` | 資料正確性核對（非實驗結果）：台積電 FinMind 數值與 Yahoo 股市逐項比對，8/8 一致，附來源網址。核對日期 2026-10-31 |

## 規劃中的實驗結果

| 實驗 | 預計檔案 | 內容 |
|---|---|---|
| E1 | `e1_ranking_metrics.csv` | 各模型與 Baseline 的 Precision@20/50、Recall@50、PR-AUC |
| E2 | `e2_portfolio.csv`、`e2_portfolio.png` | 前 50 檔等權組合 vs 0050 的累積報酬與最大回撤 |
| E3 | `e3_shap_ranking.csv`、`e3_shap.png` | SHAP 特徵排名；基本面暴漲股、炒作型暴漲股、普通股、期間下市公司四組的特徵中位數與命中率 |
| E4 | `e4_agent_eval.csv` | Agent 報告 vs 單純 LLM 的數字正確率、證據引用率；（延伸）使用者評分 |
| E5 | `e5_sensitivity.csv` | （延伸）觀察期 3 年 vs 5 年、主要 vs 對照標記、營收門檻 5% / 10% / 15% 的 Precision@50 比較 |

每次更新結果時，請同步更新 `DESIGN.md` 第 11 節與 Change Log。
