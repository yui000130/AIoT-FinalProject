"""
Multibagger Scout －FinMind 數據可行性驗證程式（期中提案用）

這支程式會檢查四件事：
  1. 專題需要的 7 種資料，免費 API 是否都抓得到、從哪一年開始
  2. 目前上市公司數、每年下市公司數 → 估計研究樣本量
  3. 只用「每日股價＋除權息結果」能否自己算出 5 年含息報酬（還原股價是付費資料）
  4. 匯出台積電(2330) 的 EPS 與月營收，讓你和看盤 App 對照

不需要註冊：免費額度約每小時 300 次，本程式約用 215 次。
抓過的資料會存在 cache/ 資料夾，重跑不會再花次數。
如果之後註冊了，把 .env.example 複製成 .env 並填入 FINMIND_API_TOKEN，
額度會提高到每小時 600 次。.env 不要上傳 GitHub（.gitignore 已排除）。

執行：python verify_data.py
結果：output/ 資料夾（CSV 可用 Excel 開、PNG 可放 PPT、summary.md 是總結）
"""

import os
import random
import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests

# ───────────── 設定 ─────────────
def load_dotenv(path):
    """讀取同資料夾的 .env（KEY=VALUE 格式），不需要額外套件；沒有 .env 就略過。"""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_dotenv(Path(__file__).resolve().parent / ".env")
API_URL = os.environ.get("FINMIND_URL_DATA") or "https://api.finmindtrade.com/api/v4/data"
TOKEN = os.environ.get("FINMIND_API_TOKEN") or os.environ.get("FINMIND_TOKEN", "")  # 不註冊就留空
START_DATE = "2005-01-01"                      # 從這天開始抓，用來看資料最早到哪一年
N_LISTED = 20                                   # 抽樣：上市中的公司數
N_DELISTED = 10                                 # 抽樣：2012 年後下市的公司數
MUST_INCLUDE = ["2330", "2317", "2454"]         # 台積電、鴻海、聯發科一定要抽
SEED = 42                                       # 固定亂數種子，每次抽到同一批，結果可重現
SLEEP_SECONDS = 0.6                             # 每次請求間隔，避免太密集被擋
WINDOW_YEARS = list(range(2013, 2021))          # 研究視窗起始年（資產負債表 2012 年底才有，所以從 2013 年 4 月起算）
BASE = Path(__file__).resolve().parent
CACHE_DIR = BASE / "cache"
OUT_DIR = BASE / "output"

PER_STOCK_DATASETS = {
    "TaiwanStockFinancialStatements": "損益表",
    "TaiwanStockBalanceSheet": "資產負債表",
    "TaiwanStockCashFlowsStatement": "現金流量表",
    "TaiwanStockMonthRevenue": "月營收",
    "TaiwanStockPrice": "每日股價",
    "TaiwanStockPER": "本益比/淨值比/殖利率",
    "TaiwanStockDividendResult": "除權息結果",
}

COMMON_STOCK_ID = re.compile(r"[1-9]\d{3}")     # 4 位數、非 0 開頭 = 普通股（排除 ETF 等）


class QuotaExceeded(Exception):
    """API 次數用完"""


request_count = 0


