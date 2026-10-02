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
| 視覺 | **2026-10-01 起改為「暮色玻璃」（流動天空＋液態玻璃＋Zen Old Mincho），以下為舊紀錄**：米白底 #f7f5f0（2026-09-25；米色、純白都試過）＋暖咖啡深色模式；**一個主題家族一個顏色**（Colormind 色票主色），當點綴（線、站點、按鈕）與下一站卡片的淡彩（12%）；首頁主題家族格是白色細框；日文明朝、中文宋體（系統字）；首頁路線圖；不放插圖、不要幼稚感、不要慢動畫。詳見 skill 的 design.md 與本 repo 的 PRODUCT.md |
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
- [x] impeccable 收尾：finish reviewer 兩輪（2026-10-02，截圖在 `.impeccable/review/`）→ `DESIGN.md`＋`.impeccable/design.json`
- [x] 建 GitHub repo、開 Pages、線上驗證：CORE 15 檔與抽查音檔都是 200、預先快取 15 筆、斷網重開可用、離線字典可查（Chromium 實測）
- [ ] iPhone 實機：加到主畫面 → 設定頁下載必備線發音 → 飛航模式開一課、播發音、做測驗
- [x] 2026-09-25 使用者 iPhone 看過後的修改：首頁三個等級方塊改成**主題家族 3×3 色塊**（點了只看那一類）、三條線**可收合**、
  **每課有不重複的子題名稱**（`workspace/.../build/unit_names.json`，select 重跑要重新命名）、圖示改成**宋體「旅行」**；`CACHE_VERSION` 升到 v2
- [x] 2026-09-25：圖示整組置中、上下留白等寬（試過上移 3% 後使用者選回等寬）；字卡頁篩選標籤點了不再重畫整頁（標籤列停在原位）；
  **開場動畫**：日の丸紅圓（#BC002D）升起＋米色明朝「旅」，約 0.9 秒後淡出、點一下跳過、資料沒載完就繼續當載入畫面、減少動態效果時不顯示；`CACHE_VERSION` 升到 v6
- [x] 2026-09-25：**底色改白底**。首頁色塊比較了 6 種（白色細框、淺灰、淡彩、深色實色、下一站深色、下一站淡彩），選「淡彩」：
  每個主題的淡彩色碼由 `tools/themes.py` 算（`bgL` 白底上 10%、`bgD` 深色卡片面上 18%）；卡片改用細框＋淡陰影；開場的「旅」改白字（白底紅圓＝日章旗）；`CACHE_VERSION` 升到 v7。
  比較圖在 `workspace/work/jp-travel-vocab/shots/white/`。圖示仍是米色底（使用者沒要求改）
- [x] 2026-09-25：使用者在測試 repo（`tabi-kotoba-test`，選完已關 Pages；GitHub repo 待使用者自己刪）選了第 6 種「下一站淡彩＋白色細框色塊」，並要求底色不要那麼白 → `#f7f5f0`；
  又指出「醫療緊急」色塊和下一站（看醫生）卡片顏色不同 → **同一家族的主題一律用家族主色**（`themes.py`）；`CACHE_VERSION` 升到 v10

代理回報、可再斟酌的卡（不影響上線）：0889 移動博物館、0903 形態展示、0614 解説室 等博物館專門用語偏冷門；1016 空き部屋はありますか 與 0813 意思重疊；1126／1127／1133／1134 日期用阿拉伯數字（前面的日期卡用漢字數字）。

## 已完成：擴充到日檢 N3（2026-09-26 上線 v15，commit 2dd14d99）

**4,479 張字卡、314 站**（旅遊 1,200 張／88 站＋日檢 N5–N3 新字 3,279 張／226 站），e2e `--all-cards` 通過、qa.json 清零、線上驗證過。
目標：路上招牌、菜單看得懂，店員敬語聽得懂，能自己組句（**連接詞加大篇幅**）；新字**混進現有三條線**（N5→必備、N4→常用、N3→進階），
編號照學習順序（0001–4479）。來源：日檢單字表（`workspace/.../dict/jlpt/n5–n3.csv`，open-anki-jlpt-decks MIT，資料源自 tanos.co.uk）＋三份補充清單
（`build/expand/connectives.json`、`keigo.json`、`signs_menus.json`）。做法已寫成 skill 的 `references/expansion.md`。

