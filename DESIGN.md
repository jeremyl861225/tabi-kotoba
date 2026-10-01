---
name: 旅ことば
description: 在日本旅行用的單字路線 App：一整天的天色上浮著液態玻璃，明朝體的字是主角。
colors:
  ink: "#18203a"
  ink-2: "#39436a"
  ink-3: "#59628a"
  glass: "rgb(255 255 255 / 0.42)"
  glass-2: "rgb(255 255 255 / 0.28)"
  glass-3: "rgb(255 255 255 / 0.7)"
  edge: "rgb(255 255 255 / 0.66)"
  edge-2: "rgb(255 255 255 / 0.36)"
  hair: "rgb(24 32 58 / 0.1)"
  track: "rgb(24 32 58 / 0.13)"
  cta: "#18203a"
  cta-ink: "#ffffff"
  ok: "#1d7748"
  ng: "#b1372f"
  gold: "#a87407"
  badge: "#edb83a"
  sky-base: "#bcd3ee"
  sky-day-1: "#a9cdee"
  sky-day-2: "#f3bcb0"
  sky-day-3: "#c8b6e6"
  sky-day-4: "#f6efe8"
  sky-day-5: "#86aee0"
  dusk-ink: "#fbf7ff"
  dusk-ink-2: "#dbd4ee"
  dusk-ink-3: "#afa7cb"
  dusk-glass: "rgb(18 26 64 / 0.42)"
  dusk-sky-base: "#161d42"
  dusk-1: "#c4613f"
  dusk-2: "#3a3c86"
  dusk-3: "#101842"
  dusk-4: "#16234f"
  dusk-5: "#24357a"
  fam-basic: "#566273"
  fam-move: "#167793"
  fam-stay: "#9a526c"
  fam-food: "#a4613a"
  fam-shop: "#875a93"
  fam-care: "#9c534c"
  fam-city: "#367d5b"
  fam-listen: "#6e61a0"
typography:
  display:
    fontFamily: "Zen Old Mincho, Hiragino Mincho ProN, YuMincho, Noto Serif JP, Songti TC, serif"
    fontSize: "clamp(40px, 26vw, 104px)"
    fontWeight: 900
    lineHeight: 1.3
    letterSpacing: "0.02em"
  headline:
    fontFamily: "Zen Old Mincho, Hiragino Mincho ProN, Songti TC, Noto Serif TC, serif"
    fontSize: "40px"
    fontWeight: 900
    lineHeight: 1.2
    letterSpacing: "0.02em"
  title:
    fontFamily: "Zen Old Mincho, Hiragino Mincho ProN, Songti TC, Noto Serif TC, serif"
    fontSize: "23px"
    fontWeight: 900
  body:
    fontFamily: "Songti TC, Noto Serif TC, Noto Serif CJK TC, Source Han Serif TC, PMingLiU, serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.55
    fontFeature: "tnum"
  label:
    fontFamily: "Zen Old Mincho, Hiragino Mincho ProN, Songti TC, serif"
    fontSize: "12.5px"
    fontWeight: 500
rounded:
  tile: "20px"
  fam: "18px"
  panel: "26px"
  card: "30px"
  pill: "999px"
spacing:
  gutter: "18px"
  panel-pad: "18px"
  grid-gap: "8px"
  tabbar-h: "64px"
components:
  button-primary:
    backgroundColor: "{colors.cta}"
    textColor: "{colors.cta-ink}"
    rounded: "{rounded.pill}"
    padding: "0 22px"
    height: "52px"
  button-ghost:
    backgroundColor: "{colors.glass}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "0 22px"
    height: "52px"
  panel:
    backgroundColor: "{colors.glass}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "18px"
  card-face:
    backgroundColor: "{colors.glass}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
    padding: "30px 16px 22px"
  chip:
    backgroundColor: "{colors.glass-2}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "0 15px"
    height: "38px"
  chip-selected:
    backgroundColor: "{colors.cta}"
    textColor: "{colors.cta-ink}"
    rounded: "{rounded.pill}"
  family-tile:
    backgroundColor: "{colors.glass-2}"
    textColor: "{colors.ink}"
    rounded: "{rounded.fam}"
    padding: "6px 4px"
  search-field:
    backgroundColor: "{colors.glass-3}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
  tabbar:
    backgroundColor: "{colors.glass}"
    textColor: "{colors.ink-3}"
    height: "64px"
---

# Design System: 旅ことば

## Overview

**Creative North Star: "暮色玻璃（在日本看一整天的天色）"**

背景是一片會慢慢流動的天空：淺色模式是白天（淡藍、桃、藤、象牙），深色模式是傍晚（紺為主，藤與茜是色團）。所有內容都浮在液態玻璃上：半透明、背景模糊、上緣一道細高光。玻璃本身沒有顏色，顏色全部來自後面的天空，所以整個 App 只有兩種表面：天空和玻璃。