# ───────────── 抓資料（含快取） ─────────────
def fetch(dataset, data_id=None, start_date=None):
    """抓一個資料集；抓過就直接讀 cache，不再花 API 次數。"""
    global request_count
    cache_file = CACHE_DIR / f"{dataset}_{data_id or 'ALL'}.csv"
    if cache_file.exists():
        try:
            return pd.read_csv(cache_file, dtype={"stock_id": str}, encoding="utf-8-sig")
        except pd.errors.EmptyDataError:
            return pd.DataFrame()

    params = {"dataset": dataset}
    if data_id:
        params["data_id"] = data_id
    if start_date:
        params["start_date"] = start_date
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

    body, resp = None, None
    for attempt in range(1, 4):
        try:
            resp = requests.get(API_URL, params=params, headers=headers, timeout=60)
            request_count += 1
            body = resp.json()
            break
        except (requests.RequestException, ValueError) as e:
            print(f"    連線失敗（第 {attempt} 次）：{e}，5 秒後重試")
            time.sleep(5)
    if body is None:
        print(f"    放棄：{dataset} {data_id or ''}")
        return pd.DataFrame()

    status = body.get("status", resp.status_code)
    if status == 402 or resp.status_code == 402:
        raise QuotaExceeded(body.get("msg", ""))
    if status != 200:
        print(f"    API 回傳錯誤 {status}：{body.get('msg', '')}（{dataset} {data_id or ''}）")
        return pd.DataFrame()

    df = pd.DataFrame(body.get("data", []))
    if "stock_id" in df.columns:
        df["stock_id"] = df["stock_id"].astype(str)
    df.to_csv(cache_file, index=False, encoding="utf-8-sig")
    time.sleep(SLEEP_SECONDS)
    return df


# ───────────── 含息報酬計算 ─────────────
def total_return(price_df, div_df, start, end):
    """
    用每日收盤價＋除權息結果，自己算含息報酬（等同還原股價）。
    原理：每次除權息，把「除權息前價格 / 參考價」累乘，
    代表把配到的股利再投入同一檔股票。
    end 之前就下市的公司，用最後一個交易日價格計算。
    """
    if price_df.empty or "close" not in price_df.columns:
        return None
    p = price_df[["date", "close"]].copy()
    p["date"] = pd.to_datetime(p["date"])
    p = p[p["close"] > 0].sort_values("date")
    start, end = pd.Timestamp(start), pd.Timestamp(end)

    before_start = p[p["date"] <= start]
    if before_start.empty:
        return None                      # 起始日還沒上市
    in_window = p[(p["date"] > start) & (p["date"] <= end)]
    if in_window.empty:
        return None                      # 起始日後就沒交易
    d0, p0 = before_start.iloc[-1]["date"], before_start.iloc[-1]["close"]
    d1, p1 = in_window.iloc[-1]["date"], in_window.iloc[-1]["close"]

    factor, n_events = 1.0, 0
    if not div_df.empty and {"before_price", "after_price"} <= set(div_df.columns):
        d = div_df.copy()
        d["date"] = pd.to_datetime(d["date"])
        d = d[(d["date"] > d0) & (d["date"] <= d1) & (d["after_price"] > 0) & (d["before_price"] > 0)]
        if not d.empty:
            factor = float((d["before_price"] / d["after_price"]).prod())
            n_events = len(d)

    return {
        "起始日": d0.date(), "起始價": p0, "結束日": d1.date(), "結束價": p1,
        "價格報酬": p1 / p0 - 1, "含息報酬": p1 / p0 * factor - 1,
        "除權息次數": n_events, "期中下市": d1 < end - pd.Timedelta(10, unit="D"),
    }


def total_return_index(price_df, div_df, start, end):
    """畫圖用：每日的價格指數與含息報酬指數（起始 = 1）。"""
    p = price_df[["date", "close"]].copy()
    p["date"] = pd.to_datetime(p["date"])
    p = p[(p["date"] >= pd.Timestamp(start)) & (p["date"] <= pd.Timestamp(end)) & (p["close"] > 0)]
    p = p.sort_values("date").set_index("date")
    p["factor"] = 1.0
    if not div_df.empty and {"before_price", "after_price"} <= set(div_df.columns):
        d = div_df.copy()
        d["date"] = pd.to_datetime(d["date"])
        for _, row in d.iterrows():
            if row["after_price"] > 0 and row["date"] in p.index and row["date"] > p.index[0]:
                p.loc[row["date"], "factor"] = row["before_price"] / row["after_price"]
    p["price_index"] = p["close"] / p["close"].iloc[0]
    p["tr_index"] = p["price_index"] * p["factor"].cumprod()
    return p


