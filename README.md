# 旅ことば Tabi Kotoba

日本旅遊日文單字卡，手機 PWA，可離線使用。<https://jeremyl861225.github.io/tabi-kotoba/>

- 約 1200 個旅途會用到的單字與常用句：機場入境、電車、巴士計程車、自駕加油、住宿溫泉、餐廳料理、購物、便利商店、藥妝就醫、緊急求助、招牌標示，以及店員與廣播常對旅客說的話。
- 每張字卡：漢字上方標假名、發音（女聲 Nanami／男聲 Keita 交替）、旅途情境例句與中文。
- 依「旅遊實用頻率」排序，分必備、常用、進階三級，級內依主題分課；每課可學習與測驗。
- 測驗八種題型：看日文選中文、看中文選日文、看漢字選讀音、聽發音選單字、聽發音選中文、聽例句選意思、用假名方塊拼出讀音、聽寫。
- 星號標記不熟的字，另有專區複習與測驗；可依等級、主題、漢字、假名、羅馬拼音或中文搜尋，字卡以外的字查離線字典。

## 旅遊實用頻率怎麼算

把多份中、日、英文旅遊日語教材的詞表合併，同一個詞（不同寫法對到同一個字典詞條）被幾份收錄就是它的收錄數；收錄數越多排越前面，同分時再看一般日語語料庫的使用頻率（[wordfreq](https://github.com/rspeer/wordfreq)）。來源清單列在 App 的「設定 → 關於」。

## 資料與授權

- 讀音與標音校對：[JMdict](https://www.edrdg.org/jmdict/j_jmdict.html)（EDRDG，CC BY-SA 4.0）、[JmdictFurigana](https://github.com/Doublevil/JmdictFurigana)、SudachiPy。
- 離線字典：JMdict 常用詞（約 2.2 萬詞，CC BY-SA 4.0），`data/dict.json` 沿用同授權。
- 日檢 N5–N3 擴充單字與級數：[open-anki-jlpt-decks](https://github.com/jamsinclair/open-anki-jlpt-decks)（MIT，資料源自 [tanos.co.uk](http://www.tanos.co.uk/jlpt/) 的日檢單字表）。
- 字型：使用裝置內建的明朝體與宋體，不隨 App 發佈字型檔。
- 發音：Microsoft 神經語音 Nanami、Keita，以 [edge-tts](https://github.com/rany2/edge-tts) 產生，僅供個人學習。
- 例句與中文解釋由 AI 撰寫，經字典與形態素分析器比對讀音；如有錯誤歡迎回報。
- 程式碼與字卡內容 © 2026 jeremyl861225。

## 重建資料

原始教材詞表有著作權，不放在 repo；管線程式在 `tools/`，說明見 `HANDOFF.md`。

```
tools/pipeline/normalize.py   # 來源 → 詞條與收錄數
tools/pipeline/auto_curate.py # 選字代理沒做完的部分用規則補完
tools/pipeline/select.py      # 排名、分級、分課
tools/pipeline/author_prep.py # 切撰寫批次
tools/build_data.py           # 組 data/cards.json＋檢查
tools/make_audio.py           # 產生發音
tools/build_dict.py           # 離線字典
tools/e2e.py                  # 手機視窗端對端驗收
```
