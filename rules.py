"""
rules.py －領域規則檢查（規劃中）

每條規則接收單一公司在特徵日的特徵，回傳：
  {"rule": 規則名稱, "triggered": 是否觸發, "evidence": 用到的數字}
結果作為報告中的反對證據或注意事項。共 2 條規則，都只用 build_dataset.py 的特徵判斷。
門檻由陳怡安訂定，固定說明與文獻出處記錄在 knowledge/。

輸入：單一公司當期特徵（dict 或 pandas.Series）
輸出：規則結果清單
負責：陳怡安
"""


def check_earnings_quality(features):
    """盈餘品質紅旗：營業現金流／淨利偏低。"""
    # TODO
    raise NotImplementedError


def check_overvaluation(features):
    """估值過高：本益比或帳面／市值落在全市場極端區間。"""
    # TODO
    raise NotImplementedError


def run_all_rules(features):
    """執行所有規則，回傳結果清單。"""
    # TODO
    raise NotImplementedError
