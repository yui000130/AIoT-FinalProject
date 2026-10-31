"""
agent.py －LLM Agent（規劃中）

核心原則：數字一律由程式與模型計算，LLM 只負責規劃與解釋；
報告中的數字會自動與工具輸出核對，不一致就重寫（最多 3 次，失敗則改用模板報告）。

流程見 DESIGN.md 第 8 節 Algorithm 1。也負責實驗 E4（Agent 報告 vs 單純 LLM）。

輸入：使用者查詢（股票代號、分析日期、篩選條件、追問）
輸出：結構化分析報告（潛力等級、機率 vs 5% 基準率、支持與反對證據、相似案例、不確定性）
負責：組員 A
"""

BASE_RATE = 0.05
MAX_REWRITE = 3


def classify_intent(query):
    """用 LLM 判斷意圖：個股分析、全市場篩選或追問。"""
    # TODO
    raise NotImplementedError


def plan_tasks(intent, query):
    """用 LLM 把查詢拆成工具呼叫序列。"""
    # TODO
    raise NotImplementedError


def run_tools(plan):
    """依序執行工具：取得特徵、模型預測、SHAP、kNN、規則檢查。"""
    # TODO
    raise NotImplementedError


def retrieve_similar_cases(features, analysis_date, k=5):
    """kNN 找特徵日早於分析日的相似成功與失敗案例。"""
    # TODO
    raise NotImplementedError


def retrieve_knowledge(rule_results, shap_values):
    """從 knowledge/ 檢索相關知識文件（RAG）。"""
    # TODO
    raise NotImplementedError


def write_report(tool_outputs, knowledge):
    """用 LLM 把工具輸出寫成報告。"""
    # TODO
    raise NotImplementedError


def verify_numbers(report, tool_outputs):
    """抽出報告中的所有數字，檢查是否都能對應到工具輸出；回傳不一致清單。"""
    # TODO
    raise NotImplementedError


def template_report(tool_outputs):
    """LLM 重寫失敗時，以固定模板產生報告。"""
    # TODO
    raise NotImplementedError


def analyze(query):
    """Agent 主流程入口。"""
    # TODO: classify_intent → plan_tasks → run_tools → write_report ⇄ verify_numbers
    raise NotImplementedError
