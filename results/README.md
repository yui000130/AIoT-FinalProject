# results/ －實驗結果（規劃中）

這個資料夾之後會放 `evaluate.py` 與 `agent.py` 產生的實驗結果。**目前尚無任何實驗結果。**

| 實驗 | 預計檔案 | 內容 |
|---|---|---|
| E1 | `e1_ranking_metrics.csv` | 各模型與 Baseline 的 Precision@20/50、Recall@50、PR-AUC |
| E2 | `e2_portfolio.csv`、`e2_portfolio.png` | 前 50 檔等權組合 vs 0050 的累積報酬與最大回撤 |
| E3 | `e3_shap_ranking.csv`、`e3_shap.png` | SHAP 特徵排名與分組命中率 |
| E4 | `e4_agent_eval.csv` | Agent 報告 vs 單純 LLM 的數字正確率、證據引用率、使用者評分 |
| E5 | `e5_horizon_sensitivity.csv` | 3 年與 5 年觀察期的 Precision@50 比較 |

每次更新結果時，請同步更新 `DESIGN.md` 第 11 節與 Change Log。