字是主角。日文、標題、數字、小標籤全部用 Zen Old Mincho（禪舊明朝），中文內文用宋體；畫面上不出現無襯線字。單字卡的大字最大到 104px、字重 900，路線圖的「下一站」站名 40px。資訊密度是「一次一件事」：首頁只有下一站、路線家族、路線清單；字卡頁一張卡一個字。

動態只放在兩個地方：天空（每秒 10 格、捲動時暫停）和分頁列的玻璃球（選分頁時滾過去）。其他都是 0.12–0.42 秒的按壓或回彈，不擋操作。

**Key Characteristics:**
- 兩種表面：流動的天空（WebGL 網格漸層）＋液態玻璃面板
- 全明朝：Zen Old Mincho 500／900 子集＋系統宋體
- 墨色按鈕（淺色）／月白按鈕（深色）是唯一的實心色塊
- 路線家族的八個顏色只出現在小色點、路線線條與完成標記
- 分頁列是有凹口的玻璃板，玻璃球沉在凹口裡、滾到選中的分頁

## Colors

色彩全部來自天空，介面本身只有墨色、玻璃白與八個路線家族色。

### Primary
- **夜墨** (ink / cta)：淺色模式所有正文與實心按鈕（開始、發音、下一站的「出發」）。深色模式換成 **月白** (dusk-ink)，按鈕字變成深紺。

### Secondary
- **路線家族色**（fam-basic 石板灰藍、fam-move 鐵道青、fam-stay 紅豆、fam-food 醬油、fam-shop 藤紫、fam-care 柿紅、fam-city 松葉、fam-listen 桔梗）：只用在色點、路線圖的線、站點完成標記。深色模式下用 oklch 相對色把亮度拉到 ≥0.74、彩度 ≥0.07（不支援時用 color-mix 混白）。

### Tertiary
- **徽章金** (badge)：分頁列上的待複習數字徽章，墨色字。
- **對／錯** (ok／ng)：測驗回饋；深色模式換成亮綠與珊瑚。

### Neutral
- **白天天色** (sky-day-1…5)：WebGL 天空的五個色點；不支援 WebGL 時改成 CSS 放射漸層。sky-base 是瀏覽器頂欄與 PWA 啟動色。
- **傍晚天色** (dusk-1…5)：深色模式的天空；dusk-sky-base 是頂欄色。
- **玻璃** (glass／glass-2／glass-3)：面板、面板裡的小元件、浮在內容上的元件（搜尋列、提示、答題選項）。深色模式下面板是紺玻璃 rgb(18 26 64 / .42)。
- **玻璃邊** (edge／edge-2)：上緣高光與 1px 細邊，用 inset box-shadow 畫。
- **髮線與軌道** (hair／track)：分隔線、路線圖未走過的軌道。

### Named Rules
**The 天空上色 Rule.** 介面元件不自己帶底色；要顏色就讓天空透過玻璃。唯一的實心色塊是 CTA（夜墨／月白）。

**The 家族色只當記號 Rule.** 八個路線家族色只出現在 10–11px 色點、2px 線條與站點記號，不鋪大面積、不當文字色（深色模式的站名除外，且經過亮度補償）。

## Typography

**Display Font:** Zen Old Mincho 900（子集 woff2，備援 Hiragino Mincho ProN、Yu Mincho、Noto Serif JP）
**Body Font:** Songti TC（備援 Noto Serif TC、PMingLiU）
**Label/Mono Font:** Zen Old Mincho 500（數字、編號、小標籤）

**Character:** 一整套明朝：日文用禪舊明朝的粗筆，中文用宋體，兩者都是有筆鋒的襯線字，像車站木牌上的字。數字一律等寬 (tabular-nums)。

### Hierarchy
- **Display** (900, 依字數自動縮放、上限 104px, 1.3)：字卡的大字，假名標音 0.34em。
- **Headline** (900, 40px, 1.2)：首頁「下一站」站名。
- **Title** (900, 23px)：路線分級標題；路線家族名 16px／700。
- **Body** (400, 16px, 1.55)：中文內文；字卡中文意思 24px／600。
- **Label** (500, 11–14px)：編號、站數、羅馬拼音 (16px)、分頁名稱 (11px／700)。

### Named Rules
**The 不混字 Rule.** 畫面上只有明朝與宋體兩種字；系統無襯線字（-apple-system、PingFang）不進 UI。字型檔只有兩個字重：400–600 都對到 500 檔，700–900 都對到 900 檔。

## Layout

單欄，最大寬度 560px，左右 18px。底部保留分頁列的空間（64px 板高＋球突出的 19px＋安全區）。首頁從上到下：下一站面板、3×3 路線家族格（間距 8px）、可展開的路線分級面板。字卡頁：卡面置中、下面是發音按鈕列、最底是固定的上一張／下一張列。標籤列 (chips) 橫向捲動，延伸到螢幕邊緣並用遮罩淡出。

