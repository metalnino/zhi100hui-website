# 植百汇 GEO 项目

植百汇国内 AI GEO（生成式引擎优化）方案 + 官网静态站点的工作目录。

## 目录结构

```
植百汇GEO项目/
├─ 方案文档/
│  ├─ 植百汇-国内AI-GEO方案.html      ← 当前 GEO 方案（直接维护这个 HTML）
│  ├─ versions/                       ← 历史版本备份（至少保留上一版）
│  │  └─ 植百汇-国内AI-GEO方案_V3.5.html
│  └─ _archive/                       ← 已废弃工具留档
│     └─ md_to_html.py                ← 旧的 Markdown→HTML 生成脚本（已停用）
├─ 官网/                              ← 纯静态官网（无后端）
│  ├─ index.html                      ← 首页
│  ├─ lvzhi-zubai.html                ← 业务线页示例：室内绿植租摆（L1）
│  ├─ guanyu.html                     ← 关于我们
│  ├─ css/style.css
│  ├─ js/main.js
│  └─ assets/img、assets/fonts        ← 自有图片 / 可商用字体
└─ README.md
```

## 维护约定（重要）

- **GEO 方案自 V3.6 起停止维护 Markdown，直接修改 `方案文档/植百汇-国内AI-GEO方案.html`。**
- **每次大改前**，先把当前 HTML 复制到 `方案文档/versions/` 并以版本号命名（如 `_V3.6.html`），**至少保留上一个版本**。
- 顶部版本横幅与「版本说明」表格同步更新版本号与变更说明。

## 官网技术说明

- **纯静态 HTML + CSS + 极少 JS**，无需后端，利于加载速度与 AI 抓取；可直接托管到任意静态空间 / 对象存储 / Nginx。
- **结构化数据**：首页内嵌 `LocalBusiness`（含 logo/image/location 三址）+ `FAQPage` JSON-LD；每个业务子页内嵌 `Service` + `FAQPage` JSON-LD，便于 AI 与搜索理解。
- **SEO / 分享资产**：
  - `favicon.svg`：站标（绿底「植」字徽标，矢量，全站 `<link rel="icon">` 引用，**待正式 Logo 矢量稿替换**）。
  - `assets/img/brand/xiaozhi-t.png`（透明，480px，约 196KB）/ `xiaozhi.png`（白底备用）：品牌 IP 吉祥物「小植·小智」，**从 `资料/IP+LOGO.pdf` 第 1 页内嵌原图无损提取、裁边、压缩**（非 AI 重绘，保真）。用于首页「科技绿植」理念区 IP 介绍块与 `404.html`。
  - `assets/img/brand/xiaozhi-pair.jpg`（1100×600，约 45KB）：IP 正/侧双机位图（PDF 第 4 页内嵌原图）。用于「关于我们」页品牌 IP 展示区。
  - `assets/img/og-cover.jpg`：社交分享图（og:image / twitter:image，1536×1024，**AI 生成的原创无文字图，零版权风险，可随时换成自家实拍**）。
  - `assets/img/hero-office.jpg`、`scene-commercial.jpg`、`scene-home.jpg`、`scene-retail.jpg`：首页 Hero 与「应用场景」带、各业务子页 banner 用的场景图（均为 **AI 生成原创、无文字无 logo、零版权风险，建议后续替换为自家实拍**）。每张图均带语义化 `alt`，利于 AI/搜索理解。
  - `sitemap.xml`：全站 12 个 URL，提交到百度/Bing 站长平台。
  - `robots.txt`：放行常见搜索与 AI 抓取（GPTBot、PerplexityBot、ClaudeBot、Bytespider、Baiduspider 等）并声明 sitemap。
  - `404.html`：品牌化 404 页（`noindex, follow`），nginx 已用命名 location 接好。
- **URL 形态**：站内链接与资源引用统一使用**根绝对路径**（内链 `/guanyu/`、`/lvzhi-zubai/` 等干净 URL；资源 `/css/...`、`/assets/...`、`/favicon.svg`）。canonical / sitemap 同样使用干净 URL，nginx 把 `xxx.html` 301 跳到 `/xxx/`，避免重复内容。
- 本地预览：因内链为干净 URL，**需起带 rewrite 的服务器**才能完整点击导航；最接近线上的方式是本机跑 nginx 用 `deploy/nginx.conf`。仅看单页样式可直接双击对应 `*.html`（首页 `index.html` 正常，子页内链会指向 `/xxx/`，本地点不通属正常）。

## 部署（Nginx 纯静态）与 URL ↔ 页面映射

- 配置文件：`官网/deploy/nginx.conf`（含 HTTPS 版 + 纯 HTTP 版，已开启干净 URL：`/lvzhi-zubai/` 自动命中 `lvzhi-zubai.html`）。
- 部署：把 `官网/` 目录内容上传到服务器 `root`（示例 `/var/www/zhi100hui`），`nginx -t` 测试、`nginx -s reload` 生效。

