"""
build_dataset.py －Point-in-Time「公司 × 年份」資料集建構（規劃中）

對 2013–2020 年每年 4 月底的特徵日 t：
  1. 取 t 時仍上市的普通股（包含之後下市者）
  2. 流動性過濾：排除 t 之前一年日均成交值最低 10% 的股票
  3. 只用「可用日 ≤ t」的資料計算約 15 項特徵
  4. 計算 t → t + 5 年的含息報酬（股價＋除權息累乘）；結束價取最後 60 個交易日平均，
     期間下市則用最後交易日價格
  5. 計算同期營收成長，做基本面確認（固定門檻，見 DESIGN.md 5.4；延伸：加入 EPS 條件）
  6. 產生兩種標記：
       y_raw （對照標記）：當年含息報酬前 5% = 1
       y_main（主要標記）：前 5% 且通過基本面確認 = 1

演算法見 DESIGN.md 第 8 節 Algorithm 2。

輸入：data/raw/*.parquet（collect_data.py 產生）
輸出：data/dataset.parquet（每列 = 公司 × 特徵年，含特徵、y_main、y_raw）
負責：游雅筑
"""

FEATURE_YEARS = list(range(2013, 2021))
HORIZON_YEARS = 5
TOP_PCT = 0.05                 # 報酬排名前 5%
LIQUIDITY_DROP_PCT = 0.10      # 排除日均成交值最低 10%
END_PRICE_DAYS = 60            # 結束價取最後 60 個交易日平均
GROWTH_CAGR = 0.10             # 基本面門檻：營收 5 年年複合成長率 ≥ 10%（事先固定，不依測試資料調整）


def feature_date(year):
    """回傳該年的特徵日（4 月 30 日；非交易日則取之前最近的交易日）。"""
    # TODO
    raise NotImplementedError


def available_date(dataset, record):
    """依法定公告期限推定一筆資料的「可用日」。"""
    # TODO: 年報 3 月底、季報與月營收依各自公告期限
    raise NotImplementedError


def universe_at(t):
    """回傳特徵日 t 時仍上市的普通股（包含之後下市者）。"""
    # TODO
    raise NotImplementedError


def liquidity_filter(stock_ids, t, drop_pct=LIQUIDITY_DROP_PCT):
    """排除 t 之前一年日均成交值最低 drop_pct 的股票（只用 t 之前的成交資料）。"""
    # TODO
    raise NotImplementedError


def compute_features(stock_id, t):
    """計算單一公司在特徵日 t 的約 15 項特徵（只用可用日 ≤ t 的資料）。"""
    # TODO: 市值、FCF 殖利率、帳面/市值、本益比、殖利率、ROA、ROE、毛利率、
    #       EBITDA 利潤率、月營收年增率、資產成長率、營業現金流/淨利、負債比、
    #       12 個月報酬、波動度、產業類別
    raise NotImplementedError


def total_return(stock_id, start, end, end_price_days=END_PRICE_DAYS):
    """計算 start → end 的含息報酬；結束價取最後 end_price_days 個交易日平均，期間下市則用最後交易日價格。"""
    # TODO: 除權息累乘可沿用 verify_data.py 的 total_return 邏輯
    raise NotImplementedError


def fundamental_growth(stock_id, start, end):
    """回傳同期營收成長資訊，供基本面確認使用。

    營收：start 前 12 個月合計 → end 前 12 個月合計（期間下市則用下市前最後 12 個月）
    （延伸）EPS：近 4 季合計（TTM）
    """
    # TODO
    raise NotImplementedError


def passes_fundamental_check(growth, cagr=GROWTH_CAGR):
    """基本面確認；資料不足則不通過並記錄。

    核心：營收 5 年年複合成長率 ≥ cagr
    （延伸）加入 EPS，與營收符合任一即通過：
        EPS 起點 > 0 時，5 年年複合成長率 ≥ cagr
        EPS 起點 ≤ 0 時，終點 > 0（由虧轉盈）
    """
    # TODO
    raise NotImplementedError


def make_labels(returns, passed, pct=TOP_PCT):
    """同一特徵年內產生兩種標記：y_raw = 報酬前 pct；y_main = 報酬前 pct 且通過基本面確認。"""
    # TODO
    raise NotImplementedError


def main():
    """建立全部特徵年的資料表並存檔。"""
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    main()
