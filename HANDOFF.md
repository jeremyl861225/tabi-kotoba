# 旅ことば Tabi Kotoba — 交接檔

日本旅遊日文單字卡 PWA（手機優先、可離線）。repo：`jeremyl861225/tabi-kotoba`（public），
**已上線** <https://jeremyl861225.github.io/tabi-kotoba/>（2026-09-25）。

整套做法已抽成 skill **`travel-vocab-app-builder`**（`~/.claude/skills/travel-vocab-app-builder/`），
之後要拿來做韓文、法文、冰島文版。這裡完成的每個階段若踩到新坑，**回頭寫進那份 skill**（SKILL.md 的「常見錯誤」與「跨版本修正紀錄」）。

## 已定案的決定（2026-09-24 與使用者確認）

| 項目 | 決定 |
|---|---|
| 字卡總量 | 1,200 詞（88 課） |
| 主題 | 22 條：寒暄、數字、動詞形容詞、機場、電車、巴士計程車、自駕加油、問路、飯店、溫泉旅館、餐廳、料理、飲料甜點、購物、便利商店、藥妝、看醫生、緊急、觀光、標示、網路領錢天氣、店員與廣播常說的話（名稱在 `tools/themes.py`） |
| 詞頻定義 | **旅遊實用頻率**：38 份中日英旅遊日語清單合併，被越多份收錄越優先；同分看 wordfreq Zipf。必備 25%／常用 37.5%／進階 37.5% |
| 單元 | 先分級、級內依主題；**一站＝一課**（每課 ≤20 張），首頁每個等級是一條線 |
| 發音 | 預錄音檔，微軟 Nanami（女）與 Keita（男）交替（edge-tts，使用者已知是非官方管道）。AivisSpeech 被否決（太刻意太尖銳） |
| 考題 | 8 種：看日文選中文、看中文選日文、看漢字選讀音、聽發音選單字、聽發音選中文、聽例句選意思、拼出讀音（假名方塊）、聽寫 |
| 查詢 | 字卡搜尋（漢字、假名、羅馬拼音、中文）＋離線字典（JMdict 常用詞 22,639 詞，英文釋義）補字卡以外的字 |
| 視覺 | **白底**（2026-09-25 起，原本米色）＋暖咖啡深色模式；Colormind 色票依主題家族當點綴（線、站點、按鈕），首頁主題家族格與下一站卡片用該色約 10% 的淡彩；日文明朝、中文宋體（系統字）；首頁路線圖；不放插圖、不要幼稚感、不要慢動畫。詳見 skill 的 design.md 與本 repo 的 PRODUCT.md |
| 名稱 | 旅ことば Tabi Kotoba，repo `tabi-kotoba` |

## 進度

- [x] 需求訪談、語音試聽
- [x] App 外殼與介面（路線圖、學習、8 種測驗、搜尋＋離線字典、不熟、設定、離線、深色模式）
- [x] 來源蒐集：38 份、2,828 筆 → `workspace/work/jp-travel-vocab/sources/`
- [x] 正規化：2,321 個候選 → `build/candidates.json`
- [x] 選字：代理＋`auto_curate.py` 規則補完＋`build/curate/manual.json`（刪 128 個多餘數字、補 46 個標準日期時間）
- [x] 排名、分級、分課：1,200 張、88 課（遞補後） → `build/selection.json`、`build/ids.json`（編號登記，勿刪）
- [x] 字卡撰寫：12 批 × 100 張＋遞補 1 批 25 張（`build/author/in-01…13.json` → `out-*.json`）。代理刪了 25 張，已寫進 `curate/manual.json` 重跑 select 遞補（新卡 1201–1225）
- [x] build_data：1,200 張、88 課，`build/qa.json` 全部清到 0（讀音誤報逐張記在 `build/author/reading_ok.json`，人工修正在 `build/author/fix.json`）；抽 30 張讀過
- [x] 語音：4,800 個檔、56 MB（`tools/make_audio.py`，0 失敗）
- [x] e2e：`--all-cards` 全部通過（1,200 張、8 種題型都出現）
- [x] index.html 開頭的 direction contract 註解更新成現在的米色版
- [ ] impeccable 收尾：finish reviewer（截圖在 `.impeccable/review/`）→ documenter 產 DESIGN.md
- [x] 建 GitHub repo、開 Pages、線上驗證：CORE 15 檔與抽查音檔都是 200、預先快取 15 筆、斷網重開可用、離線字典可查（Chromium 實測）
- [ ] iPhone 實機：加到主畫面 → 設定頁下載必備線發音 → 飛航模式開一課、播發音、做測驗
- [x] 2026-09-25 使用者 iPhone 看過後的修改：首頁三個等級方塊改成**主題家族 3×3 色塊**（點了只看那一類）、三條線**可收合**、
  **每課有不重複的子題名稱**（`workspace/.../build/unit_names.json`，select 重跑要重新命名）、圖示改成**宋體「旅行」**；`CACHE_VERSION` 升到 v2
- [x] 2026-09-25：圖示整組置中、上下留白等寬（試過上移 3% 後使用者選回等寬）；字卡頁篩選標籤點了不再重畫整頁（標籤列停在原位）；
  **開場動畫**：日の丸紅圓（#BC002D）升起＋米色明朝「旅」，約 0.9 秒後淡出、點一下跳過、資料沒載完就繼續當載入畫面、減少動態效果時不顯示；`CACHE_VERSION` 升到 v6
- [x] 2026-09-25：**底色改白底**。首頁色塊比較了 6 種（白色細框、淺灰、淡彩、深色實色、下一站深色、下一站淡彩），選「淡彩」：
  每個主題的淡彩色碼由 `tools/themes.py` 算（`bgL` 白底上 10%、`bgD` 深色卡片面上 18%）；卡片改用細框＋淡陰影；開場的「旅」改白字（白底紅圓＝日章旗）；`CACHE_VERSION` 升到 v7。
  比較圖在 `workspace/work/jp-travel-vocab/shots/white/`。圖示仍是米色底（使用者沒要求改）

代理回報、可再斟酌的卡（不影響上線）：0889 移動博物館、0903 形態展示、0614 解説室 等博物館專門用語偏冷門；1016 空き部屋はありますか 與 0813 意思重疊；1126／1127／1133／1134 日期用阿拉伯數字（前面的日期卡用漢字數字）。

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