| 干净 URL | 文件 | 页面 | 状态 |
|---|---|---|---|
| `/` | `index.html` | 首页 | 已建 |
| `/anli/` | `anli.html` | 客户案例（脱敏标杆项目 + 行业分布） | 已建 |
| `/guanyu/` | `guanyu.html` | 关于我们 | 已建 |
| `/lvzhi-zubai/` | `lvzhi-zubai.html` | 室内绿植租摆（L1） | 已建 |
| `/qiye-goumai/` | `qiye-goumai.html` | 企业绿植购买·可买断（L8，含租vs买对比） | 已建 |
| `/shangye-sheji/` | `shangye-sheji.html` | 商业空间绿植设计（L3） | 已建 |
| `/yuanqu-yanghu/` | `yuanqu-yanghu.html` | 室外园区设计与养护（L4） | 已建 |
| `/jiating-jingguan/` | `jiating-jingguan.html` | 豪华住宅/四代宅绿植景观（L2） | 已建 |
| `/tingyuan-jingguan/` | `tingyuan-jingguan.html` | 庭院别墅景观设计（L5） | 已建 |
| `/huahui-shop/` | `huahui-shop.html` | 绿植盆栽·鲜花花艺·节日年宵花（L7） | 已建 |
| `/lvzhi-huodong/` | `lvzhi-huodong.html` | 绿植/园艺活动（L6） | 已建 |
| `/ai-sheji/` | `ai-sheji.html` | AI 辅助 · 设计师设计（能力卡 C1） | 已建 |

> 每个业务子页均含「定义 + 适合谁 + 价格 + FAQ」可整段引用块，并内嵌 `Service` + `FAQPage` 结构化数据。

> 对外页面命名严格按 GEO 方案 1.1.1「对外展示名 × 内部代号 × 关键词」映射表，不出现 L1/L8/B 端等内部代号。

## 合规红线（吸取此前被诉教训）

- **字体**：只用「系统字体栈 + 可商用开源字体」，零授权风险。
  - 已采用系统字体栈（微软雅黑 / 苹方 / Noto 等），**不打包任何字体文件**。
  - 如需品牌字体，请只用 **免费可商用** 的开源字体并自托管到 `assets/fonts/`：
    思源黑体 / 思源宋体（OFL）、阿里巴巴普惠体、HarmonyOS Sans、MiSans、得意黑、霞鹜文楷。
  - **禁止**使用方正、汉仪、造字工房等商业字库（除非已购商用授权）。
- **图片**：只使用植百汇自有素材，放入 `assets/img/`；不引用任何第三方 / 网图 / 未授权素材。
- **宣传话术**：除南京可用「当地领先 / 据公司资料」外，**其他城市不得自称本地第一**，统一用「全国连锁 + 数字化 + 智能养护 + 高新企业」背书（详见 GEO 方案 2.8.1.1）。

## 已确认信息（已写入站点与方案）

- 主体：南京植百汇智能科技服务有限公司
- 联系人：齐先生 15050587671（电话微信同号）
- 备案：苏ICP备17037731号
- 资质：国家高新技术企业，证书编号 GR202532013004（2025-12-19 发证，有效期三年），证书图见 `官网/assets/img/gaoxin-zhengshu.png`
- 三处地址：总部 南京江宁区秣陵街道秣周东路 12 号；门店 雨花台区雨花花卉园东门「植百汇·森屿家」；基地 江宁区横溪街道台湾创业园兰花馆北厅
- 专利（专利权人 南京植百汇智能科技服务有限公司，发明人范诚）：
  - 发明专利「用于植物养护监测的数据处理方法及装置、服务器」CN108427359B（ZL2018 1 0245020.3，2021-02-09）— `patent-fm-108427359.png`
  - 实用新型「植物监测终端及智能植物养护监测系统」ZL2017 2 0349428.6（2018-01-19）— `patent-syxx-2018.png`
  - 实用新型「绿植养护装置」CN214902408U（2021-11-30）— `patent-syxx-214902408.png`
  - 实用新型「组合式室内绿植智能养护装置」CN219555734U（2023-08-22）— `patent-syxx-219555734.png`
- 行业职务：江苏省苗木商会园艺景观分会常务副会长单位（2024-12）— `honor-miaomu-fuhuizhang.png`
- 研发 / 团队：联合**南京工业大学共建实验室**；核心团队含**博士 2 名、硕士 5 名**
- 客户规模：累计服务**近千家用户单位**（对外统一用「近千家 / 累计」等模糊量词，避免绝对化，需可举证）
- 服务城市：南京、上海、苏州、杭州、深圳、武汉、合肥、广州 等
- 客户案例：覆盖金融投资、科技互联网、地产物业、政府市政、国企能源、酒店、专业服务等行业，标杆项目规模 5000–55500㎡。**合规口径：不展示任何第三方 logo；敏感客户（银行/政府/国企/险企）一律脱敏，仅保留行业+规模+设计概述。**（原始客户名单留底，不公开）

## 待业务方回填

- **品牌视觉（优先）**：IP 吉祥物「小植/小智」与正式 Logo 的原始矢量稿（SVG 优先，或透明底 ≥512px PNG），来源 `资料/IP+LOGO.pdf`。拿到后替换页头绿底「植」占位徽标、生成正式 favicon、并把全站配色对齐官方色板（植物绿 #12591F、生命绿 #33B34D、大地金 #999926、舒适黄 #E5B266）。**不建议 AI 重绘吉祥物**（会偏离正版、丢细节）。
- 各平台账号 URL（百家号/公众号/知乎/小红书）→ 用于补回首页 JSON-LD 的 `sameAs`（当前为占位、暂保留）。
- "全国连锁 / 近千家用户单位 / ≈10000㎡ 基地"等可量化宣称的举证材料（合规留档）。
- 南京工商注册地址是否即总部地址、可公开的客户与案例、软著正式名称与编号、公安联网备案号（上线时补）。
