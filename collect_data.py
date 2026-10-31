"""
collect_data.py －全市場資料收集（規劃中）

收集臺灣證券交易所上市普通股（包含 2012 年後下市的公司）的 7 種 FinMind 資料：
損益表、資產負債表、現金流量表、月營收、每日股價、本益比/淨值比/殖利率、除權息結果。

設計要求：
  - 自動等待：API 次數用完時暫停，等額度恢復後繼續
  - 可接續：已抓過的（股票, 資料集）跳過，中斷後重跑會從斷點接著抓
  - 輸出 Parquet：每個資料集一個檔案，存在 data/raw/

輸入：TaiwanStockInfo、TaiwanStockDelisting（股票清單）
輸出：data/raw/{dataset}.parquet
負責：組員 C
"""

DATASETS = [
    "TaiwanStockFinancialStatements",
    "TaiwanStockBalanceSheet",
    "TaiwanStockCashFlowsStatement",
    "TaiwanStockMonthRevenue",
    "TaiwanStockPrice",
    "TaiwanStockPER",
    "TaiwanStockDividendResult",
]


def get_universe():
    """回傳研究範圍的股票代號清單：目前上市普通股＋2012 年後下市的公司。"""
    # TODO: 參考 verify_data.py 的篩選方式（4 位數、非 0 開頭、type == "twse"）
    raise NotImplementedError


def fetch_with_quota(dataset, data_id, start_date):
    """抓單一（資料集, 股票）；遇到 API 次數用完時自動等待後重試。"""
    # TODO: 偵測 402 狀態碼，等待到下一個小時再重試
    raise NotImplementedError


def load_progress():
    """讀取已完成的（股票, 資料集）清單，用於中斷後接續。"""
    # TODO: 從 data/raw/ 既有檔案或進度檔判斷已完成項目
    raise NotImplementedError


def save_parquet(dataset, df):
    """把資料附加存成 data/raw/{dataset}.parquet。"""
    # TODO: 需要 pyarrow；處理欄位型別（stock_id 一律為字串）
    raise NotImplementedError


def main():
    """依股票清單與資料集清單逐一收集，跳過已完成項目。"""
    # TODO: get_universe → load_progress → 迴圈 fetch_with_quota → save_parquet
    raise NotImplementedError


if __name__ == "__main__":
    main()