- 選字：3,011 候選 → 收 2,964（Sonnet 分流）＋補充清單 410 → 清標記、去重後新卡 3,279
- 撰寫：`build/author/in-14…46.json` → `out-*.json`（14–17 Opus、18–46 Sonnet，每代理四批）；`fix.json` 修 28 張（標音、例句用錯字義）；
  `reading_ok.json` 約 400 條逐張確認的分析器誤報（`"*"` 開頭是全域）；`example_ok.json` 11 張
- 分站：`tools/pipeline/group_prep.py` → `build/expand/group/out-<級>-<主題>.json`（48 條線 226 站，主線程改掉 14 個勉強的站名）；
  併進新字的旅遊站只採納 7 個改名（`unit_names.json`）
- 音檔：新增 13,116 個（字卡音檔總計約 190 MB：必備 29、常用 47、進階 116 MB）
- 備份：`build/selection.before-n3.json`（1,200 張版）、`selection.n3.json`（現行）；**`selection.json` 現在就是 N3 版**

### 字典（字卡以外的字，2026-09-26 完成）
- **22,639 詞全部中文釋義**（Haiku 代理翻譯，`build/dictzh/in-01…46.tsv` → `out-*.tsv`，人工修正 `fix.tsv`，`check.py` 驗收）；
  `build_dict.py` 只收格式正確的行，並用 `OPENCC_FIX` 改回 opencc 誤轉的字
- 字典詞可點開（`#/dict/<JMdict 編號>`），發音用預錄音檔 `audio/d/<編號>.mp3`（22,639 個、約 100 MB，點了才抓）

### 之後可做（沒有使用者要求，列著備查）
- 字典釋義是 AI 翻譯（約九成好）：看到錯的直接寫進 `build/dictzh/fix.tsv`（依編號）再跑 `build_dict.py`
- iPhone 實機離線測試（原本就列著的待辦）

## 2026-10-02：新圖示、數字與量詞專欄、數字聽力、五十音課程（v24）

使用者要求：圖示重做（顏色同天空漸層、取消鐵軌、日文用「旅」）；新增數字與量詞專欄（量詞配數字的變音，含日期時間）；新增數字聽力測驗（聽金額、日期、時間，填出數字）；新增五十音課程（由我發揮）。
- **圖示**：`tools/make_icons.py` 在瀏覽器裡用 `js/sky.js` 的著色器（`FRAG`＋`PALETTES.day`，t＝140）畫背景、柔化，中央墨色 Zen Old Mincho 900「旅」。
  要 Playwright 跑：`~/.claude/tools/playwright-venv/bin/python tools/make_icons.py`（`--variant ink|white|tile`、`--t` 可比較）。iPhone 要刪掉主畫面的捷徑再加一次才會換圖示。
- **數字與量詞**（`#/numbers`，`js/numbers.js`）：數字、量詞（19 個：つ 個 人 名 本 杯 枚 冊 匹 台 回 階 歳 泊 足 着 軒 番線 円）、日期（月、日、星期、今天明天、期間）、時間（時、24 小時制、分、時間）。
  讀音表在 `tools/build_numbers.py`（不規則的整張手寫），變音位置用「數字念法＋量詞基本念法」逐字比對自動標色（`hi`）。
- **數字聽力**（`#/numquiz`，測驗頁最上面也有入口）：題庫 370 句（金額 110、日期 70、時間 90、數量 100；女聲男聲各半），畫面上的數字鍵填答，時間填 24 小時制；成績存 `store.numq`。
- **五十音**（`#/letters`，首頁「下一站」下面的入口格；`js/letters.js` 與韓文版共用）：平假名 9 課（含促音・長音對照）、片假名 6 課（含外來語特殊音）、全表；
  每個假名有例字（字卡裡挑、播字卡原本的音檔）、每課有重點說明；練習三種題型（聽音選字、看字選拼音、平假名選片假名），八成以上算學完（`store.letters`）。
- **音檔**：一律把**假名**送給語音服務（數字、日期給漢字會念錯）；單一假名放慢到 -55%（量過：正常語速「し」有聲段只有 50ms，會變氣音）。
  `audio/c/`（專欄 409）、`audio/q/`（聽力 370）、`audio/l/`（五十音 134）共約 10 MB；`tools/make_extra_audio.py` 依 hash 只重做改過的。設定頁「離線使用」多一列可整批下載。
