"""
build_dataset.py －Point-in-Time「公司 × 年份」資料集建構（規劃中）

對 2013–2020 年每年 4 月底的特徵日 t：
  1. 取 t 時仍上市的普通股（包含之後下市者）
  2. 只用「可用日 ≤ t」的資料計算約 15 項特徵
  3. 計算 t → t + 5 年的含息報酬（股價＋除權息累乘），期間下市用最後交易日價格
  4. 當年含息報酬前 5% 標記為 1，其餘為 0

演算法見 DESIGN.md 第 8 節 Algorithm 2。

輸入：data/raw/*.parquet（collect_data.py 產生）
輸出：data/dataset.parquet（每列 = 公司 × 特徵年，含特徵與標記）
負責：組員 C
"""

FEATURE_YEARS = list(range(2013, 2021))
HORIZON_YEARS = 5
TOP_PCT = 0.05


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


def compute_features(stock_id, t):
    """計算單一公司在特徵日 t 的約 15 項特徵（只用可用日 ≤ t 的資料）。"""
    # TODO: 市值、FCF 殖利率、帳面/市值、本益比、殖利率、ROA、ROE、毛利率、
    #       EBITDA 利潤率、月營收年增率、資產成長率、營業現金流/淨利、負債比、
    #       12 個月報酬、波動度、產業類別
    raise NotImplementedError


def total_return(stock_id, start, end):
    """計算 start → end 的含息報酬；期間下市則以最後交易日價格計算。"""
    # TODO: 可沿用 verify_data.py 的 total_return 邏輯
    raise NotImplementedError


def label_top_pct(returns, pct=TOP_PCT):
    """同一特徵年內，含息報酬前 pct 標記為 1，其餘為 0。"""
    # TODO
    raise NotImplementedError


def main():
    """建立全部特徵年的資料表並存檔。"""
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    main()
