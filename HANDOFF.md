# 旅ことば Tabi Kotoba — 交接檔

日本旅遊日文單字卡 PWA（手機優先、可離線）。repo：`jeremyl861225/tabi-kotoba`（public），
上線網址預定 <https://jeremyl861225.github.io/tabi-kotoba/>。

## 已定案的決定（2026-09-24 與使用者確認）

| 項目 | 決定 |
|---|---|
| 字卡總量 | 約 1200 詞 |
| 主題 | 過海關、購物、交通、食物、日常常用＋住宿溫泉、自駕加油、藥妝就醫緊急、聽懂對方說的話＋「所有旅途會用到的」（通訊、換匯、寄物、天氣、標示…） |
| 詞頻定義 | **旅遊實用頻率**：彙整多份中日英旅遊日語清單，被越多來源收錄＝越優先；同分以一般日語語料庫詞頻（wordfreq Zipf）排序。分「必備／常用／進階」三級 |
| 單元切法 | 先分級、級內依主題，每單元約 20 詞 |
| 發音 | 預錄音檔，**微軟 Nanami（女）與 Keita（男）兩種聲音交替**（edge-tts 產生；使用者已知是非官方管道）。AivisSpeech 被否決（「太刻意太尖銳」） |
| 考題 | 四種全要：看日文選中文、看中文選日文、聽發音選單字、看漢字選讀音 |
| 視覺 | ~~車站站牌風~~ → 2026-09-24 使用者要求用 skill 美化、參考 Drops：**Drops × 路線圖**（上課與測驗整片路線色、白色膠囊鍵、首頁為由必備往進階延伸的路線圖）。使用者指定必留：首頁路線圖進度、深色模式；不要：幼稚感、拖慢操作的動畫；不放單字插圖。設計紀錄見 PRODUCT.md 與 index.html 開頭的 direction contract |
| 名稱 | 旅ことば Tabi Kotoba，repo `tabi-kotoba` |

我自行決定的預設（使用者可改）：每卡一句禮貌體例句＋假名＋台灣用語中譯；「聽懂對方說的話」
的例句是可回應的一句；羅馬拼音可開關（預設關）；星號手動，考題答錯可一鍵加星；進度只存本機、
可匯出匯入備份。

## 進度

- [x] 需求訪談（兩輪）與語音試聽
- [x] App 外殼（PWA、路由、學習、測驗、搜尋、設定、離線）＋ Drops × 路線圖改版（impeccable skill）
- [~] 來源蒐集（中／日／英）→ `workspace/work/jp-travel-vocab/sources/`（38 份、2,828 筆；研究代理仍可能補）
- [x] 正規化（JMdict）→ `build/candidates.json`（`tools/pipeline/normalize.py`）
- [~] 選字（三個代理審核去留／修對應／分主題）→ `build/curate/out-*.json`
- [ ] 詞頻排序 ＋ 分級分單元（build_data.py）
- [ ] 字卡撰寫（中譯、例句）＋ 讀音／假名校對
- [ ] 語音產生（兩聲 × 單字＋例句）
- [ ] App（PWA）實作
- [ ] 驗收（資料檢查器＋Playwright 手機視窗）
- [ ] 部署 GitHub Pages ＋ 線上驗證

## 工具

- `tools/pipeline/common.py`：路徑、JMdict／JmdictFurigana 索引、Sudachi
- `tools/pipeline/normalize.py`：來源 → 詞條鍵與收錄數
- `tools/pipeline/rubytools.py`：單字標音（JmdictFurigana）、例句讀音比對（Sudachi）、朗讀文字、羅馬拼音
- `tools/themes.py`：22 條路線色與推算的色場／文字色（對比度自動達標）
- `tools/make_audio.py`：edge-tts 批次產生並修剪靜音
- `tools/subset_font.py`：M PLUS 1 依實際用字裁切成 woff2
- Python 環境：`workspace/work/jp-travel-vocab/.venv`（fugashi、sudachipy full、wordfreq、fonttools、edge-tts、opencc、jaconv）

## 若中斷，下一步

看上面第一個未勾的項目；中間產物都在 `~/Desktop/Claude code/workspace/work/jp-travel-vocab/`。