- **字型**：新文字多了 7 個字（゛゜ヂヅヲ…），新增 `tools/make_font.py` 重裁（字表＝工作區 `fonts/zenold/chars-all.txt`＋App 現在的文字）。
- e2e：檢查音檔齊全、量詞表有標色、五十音第一課練習全對會記成學完、數字聽力照答案填 10 題全對。

## 2026-10-02：站號章、家族色、一行字（v22）

使用者在 iPhone 上看 v21 後要求：
- **站號章**（首頁下一站、課程頁、字表的「必 10」方塊）改成配合新設計 → 染了家族色的小玻璃（`.badge`，字用家族深色），不再是實心色塊。
- **家族色**改成配合天色 → `tools/themes.py` 的 `PALETTES` 換成「一天的天色」日本傳統色：基本＝紺、交通＝浅葱、住宿＝山吹、飲食＝柿、購物＝紅梅、
  醫療緊急＝茜、觀光生活＝若竹、店員廣播＝藤（OKLCH 定色，五色由主色推算）；對比推算用的 `N1／N9／N8` 改成玻璃上的近似底色。標籤列的色點也改用家族線色。
- **一行字盡量不換行，可縮小字體** → `data-fit="最小字級"`＋app.js 的 `fitText()`（先還原、一次量、一次寫；MutationObserver、字型載完、轉向、展開路線時重算）；
  套在下一站站名（副標移到站名下方整行）、首頁統計列、課程頁標題與說明、路線站名、家族格名稱、字表的單字與中文、下一站卡片底下那行。縮到最小也放不下就維持原字級、平均換成兩行（v23）。
- 已知：iPhone 沒有內建中文宋體，中文內文會用系統黑體（Songti TC 只有 Mac 有）；要全明朝得另外打包中文襯線字型（使用者還沒要求）。

## 2026-10-01：整體改版「暮色玻璃」（v21）

使用者在四個試作中選 **D 的主題＋B 的字體**，分頁列保留滾球（配色與透明度照 D），開場重做。
- **天空**：`js/sky.js` 自寫的網格漸層著色器（效果參考 Paper Shaders 的 MeshGradient；五個色點漂移＋雜訊扭曲＋顆粒），
  淺色＝白天（空色、桃、藤、象牙）、深色＝傍晚（茜、藤、紺）。半解析度算圖、每秒 10 格（捲動或拖字卡時暫停 0.3 秒）、App 在背景時停、減少動態效果時只畫一格；
  不支援 WebGL 時用 CSS 漸層。切深淺色時天色 0.8 秒轉過去（`setSkyMode`）。
- **玻璃**：`css/app.css` 檔頭的變數整組換掉（`--glass`／`--glass-2`／`--glass-3`／`--edge`／`--shadow`…）；舊名 `--surface`／`--ground`／`--trunk` 指向新值。
  背景模糊只給大面板（下一站、三條線、清單、設定群組、字卡、答題卡、搜尋列、分頁列、底部按鈕區），小元件只用半透明，手機才不會卡。
  主按鈕＝墨色膠囊（`--cta`），主題家族色只留在路線章、站點、進度。下一站那格有流光邊框（kokonut 做法）。
- **字體**：Zen Old Mincho（OFL）500／900 兩個字重，裁切成 App＋字典用到的 4,717 字（各約 1.2 MB，`fonts/`，已放進 SW 預先快取）；
  `font-weight: 400–600` 對到 500、`700–900` 對到 900。中文內文仍是宋體；中文字型裡沒有的約 8% 介面字會退回系統明朝／宋體。
- **字卡**：單字、讀音、中文包在一片玻璃 `.face` 上，手指拖著走、放手超過 90px 甩出去換卡，不夠就彈回（app.js 的 touch 處理）。
- **分頁列**：底板改玻璃、內距 34px、四角 32px（接近膠囊）；球是玻璃珠（半透明白／紺＋高光＋模糊），圖示墨色。
- **開場**：`js/splash.js`＋`css/app.css` 末段。夜色→白天（傍晚）、太陽從下方升起經過玻璃磚、「旅」由模糊凝結、天亮後字轉墨色；
  約 1.7 秒，結束時 App 本體淡入（`html.splashing`），天空不換。`window.__tkSplashT` 是截圖測試用的時間掛鉤。