## Elevation & Depth

深度靠「玻璃＋背景模糊」而不是陰影堆疊。每塊玻璃都是同一組：背景模糊 22px＋飽和 1.6、上緣 1px 白色高光、1px 白色細邊，以及一道很淡、往下偏移的環境陰影。浮在內容上的元件（搜尋列、提示、底部操作列）用更不透明的 glass-3。

### Shadow Vocabulary
- **玻璃面板** (`box-shadow: inset 0 1px 0 var(--edge), inset 0 0 0 1px var(--edge-2), 0 18px 34px -24px var(--shade)`)：所有面板、卡面、提示。
- **玻璃小元件** (`box-shadow: inset 0 1px 0 var(--edge), inset 0 0 0 1px var(--edge-2)`)：chip、家族格、目前的單字列（不帶外陰影）。
- **玻璃球** (`inset 0 1px 1px rgb(255 255 255 / .8), inset 0 0 0 1px var(--edge-2), inset 0 -3px 6px rgb(255 255 255 / .18), 0 10px 18px -10px var(--shade)`)：分頁列的球，加兩道放射漸層的鏡面高光。

### Named Rules
**The 一層玻璃 Rule.** 玻璃不疊玻璃超過兩層（面板＋裡面的小元件）。第三層一律改成實心 CTA 或純文字。

## Shapes

全部是大圓角，沒有直角：膠囊按鈕與 chip (999px)、小磚 20px、家族格 18px、面板 26px、字卡 30px、開場的玻璃磚 30%。圓點與色點是正圓。分頁列是 32px 圓角的板子，上緣挖一個帶 9px 圓角過渡的凹口，球（48px）沉在凹口裡、球心在板緣下 5px、與凹口間隙 3px。

## Components

### Buttons
- **Shape:** 膠囊 (999px)，高 52px（小號 40px、發音鈕 50px、出發鈕 46px）。
- **Primary:** 夜墨底、白字（深色模式月白底、深紺字），600 字重。
- **Hover / Focus:** 按下縮到 0.96–0.97（0.12 秒）；鍵盤焦點是 2px 墨色外框、間距 3px。
- **Ghost:** 玻璃底＋玻璃陰影、墨色字。

### Chips
- **Style:** glass-2 底、1px 玻璃邊、14px／500。
- **State:** 選中時變成實心 CTA；色點加一圈 CTA 字色的外環。

### Cards / Containers
- **Corner Style:** 面板 26px、字卡 30px。
- **Background:** glass。
- **Shadow Strategy:** 玻璃面板（見 Elevation）。
- **Internal Padding:** 18px；字卡上方留 30px 給左上角的編號。
- **字卡拖曳:** 水平拖動時卡面跟著手指平移並微傾；超過 90px 或快速甩動就飛出、換下一張；不夠就以 0.42 秒帶一點回彈彈回。

### Inputs / Fields
- **Style:** glass-3 膠囊、17px 字。
- **Focus:** 內框 1.5px 墨色。

### Navigation
- **分頁列:** 五個分頁，明朝 11px／700，未選中為 ink-3。底板是玻璃（模糊 24px）、SVG 畫細邊與上緣高光。選中的分頁圖示升到球心、換成 ball-ink；切換時球沿板緣滾過去（380ms），凹口跟著移動。待複習數字是金色徽章。

### 下一站面板（signature）
首頁最上方的玻璃面板，站名 40px／900。進場時一圈白色流光沿邊框繞一圈（2.4 秒、只跑一次）後停住。

### 開場（signature）
約 1.7 秒：天空從夜色轉成白天（深色模式轉成傍晚），一團暖光從畫面下方升起、在中央散開；一塊玻璃磚凝結，「旅」與「旅ことば」浮現，天亮後字轉成墨色。開場結束時天空不換，App 直接淡入在同一片天空上。點一下可跳過；減少動態效果時不播。

## Do's and Don'ts

### Do:
- **Do** 讓所有表面都是玻璃（glass／glass-2／glass-3＋背景模糊＋上緣高光），顏色交給天空。
- **Do** 所有字都用 Zen Old Mincho 或宋體；數字等寬。
- **Do** 實心色塊只給 CTA（夜墨／月白）。
- **Do** 深色模式的家族色經過亮度補償（oklch l ≥ 0.74）。
- **Do** 天空在捲動、拖曳、背景時暫停；減少動態效果時只畫一格。

### Don't:
- **Don't** 回到米色紙、平面卡片清單的舊樣式（2026-10-01 使用者選定暮色玻璃後淘汰）。
- **Don't** 在 UI 用系統無襯線字。
- **Don't** 用路線家族色鋪大面積或當正文色。
- **Don't** 讓動畫一直重畫（流光邊只跑一圈；天空每秒最多 10 格）。
- **Don't** 把分頁列換成一般的底部導覽；玻璃球滾動是使用者指定保留的。
