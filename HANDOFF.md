# 旅ことば Tabi Kotoba — 交接檔

日本旅遊日文單字卡 PWA（手機優先、可離線）。repo：`jeremyl861225/tabi-kotoba`（public，**尚未建立**），
上線網址預定 <https://jeremyl861225.github.io/tabi-kotoba/>。

整套做法已抽成 skill **`travel-vocab-app-builder`**（`~/.claude/skills/travel-vocab-app-builder/`），
之後要拿來做韓文、法文、冰島文版。這裡完成的每個階段若踩到新坑，**回頭寫進那份 skill**（SKILL.md 的「常見錯誤」與「跨版本修正紀錄」）。

## 已定案的決定（2026-09-24 與使用者確認）

| 項目 | 決定 |
|---|---|
| 字卡總量 | 1,200 詞（87 課） |
| 主題 | 22 條：寒暄、數字、動詞形容詞、機場、電車、巴士計程車、自駕加油、問路、飯店、溫泉旅館、餐廳、料理、飲料甜點、購物、便利商店、藥妝、看醫生、緊急、觀光、標示、網路領錢天氣、店員與廣播常說的話（名稱在 `tools/themes.py`） |
| 詞頻定義 | **旅遊實用頻率**：38 份中日英旅遊日語清單合併，被越多份收錄越優先；同分看 wordfreq Zipf。必備 25%／常用 37.5%／進階 37.5% |
| 單元 | 先分級、級內依主題；**一站＝一課**（每課 ≤20 張），首頁每個等級是一條線 |
| 發音 | 預錄音檔，微軟 Nanami（女）與 Keita（男）交替（edge-tts，使用者已知是非官方管道）。AivisSpeech 被否決（太刻意太尖銳） |
| 考題 | 8 種：看日文選中文、看中文選日文、看漢字選讀音、聽發音選單字、聽發音選中文、聽例句選意思、拼出讀音（假名方塊）、聽寫 |
| 查詢 | 字卡搜尋（漢字、假名、羅馬拼音、中文）＋離線字典（JMdict 常用詞 22,639 詞，英文釋義）補字卡以外的字 |
| 視覺 | 米色底＋暖咖啡深色模式；Colormind 色票依主題家族當點綴（線、站點、按鈕）；日文明朝、中文宋體（系統字）；首頁路線圖；不放插圖、不要幼稚感、不要慢動畫。詳見 skill 的 design.md 與本 repo 的 PRODUCT.md |
| 名稱 | 旅ことば Tabi Kotoba，repo `tabi-kotoba` |

## 進度

- [x] 需求訪談、語音試聽
- [x] App 外殼與介面（路線圖、學習、8 種測驗、搜尋＋離線字典、不熟、設定、離線、深色模式）
- [x] 來源蒐集：38 份、2,828 筆 → `workspace/work/jp-travel-vocab/sources/`
- [x] 正規化：2,321 個候選 → `build/candidates.json`
- [x] 選字：代理＋`auto_curate.py` 規則補完＋`build/curate/manual.json`（刪 128 個多餘數字、補 46 個標準日期時間）
- [x] 排名、分級、分課：1,200 張、87 課 → `build/selection.json`、`build/ids.json`（編號登記，勿刪）
- [~] 字卡撰寫：12 批 × 100 張（`build/author/in-01…12.json` → `out-*.json`）。01–04 完成；05–08 代理撰寫中；09–12 待派
- [~] build_data：已處理 `drop:true`（先拿掉、列進 qa 的 dropped；遞補要寫 manual.json 再跑 select）、以 pos 修正 kind、簡體字檢查改 s2tw；待全部寫完後 `build/qa.json` 清到 0、抽 30 張讀過
- [ ] 語音：`tools/make_audio.py`（約 4,800 個檔、約 60 MB）
- [~] e2e：首頁選擇器已改 `.stn`；待資料完成後跑 `--all-cards`
- [x] index.html 開頭的 direction contract 註解更新成現在的米色版
- [ ] impeccable 收尾：finish reviewer（截圖在 `.impeccable/review/`）→ documenter 產 DESIGN.md
- [ ] 建 GitHub repo、開 Pages、線上驗證（precache HEAD 檢查、快取筆數、iPhone 飛航模式）

代理撰寫時回報的待查項：0070 温めますか、0090 〜をください、0018 お元気ですか（kind 標 w 其實是句子）；0179 X線検査；
0284 ドラッグストアはどこですか（由截斷的來源句補回）；0299 軟膏（字典釋義是同音的「難航」）；0386 どんな（詞性）。

## 工具

| 程式 | 作用 |
|---|---|
| `tools/pipeline/common.py` | 路徑、JMdict／JmdictFurigana 索引、Sudachi |
| `tools/pipeline/normalize.py` | 來源 → 詞條鍵與收錄數 |
| `tools/pipeline/auto_curate.py` | 選字代理沒做完的分段用規則補完 |
| `tools/pipeline/select.py` | 排名、主題保底、分級、分課、編號登記 |
| `tools/pipeline/author_prep.py` | 切撰寫批次（跳過已寫好的） |
| `tools/pipeline/rubytools.py` | 單字標音、例句讀音比對、朗讀文字、羅馬拼音 |
| `tools/build_data.py` | 組 `data/cards.json`、`build/tts.json`、`build/qa.json` |
| `tools/make_audio.py` | edge-tts 批次產生並修剪靜音（可中斷續跑） |
| `tools/build_dict.py` | 離線字典 `data/dict.json` |
| `tools/themes.py` | 22 條主題的色票與推算色 |
| `tools/make_icons.py` | App 圖示 |
| `tools/e2e.py` | Playwright 手機視窗驗收 |

Python 環境：`workspace/work/jp-travel-vocab/.venv`（fugashi、sudachipy full、wordfreq、fonttools、edge-tts、opencc、jaconv）。
撰寫規格：`build/author/PROMPT.md`；選字規格：`build/curate/RULES.md`。

## 若中斷，下一步

看上面第一個未勾的項目；中間產物都在 `~/Desktop/Claude code/workspace/work/jp-travel-vocab/`。
撰寫批次：`ls build/author/out-*` 看哪些已完成，未完成的重派代理（派工方式見 skill 的 agents.md，每 20 條寫一次檔）。