- 試作頁：<https://jeremyl861225.github.io/tabi-kotoba-test/tabi-kotoba/2026-10-01-redesign/>（已定案 D＋B 字體）。
- **收尾審查（2026-10-02，兩輪）**：第一輪 8 項全改（數字也用明朝不混系統字、傍晚色組改紺為主、徽章／深色線條／基本家族的對比、
  測驗頁拿掉題型小標改 `data-qtype`、凹口間隙、天空省電、字級、標籤列切邊）；第二輪 6 項解決，回歸 R1「家族色分不清」→
  基本家族改**石板灰藍 #566273**（`themes.py`），深色模式家族色用 `oklch(from …)` 把亮度拉到 ≥0.74（不支援時 color-mix 混白）；
  下一站流光邊改成**只繞一圈**。設計規格寫在 `DESIGN.md`（＋`.impeccable/design.json`）。
- **未解**：清單裡振假名的基字往右偏約 6px（ruby 置中問題，沒動）；Android／iPhone 實機效能（背景模糊＋WebGL）待測；
  桌機寬螢幕上球下方偶爾有 1px 灰點。

## 2026-10-01：分頁列球改深灰（v20）＋整體設計試作

- 分頁列的球：紅 → 深紅（v19，再沉進凹口：球心在上緣之下 5px、間隙 3px）→ **深灰**（v20，`--ball`／`--ball-deep`，深色模式用稍亮的灰）；選到的分頁名稱改墨色。
- 使用者問能不能整體換設計、點名 motion／shadergradient／kokonut ui／liquid-glass：用 impeccable 跑方向抽籤（seed be4917ea），做了四個方向的主畫面＋字卡（淺深色），
  放在測試站 <https://jeremyl861225.github.io/tabi-kotoba-test/tabi-kotoba/2026-10-01-redesign/>：
  A 站名牌（抽籤主打）、B 東海道五十三次（impeccable 首選）、C 乘車券（挑戰者融合）、D 暮色玻璃（Paper Shaders 網格漸層＋液態玻璃＋kokonut 便當格＋Motion）。
  **選定後**：整個 App 照該方向改（路線、字卡、測驗、不熟、設定、字典、開場），網頁字型要自己打包裁切才能離線，之後跑 impeccable 的收尾審查與 DESIGN.md。

## 2026-09-29：料理字庫擴充（v18 上線）

使用者要求：居酒屋用語、常見料理、酒品、懷石食材、生魚片壽司的魚貝類、蔬菜等，**約 600 字、混進現有三條線**（依常見程度分必備／常用／進階）。
- 清單是人工整理的 `workspace/.../build/expand/food.txt`（「@主題 線 站名」＋每行 寫法|讀音|中文|說明|p），`tools/pipeline/food_prep.py` 轉成 `food.json`、
  扣掉和既有字卡重複的 56 個（同寫法同讀音、或同讀音且一邊是假名；句型卡不算；行首「!」強制收，例：鯛 vs 泰國タイ）；`--groups` 依站名寫分組檔。
- **新主題 6 個**（`themes.py`，都屬飲食家族、同一個顏色）：IZ 居酒屋、DN 常見料理、SU 壽司與海鮮、SK 酒類、KS 懷石與和食、VG 蔬菜與調味料。
  沒有塞進既有的 FD／RS／DK 線，因為 3-FD 等擴充線已分好站、有人在上面累積進度。
- `build_extras.py` 收 food.json（`level` 空、`tier` 直接給，卡片不顯示日檢級數）；`select.py` 的料理站另外排、**平均插進整條線，原本各站的相對順序不變**
  （檢查過：既有 314 站成員與 4,479 張卡內容完全不變）。結果 595 張、40 站（お冷、玉子、柚子 在字典層級與既有卡相同，略過）。
- 編號照學習順序重排（新站插進去，後面的字號碼往後移），同 N3 擴充時的做法。
- 撰寫：`build/author/in-47…52.json`（PROMPT.md 末節「料理字庫卡」），兩個 Sonnet 代理各三批，約 20 分鐘；沒有刪卡、沒有改寫法。
- QA：真的寫錯 7 條寫進 `fix.json`（今年→ことし、何ですか→なん、祝い事→いわ、小さな→ちい、3本→ぼん、葱的例句用漢字、食欲→食慾；
  另把「美味しい」統一改假名 12 條）；其餘 59 條讀音誤報（量詞、連濁、お好み焼き）逐條看過寫進 `reading_ok.json`；`TW_OK` 加「郁干栖」（濃郁、干貝、一夜干、羊栖菜）。
