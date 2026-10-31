"""
app.py －Streamlit 網站（規劃中）

三個頁面：
  1. 個股分析：輸入股票代號與分析日期，顯示 Agent 報告、相似案例卡片，可追問
  2. 全市場篩選：依年度與條件列出機率最高的公司
  3. 回測成果：顯示 E1–E5 實驗結果

執行（完成後）：streamlit run app.py
頁面底部須顯示免責聲明：研究與教學用途，不構成投資建議。

輸入：使用者操作
輸出：網頁
負責：組員 A
"""


def page_stock_analysis():
    """個股分析頁：呼叫 agent.analyze 並顯示報告與相似案例卡片。"""
    # TODO
    raise NotImplementedError


def page_screener():
    """全市場篩選頁：依條件列出機率最高的公司。"""
    # TODO
    raise NotImplementedError


def page_backtest():
    """回測成果頁：讀取 results/ 顯示實驗表格與圖。"""
    # TODO
    raise NotImplementedError


def main():
    """側欄切換三個頁面。"""
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    main()