# ───────────── 輸出工具 ─────────────
def md_table(df):
    """把 DataFrame 轉成 Markdown 表格（不需要額外套件）。"""
    cols = list(df.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(v) for v in row.values) + " |")
    return "\n".join(lines)


def pct(x):
    return "" if pd.isna(x) else f"{x * 100:.1f}%"


# ───────────── 主程式 ─────────────
def main():
    CACHE_DIR.mkdir(exist_ok=True)
    OUT_DIR.mkdir(exist_ok=True)
    print("=== Multibagger Scout 數據驗證 ===")
    print("模式：" + ("已設定 Token（每小時約 600 次）" if TOKEN else "未註冊（每小時約 300 次）"))

    # 1. 股票清單與下市名單
    print("\n[1/5] 取得上市股票清單與下市櫃名單")
    info = fetch("TaiwanStockInfo")
    info = info.sort_values("date").drop_duplicates("stock_id", keep="last")
    listed = info[(info["type"] == "twse") & info["stock_id"].str.fullmatch(COMMON_STOCK_ID)]
    delist = fetch("TaiwanStockDelisting")
    delist["date"] = pd.to_datetime(delist["date"])
    delist = delist[delist["stock_id"].str.fullmatch(COMMON_STOCK_ID)]
    delist_recent = delist[(delist["date"] >= "2012-01-01") & ~delist["stock_id"].isin(listed["stock_id"])]
    print(f"    目前上市普通股：{len(listed)} 家；2012 年後下市櫃：{delist_recent['stock_id'].nunique()} 家")

    rng = random.Random(SEED)
    pool = sorted(set(listed["stock_id"]) - set(MUST_INCLUDE))
    sample_listed = MUST_INCLUDE + rng.sample(pool, N_LISTED - len(MUST_INCLUDE))
    dl_pool = sorted(delist_recent["stock_id"].unique())
    sample_delisted = rng.sample(dl_pool, min(N_DELISTED, len(dl_pool)))
    groups = {s: "上市中" for s in sample_listed} | {s: "已下市" for s in sample_delisted}
    names = dict(zip(info["stock_id"], info["stock_name"])) | dict(zip(delist["stock_id"], delist["stock_name"]))

    # 2. 逐檔抓 7 種資料
    print(f"\n[2/5] 逐檔抓資料：{len(groups)} 檔 × {len(PER_STOCK_DATASETS)} 種")
    data, coverage, stopped = {}, [], False
    for i, (sid, grp) in enumerate(groups.items(), 1):
        print(f"    ({i}/{len(groups)}) {sid} {names.get(sid, '')}［{grp}］")
        for ds, ds_name in PER_STOCK_DATASETS.items():
            try:
                df = fetch(ds, sid, START_DATE)
            except QuotaExceeded as e:
                print(f"\n!!! API 次數已用完（{e}）。已抓的資料都存在 cache/，一小時後重跑會接著抓。")
                stopped = True
                break
            data[(sid, ds)] = df
            ok = not df.empty
            coverage.append({
                "股票代號": sid, "名稱": names.get(sid, ""), "狀態": grp, "資料集": ds_name,
                "抓到": "是" if ok else "否", "筆數": len(df),
                "最早日期": df["date"].min() if ok else "", "最晚日期": df["date"].max() if ok else "",
            })
        if stopped:
            break

    cov = pd.DataFrame(coverage)
    cov.to_csv(OUT_DIR / "1_sample_coverage.csv", index=False, encoding="utf-8-sig")

    summary_rows = []
    for ds, ds_name in PER_STOCK_DATASETS.items():
        sub = cov[cov["資料集"] == ds_name] if not cov.empty else cov
        got = sub[sub["抓到"] == "是"] if not sub.empty else sub
        listed_got = got[got["狀態"] == "上市中"] if not got.empty else got
        summary_rows.append({
            "資料": ds_name, "資料集代碼": ds,
            "上市中抓到": f"{len(listed_got)}/{len(sub[sub['狀態'] == '上市中']) if not sub.empty else 0}",
            "已下市抓到": f"{len(got) - len(listed_got)}/{len(sub[sub['狀態'] == '已下市']) if not sub.empty else 0}",
            "最早日期": got["最早日期"].min() if not got.empty else "",
            "起始日中位數": pd.to_datetime(got["最早日期"]).median().date() if not got.empty else "",
        })
    ds_summary = pd.DataFrame(summary_rows)
    ds_summary.to_csv(OUT_DIR / "2_dataset_summary.csv", index=False, encoding="utf-8-sig")
    print("\n" + ds_summary.to_string(index=False))

    # 3. 樣本量估計
    print("\n[3/5] 估計研究樣本量")
    first_trade = {}
    for sid in sample_listed:
        df = data.get((sid, "TaiwanStockPrice"), pd.DataFrame())
        if not df.empty:
            first_trade[sid] = pd.to_datetime(df["date"]).min()
    est_rows = []
    for y in WINDOW_YEARS:
        t = pd.Timestamp(f"{y}-04-30")
        share = sum(d <= t for d in first_trade.values()) / max(len(first_trade), 1)
        low = round(len(listed) * share)
        dl_after = delist[delist["date"] > t]["stock_id"].nunique()
        est_rows.append({"視窗起始": f"{y}-04", "現存公司推估": low,
                         "加上之後下市者（上限）": low + dl_after})
    est = pd.DataFrame(est_rows)
    total_low, total_high = est["現存公司推估"].sum(), est["加上之後下市者（上限）"].sum()
    est.to_csv(OUT_DIR / "3_sample_size_estimate.csv", index=False, encoding="utf-8-sig")
    delist_by_year = delist.groupby(delist["date"].dt.year)["stock_id"].nunique().rename("下市櫃家數")
    delist_by_year = delist_by_year[delist_by_year.index >= 2012]
    delist_by_year.to_csv(OUT_DIR / "3_delisting_by_year.csv", encoding="utf-8-sig")
    print(est.to_string(index=False))
    print(f"    合計樣本約 {total_low:,}～{total_high:,} 筆；前 5% 暴漲股約 "
          f"{round(total_low * 0.05):,}～{round(total_high * 0.05):,} 筆")

    # 4. 含息報酬
    print("\n[4/5] 用股價＋除權息自己算 5 年含息報酬")
    ret_rows = []
    for sid, grp in groups.items():
        price = data.get((sid, "TaiwanStockPrice"), pd.DataFrame())
        div = data.get((sid, "TaiwanStockDividendResult"), pd.DataFrame())
        for y in (2012, 2019):
            r = total_return(price, div, f"{y}-04-30", f"{y + 5}-04-30")
            if r:
                ret_rows.append({"股票代號": sid, "名稱": names.get(sid, ""), "狀態": grp,
                                 "視窗": f"{y}-04 → {y + 5}-04", **r})
    rets = pd.DataFrame(ret_rows)
    if not rets.empty:
        show = rets.copy()
        show["價格報酬"] = show["價格報酬"].map(pct)
        show["含息報酬"] = show["含息報酬"].map(pct)
        show.to_csv(OUT_DIR / "4_five_year_returns.csv", index=False, encoding="utf-8-sig")
        print(show[["股票代號", "名稱", "視窗", "價格報酬", "含息報酬", "除權息次數", "期中下市"]]
              .head(12).to_string(index=False))

    price_2330 = data.get(("2330", "TaiwanStockPrice"), pd.DataFrame())
    div_2330 = data.get(("2330", "TaiwanStockDividendResult"), pd.DataFrame())
    if not price_2330.empty:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            idx = total_return_index(price_2330, div_2330, "2019-04-30", "2024-04-30")
            fig, ax = plt.subplots(figsize=(9, 4.5))
            ax.plot(idx.index, idx["price_index"], label="Price only", color="#9aa0a6")
            ax.plot(idx.index, idx["tr_index"], label="Total return (dividends reinvested)", color="#1a73e8")
            ax.set_title("2330 TSMC, Apr 2019 - Apr 2024 (start = 1)")
            ax.set_ylabel("Growth of 1")
            ax.legend(frameon=False)
            ax.spines[["top", "right"]].set_visible(False)
            fig.tight_layout()
            fig.savefig(OUT_DIR / "4_tsmc_total_return.png", dpi=200)
            plt.close(fig)
            print("    已輸出 4_tsmc_total_return.png")
        except ImportError:
            print("    沒裝 matplotlib，略過畫圖")

    # 5. 台積電核對表
    print("\n[5/5] 匯出台積電核對表（請對照看盤 App）")
    check = []
    fs = data.get(("2330", "TaiwanStockFinancialStatements"), pd.DataFrame())
    if not fs.empty:
        eps = fs[fs["type"] == "EPS"].sort_values("date").tail(4)
        check += [{"項目": "EPS（元）", "期間": d, "FinMind 數值": v} for d, v in zip(eps["date"], eps["value"])]
    rev = data.get(("2330", "TaiwanStockMonthRevenue"), pd.DataFrame())
    if not rev.empty:
        rev = rev.sort_values("date").tail(3)
        check += [{"項目": "月營收（億元）", "期間": f"{int(y)}-{int(m):02d}", "FinMind 數值": round(v / 1e8, 2)}
                  for y, m, v in zip(rev["revenue_year"], rev["revenue_month"], rev["revenue"])]
    if not price_2330.empty:
        last = price_2330.sort_values("date").tail(1).iloc[0]
        check.append({"項目": "收盤價（元）", "期間": last["date"], "FinMind 數值": last["close"]})
    checklist = pd.DataFrame(check)
    if not checklist.empty:
        checklist["App 數值"] = ""
        checklist["是否一致"] = ""
        checklist.to_csv(OUT_DIR / "5_tsmc_crosscheck.csv", index=False, encoding="utf-8-sig")
        print(checklist.to_string(index=False))

    # 總結
    lines = [
        "# FinMind 數據驗證結果", "",
        f"- 執行時間：{pd.Timestamp.now():%Y-%m-%d %H:%M}",
        f"- 模式：{'已註冊' if TOKEN else '未註冊'}；本次實際呼叫 API {request_count} 次",
        f"- 抽樣：上市中 {len(sample_listed)} 檔、已下市 {len(sample_delisted)} 檔（亂數種子 {SEED}）",
        f"- 目前上市普通股 {len(listed)} 家；2012 年後下市櫃 {delist_recent['stock_id'].nunique()} 家",
        "" if not stopped else "- **注意：API 次數用完，資料不完整，請一小時後重跑**",
        "", "## 各資料集是否抓得到", "", md_table(ds_summary),
        "", "## 樣本量估計（2013–2020 每年 4 月底起算）", "", md_table(est), "",
        f"合計約 {total_low:,}～{total_high:,} 筆，前 5% 暴漲股約 "
        f"{round(total_low * 0.05):,}～{round(total_high * 0.05):,} 筆。",
        "上限包含之後下市的公司，但下市櫃表沒有區分上市或上櫃，所以會偏高。",
    ]
    if not rets.empty:
        lines += ["", "## 5 年含息報酬示範（前 10 筆）", "",
                  md_table(show[["股票代號", "名稱", "視窗", "價格報酬", "含息報酬", "除權息次數"]].head(10))]
    (OUT_DIR / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\n完成！本次呼叫 API {request_count} 次。結果在 {OUT_DIR}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("已中斷，已抓的資料保留在 cache/")
    except QuotaExceeded as e:
        sys.exit(f"API 次數已用完（{e}）。已抓的資料保留在 cache/，請一小時後重跑。")