- 發音：新增約 2,380 個音檔。`tts_check.py`（`TK_MIN_ID=4524` 只查新卡）＋`tts_alt.py` 找出 **26 張念錯**：
  單一漢字 鰤 蜆 鱸 鮑 鱧 丼（念どん）魬（語音服務念不出來）；多字 七味→ななみ、銀杏→いちょう、地魚→ちぎょ、牛カツ／牛すじ→うし、神戸牛→こうべうし、
  朝定食→ちょう、ゆず酒→ゆずざけ、大トロ→だいトロ、きな粉→きなこな、ラー油→ラーあぶら、豚汁→ぶたじる、合い挽き→あいひき、味玉→あじだま 等。
  這些冷門詞在**例句**裡也會念錯，新增 `build/author/tts_kana_ex.json`（[寫法, 讀音]），build_data 把例句朗讀文字裡的這些詞換成假名（丼除外：牛丼、天丼本來就念どん）；
  舊卡 0822 的例句「大トロ」因此重做，`sw.js` 的 `AUDIO_REDO.v18`。
- 句子卡「可以這樣回答」只給店員／廣播說的話（`rp`：LS 主題或「店員常說的話」站），旅客自己說的句子例句按鈕叫「例句」。
- 結果：**5,074 張、354 站**，qa 清零，e2e `--all-cards` 通過。

## 2026-09-29：使用者回報發音念錯＋介面四項（v16）

1. **北念成ほく、南念成なん**（音讀／訓讀）→ 不只這兩張。Sudachi 讀音跟字卡一樣時 build_data 會送漢字給語音，
   但 Edge 語音自己的判斷不同（單獨一個漢字常念成音讀）。`tools/tts_check.py` 對 3,289 張「送漢字」的單字卡各合成一份假名版比聲紋
   （MFCC＋DTW；同讀音同聲調會產生一模一樣的檔＝距離 0），`tools/tts_alt.py` 再把單一漢字的卡跟其他讀音比；
   找出 **102 張**念錯（魚→うお、卵→らん、町→ちょう、店→てん、下→げ、日→にち、君→くん、口→ぐち、辛い→からい、年月→ねんげつ…），
   寫進 `build/author/tts_kana.json`，build_data 改送假名，重做 204 個音檔。**加卡後要重跑這兩支。**
   - 陷阱：單獨一個假名（し、ひ、ち）女聲會念成氣音；市、氏、死、計、刑、語、碁、髪、神的漢字版本來就念對，保留漢字。
   - 例句與句子卡（有上下文）沒有做這項檢查。
   - `sw.js` 加 `AUDIO_REDO`：內容改過、網址沒變的音檔，新版啟用時從發音快取刪一次（v14 的 32 個與這次 102 個），否則手機會一直播舊檔。
     音檔快取沒有時上網抓改用 `cache: 'no-cache'`。
2. 單元測驗考完，底部主按鈕改成**下一站**（`stationAfter`：路線上緊接的那一站，首頁選了主題家族就在那一類裡往下）；非單元測驗仍是「再考一次」。
3. 字卡頁排序加**依編碼**（`browse.sort === 'no'`）。
4. **分頁列改成浮起來的紅球**（使用者給的參考圖）：`js/tabbar.js`。毛玻璃底板（`backdrop-filter`）用 `clip-path: path()` 裁出凹口，
   細框與高光用同一條 SVG 路徑；選到的分頁圖示升進球裡、名稱留在原位變紅；換分頁時球滑過去（380ms、不回彈、略微拉長），凹口每一格跟著重算；
   減少動態效果時直接跳到位。球是日の丸的紅（`--sun`），跟開場呼應。`--tb-space` 取代原本的 `--tabbar-h`。
5. 使用者提到 react-three-fiber、liquid-glass-js、liquid-logo、kokonut ui：前兩個與 kokonut 都需要 React／建置步驟或 html2canvas，
   沒有放進 App；liquid-logo（Paper Shaders 液態金屬）可以不用 React。比較頁放在測試站
   `tabi-kotoba/2026-09-29-liquid/`（開場 A 平面／B 金屬圓／C 金屬「旅」字；分頁列球 A 光澤／B 液態金屬），**等使用者選**。
7. **開場改成立體紅球**（v17，使用者指定）：`js/splash.js` 用 WebGL 片段著色器畫紅色球體，「旅」是球上的凹坑（字形高度圖＋法線擾動＋坑內陰影），
   一開始字在背面、房間昏暗 → 球轉到正面 → 左上一束光打上來、坑壁明暗讓字浮出 → 房間亮成 App 底色、淡出（約 1.95 秒＋淡出 0.4 秒，點一下跳過）。
   `index.html` 開頭先加 `gl-try` 讓第一格就是暗房；WebGL 失敗或減少動態效果時維持原本平面的日の丸開場。`window.__tkSplashT` 是截圖測試用的時間掛鉤。
   液態金屬開場的比較頁因此作廢（測試站 meta 已標註）。
6. 設定頁「關於」的字典說明改成中文釋義＋預錄發音（原本還寫英文釋義、手機語音）。

## 2026-09-25 晚：使用者回報四個問題（已修正上線 v14，commit 94d4252）

1. 句型卡「〜はありますか」女聲把は念成 ha → `build_data.particle_start`：〜拿掉後第一個字是は／へ改念 わ／え；重做 50 個音檔
2. 單元頁看不出學到哪 → `viewUnit` 左側進度線（學過打勾、目前＝繼續學習那張，淡彩底＋「目前」、自動捲到）
3. 字典字卡點不開、英文、沒聲音 →
   - `#/dict/<JMdict 編號>` 單字頁（`viewDictEntry`），例句裡有這個字的字卡也列出來；中文也能查字典
   - 發音：預錄 `audio/d/<編號>.mp3`（`tools/make_dict_audio.py`，Nanami 32 kbps，約 2.3 萬個，**產生中、分批上傳**；抓不到才用手機語音）
   - 中文釋義：`tools/pipeline/dict_zh_prep.py` 依詞頻切 46 檔（`build/dictzh/in-NN.tsv`，每檔 500），代理翻成 `out-NN.tsv`，
     人工修正 `fix.tsv`，`build_dict.py` 合併成 `z` 欄。**01 已上線；02–07 翻譯中（Haiku，每代理 3 檔）；08–46 未派**。還沒翻到的暫時顯示英文
   - 教訓：第一批 Haiku 代理「翻譯」是把英文轉小寫交差（整批作廢，放在 `bad-haiku/`）；RULES.md 加「絕對不可以」一節後，第二次的品質可用（約九成好）
4. 標音放錯字 → `rubytools.split_group_ruby`（一段標音跨好幾個詞時照詞切，全漢字的詞整段標、不逐字撐開字距；對不上 JmdictFurigana 的不切）；
   `phrase_ruby` 比對讀音時不管標點、數字也標音（修好 8 張整句疊一串的句子卡）；`insert_tildes`（〜 放回原位、讀音欄照寫法帶〜）
- 另外：數字＋量詞音變檢查 `counter_problems`（抓到「二十分」標成にじゅうふん）
- 做 hotfix 時用 `build/selection.before-n3.json` 暫時換掉 selection.json 跑 build_data（線上仍是 1,200 張），跑完換回 `selection.n3.json`

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
| `tools/tts_check.py`、`tools/tts_alt.py` | 找語音念錯讀音的卡（假名版／其他讀音 vs 漢字版比聲紋）→ `build/author/tts_kana.json` |
| `js/tabbar.js` | 分頁列：紅球與毛玻璃凹口的位置與動畫 |
| `js/splash.js` | 立體開場（WebGL 著色器） |
| `tools/build_dict.py` | 離線字典 `data/dict.json` |
| `tools/themes.py` | 22 條主題的色票與推算色 |
| `tools/make_icons.py` | App 圖示 |
| `tools/e2e.py` | Playwright 手機視窗驗收 |

Python 環境：`workspace/work/jp-travel-vocab/.venv`（fugashi、sudachipy full、wordfreq、fonttools、edge-tts、opencc、jaconv）。
撰寫規格：`build/author/PROMPT.md`；選字規格：`build/curate/RULES.md`。

## 若中斷，下一步

看上面第一個未勾的項目；中間產物都在 `~/Desktop/Claude code/workspace/work/jp-travel-vocab/`。
撰寫批次：`ls build/author/out-*` 看哪些已完成，未完成的重派代理（派工方式見 skill 的 agents.md，每 20 條寫一次檔）。
