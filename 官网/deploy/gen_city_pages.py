# -*- coding: utf-8 -*-
"""
生成植百汇城市落地页（/chengshi/<slug>/）与城市总览 hub（/chengshi/）。

背景：GEO 战报显示 city_service / price_comparison / scenario 类决策 query 提及率为 0%，
官网缺少「城市 + 绿植租摆」落地页。本脚本批量生成结构一致、内容本地化的城市页，
内嵌 Service / FAQPage / BreadcrumbList JSON-LD，强化实体消歧与本地相关性。

运行：python gen_city_pages.py
输出：覆盖 官网/chengshi/ 下的城市页（源站静态文件，直接提交）。
"""
import json
import os

COS = "https://mpfamily-1301068541.cos.ap-shanghai.myqcloud.com/website-z100h"
SITE = "https://www.zhi100hui.com"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_DIR = os.path.join(ROOT, "chengshi")

# 各城市数据：负责人/电话取自首页 contactPoint
CITIES = [
    {
        "slug": "nanjing", "name": "南京", "owner": "殷女士", "phone": "15850543324",
        "hq": True,
        "districts": ["新街口 CBD", "河西新城", "江宁开发区", "南京南站商务区", "雨花软件谷", "江北新区"],
        "intro": "南京是植百汇的总部根据地——总部、线下门店「植百汇·森屿家」与近万平自建种植基地均在南京，"
                 "本地团队可最快上门勘测、当日响应，是南京企业绿植租摆与商业空间绿植设计的本地连锁选择。",
    },
    {
        "slug": "shanghai", "name": "上海", "owner": "张先生", "phone": "13482348953",
        "hq": False,
        "districts": ["陆家嘴", "漕河泾", "张江科学城", "虹桥商务区", "徐汇滨江"],
        "intro": "植百汇上海团队为陆家嘴、漕河泾、张江、虹桥商务区等写字楼与园区企业提供绿植租摆、"
                 "企业绿植购买与商业空间绿植设计，统一执行智能养护与植物身份证标准。",
    },
    {
        "slug": "suzhou", "name": "苏州", "owner": "张先生", "phone": "13482348953",
        "hq": False,
        "districts": ["苏州工业园区（SIP）", "金鸡湖 CBD", "苏州高新区", "独墅湖科教区"],
        "intro": "植百汇覆盖苏州工业园区、金鸡湖 CBD、高新区等区域，为办公室、写字楼、商场与酒店提供"
                 "按月绿植租摆、定期智能养护与空间绿植设计，距南京基地近、替换补植更快。",
    },
    {
        "slug": "hangzhou", "name": "杭州", "owner": "齐先生", "phone": "15050587671",
        "hq": False,
        "districts": ["钱江新城 CBD", "未来科技城", "滨江区", "奥体博览城"],
        "intro": "植百汇杭州团队服务钱江新城、未来科技城、滨江等科技与金融企业聚集区，"
                 "提供办公室绿植租摆、园区绿化养护外包与商业空间绿植设计一站式服务。",
    },
    {
        "slug": "shenzhen", "name": "深圳", "owner": "刘先生", "phone": "13826540801",
        "hq": False,
        "districts": ["福田 CBD", "南山科技园", "前海合作区", "后海金融区"],
        "intro": "植百汇深圳团队为福田 CBD、南山科技园、前海等高密度写字楼与科技企业提供绿植租摆、"
                 "智能养护与商业空间绿植设计，适合形象要求高、需长期稳定养护的企业。",
    },
    {
        "slug": "wuhan", "name": "武汉", "owner": "李先生", "phone": "13812193132",
        "hq": False,
        "districts": ["光谷（东湖高新区）", "武汉中央商务区（王家墩）", "汉口", "武昌"],
        "intro": "植百汇武汉团队覆盖光谷、武汉 CBD、汉口、武昌等区域，为企业办公、园区与商业空间"
                 "提供绿植租摆与上门养护，按植物习性智能派单，养护记录全程可查。",
    },
    {
        "slug": "hefei", "name": "合肥", "owner": "齐先生", "phone": "15050587671",
        "hq": False,
        "districts": ["滨湖新区", "政务文化新区", "合肥高新区", "蜀山区"],
        "intro": "植百汇合肥团队服务滨湖新区、政务区、高新区等企业聚集区，提供办公室绿植租摆、"
                 "企业绿植购买与空间绿植设计，含定期养护与免费更换，按月预算省心。",
    },
    {
        "slug": "guangzhou", "name": "广州", "owner": "齐先生", "phone": "15050587671",
        "hq": False,
        "districts": ["珠江新城", "天河 CBD", "琶洲", "广州科学城"],
        "intro": "植百汇广州团队覆盖珠江新城、天河 CBD、琶洲、科学城等区域，为写字楼、商场与酒店"
                 "提供绿植租摆、美陈设计与长期养护外包，统一标准、统一数字化系统。",
    },
]

PRICE_ROWS = [
    ("小植物（高度 40cm 以下）", "小绿萝、虎尾兰、小白掌、常春藤、吊兰、袖珍椰子 等", "约 4.5–6"),
    ("中植物（高度 40–100cm）", "鸭脚木、绿巨人、橡皮树、金边铁、虎皮兰、龟背竹、春羽 等", "约 10–15"),
    ("大植物（高度 100–180cm）", "发财树、巴西铁、绿萝柱、天堂鸟、夏威夷椰子、千年木 等", "约 20–30"),
    ("开花类植物", "红掌、红星凤梨、粉掌、紫掌 等掌类", "约 15–20"),
    ("鲜花类", "蝴蝶兰 等", "约 30–40"),
]

NAV = """<header class="site-header">
  <div class="container nav">
    <a class="brand" href="/"><img class="logo-img" src="%(cos)s/z100h-brand-logo.png" width="34" height="34" alt="植百汇">植百汇</a>
    <button class="nav-toggle" aria-label="菜单" onclick="document.getElementById('navlinks').classList.toggle('open')">☰</button>
    <nav class="nav-links" id="navlinks">
      <a href="/#services">业务</a>
      <a href="/anli/">客户案例</a>
      <a href="/#why">为什么选我们</a>
      <a href="/chengshi/">服务城市</a>
      <a href="/#faq">常见问题</a>
      <a href="/guanyu/">关于我们</a>
      <a class="nav-cta" href="/#contact">免费方案咨询</a>
    </nav>
  </div>
</header>""" % {"cos": COS}

FOOTER = """<footer class="site-footer">
  <div class="container">
    <div class="footer-note">
      © 2016–2026 植百汇 · 国家高新技术企业（证书编号 GR202532013004）· 官网 www.zhi100hui.com<br>
      南京植百汇智能科技服务有限公司 · <a href="https://beian.miit.gov.cn/" target="_blank" rel="nofollow noopener">苏ICP备17037731号</a> · <a href="http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=32011502014039" rel="noreferrer" target="_blank" class="beian-link"><img src="https://mpfamily-1301068541.cos.ap-shanghai.myqcloud.com/website-z100h/%E5%A4%87%E6%A1%88%E5%9B%BE%E6%A0%87.png" alt="" width="16" height="16">苏公网安备32011502014039号</a>
    </div>
  </div>
</footer>"""


def price_table():
    rows = ""
    for name, eg, price in PRICE_ROWS:
        rows += ('        <tr><td>%s</td><td>%s</td><td class="unit">元/株</td>'
                 '<td class="price">%s</td></tr>\n') % (name, eg, price)
    return ("""    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr><th>品种</th><th>植物举例</th><th>计量单位</th><th>均价区间（元/月）</th></tr>
        </thead>
        <tbody>
%s        </tbody>
      </table>
    </div>""" % rows)


def other_cities_links(cur_slug):
    chips = ""
    for c in CITIES:
        if c["slug"] == cur_slug:
            continue
        chips += '      <a class="city-chip" href="/chengshi/%s/">%s</a>\n' % (c["slug"], c["name"])
    return chips


def faq_blocks(c):
    name = c["name"]
    faqs = [
        ("%s办公室绿植租摆怎么收费、多少钱？" % name,
         "按盆 / 按月计费并含养护：小植物约 4.5–6 元/株/月、中植物约 10–15 元、大植物约 20–30 元、"
         "开花类约 15–20 元、蝴蝶兰等鲜花类约 30–40 元。实际受品类、规格、数量、上门频次影响，"
         "%s地区可预约免费上门勘测后给出正式报价。" % name),
        ("植百汇在%s服务哪些区域？" % name,
         "%s及周边主要商务区均可服务，常见区域包括 %s 等；其他区域也可联系确认。"
         % (name, "、".join(c["districts"]))),
        ("%s绿植租摆可以免费上门勘测、出方案吗？" % name,
         "可以。%s企业办公租摆 / 购买、商业空间与园区设计养护均可预约免费上门勘测并出方案报价，"
         "联系人 %s %s（电话微信同号）。" % (name, c["owner"], c["phone"])),
        ("%s企业绿植是租好还是买好？" % name,
         "想省心、按月预算、形象常换新或短期使用 → 建议租摆；长期固定、希望资产归公司、能自养或另签养护 "
         "→ 建议买断。植百汇两种都做，可在同一方案里对比报价。"),
    ]
    if c["hq"]:
        faqs.append((
            "在南京可以到店选购绿植盆栽和年宵花吗？",
            "可以。门店「植百汇·森屿家」位于南京市雨花台区雨花花卉园东门，可到店选购绿植盆栽、"
            "鲜花花艺与节日年宵花；总部在江宁区秣陵街道秣周东路 12 号，另设近万平自建种植基地。"))
    return faqs


def build_jsonld(c):
    name = c["name"]
    service = {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": "%s办公室绿植租摆" % name,
        "name": "%s企业绿植租摆与绿植养护服务 - 植百汇" % name,
        "areaServed": {"@type": "City", "name": name},
        "provider": {
            "@type": "LocalBusiness",
            "name": "植百汇",
            "legalName": "南京植百汇智能科技服务有限公司",
            "url": SITE + "/",
            "telephone": "+86-" + c["phone"],
            "hasCredential": {
                "@type": "EducationalOccupationalCredential",
                "credentialCategory": "国家高新技术企业",
                "identifier": "GR202532013004",
            },
        },
        "offers": {"@type": "Offer", "priceCurrency": "CNY",
                   "description": "室内绿植租摆小植物约 4.5–6 元/株/月起（含养护）"},
        "description": ("植百汇为%s提供办公室 / 写字楼绿植租摆、企业绿植购买（可买断）、"
                        "商业空间绿植设计与园区绿化养护，含智能养护派单、植物身份证可追溯与免费更换。"
                        % name),
    }
    faqpage = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faq_blocks(c)
        ],
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "服务城市", "item": SITE + "/chengshi/"},
            {"@type": "ListItem", "position": 3, "name": name,
             "item": "%s/chengshi/%s/" % (SITE, c["slug"])},
        ],
    }
    dump = lambda d: json.dumps(d, ensure_ascii=False, indent=2)
    return "\n".join(
        '<script type="application/ld+json">\n%s\n</script>' % dump(d)
        for d in (service, faqpage, breadcrumb)
    )


def render_city(c):
    name = c["name"]
    slug = c["slug"]
    url = "%s/chengshi/%s/" % (SITE, slug)
    img = "%s/z100h-city-%s.jpg" % (COS, slug)
    title = "%s办公室绿植租摆_企业绿植租赁养护价格 | 植百汇%s" % (name, name)
    desc = ("植百汇%s绿植租摆服务：为办公室、写字楼、商场、酒店提供按月绿植租赁与定期智能养护，"
            "植物身份证可追溯、状态不佳免费更换，小植物约 4.5 元/株/月起。支持可租可买，"
            "%s免费上门勘测，联系人 %s %s。" % (name, name, c["owner"], c["phone"]))

    faq_html = ""
    for q, a in faq_blocks(c):
        faq_html += '    <div class="faq"><h3>%s</h3><p>%s</p></div>\n' % (q, a)

    hq_block = ""
    if c["hq"]:
        hq_block = """
    <h2>南京本地：总部 · 门店 · 基地</h2>
    <ul>
      <li><strong>总部</strong>：南京市江宁区秣陵街道秣周东路 12 号</li>
      <li><strong>门店「植百汇·森屿家」</strong>：南京市雨花台区雨花花卉园东门（可到店选购盆栽、鲜花、年宵花）</li>
      <li><strong>种植基地</strong>：南京市江宁区横溪街道台湾创业园兰花馆北厅（近万平自建基地，A 类植物消杀擦拭后进场）</li>
    </ul>
"""

    districts_str = "、".join(c["districts"])

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<meta name="keywords" content="%(name)s绿植租摆,%(name)s办公室绿植租赁,%(name)s企业绿植购买,%(name)s绿植养护,%(name)s商业空间绿植设计,%(name)s写字楼绿植,植百汇%(name)s">
<link rel="canonical" href="%(url)s">
<meta property="og:title" content="%(name)s办公室绿植租摆 · 企业绿植租赁养护 - 植百汇">
<meta property="og:description" content="%(name)s企业绿植租摆与养护，植物身份证可追溯、免费更换，小植物约 4.5 元/株/月起，免费上门勘测。">
<meta property="og:type" content="website">
<meta property="og:url" content="%(url)s">
<meta property="og:image" content="%(img)s">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="%(img)s">
<link rel="icon" href="%(cos)s/z100h-favicon.png" type="image/png">
<link rel="apple-touch-icon" href="%(cos)s/z100h-favicon.png">
<link rel="stylesheet" href="/css/style.css">
%(jsonld)s
</head>
<body>

%(nav)s

<section class="page-hero">
  <div class="container">
    <div class="breadcrumb"><a href="/">首页</a> / <a href="/chengshi/">服务城市</a> / %(name)s</div>
    <h1>%(name)s办公室绿植租摆 · 企业绿植租赁养护</h1>
    <p class="hero-sub">%(name)s企业绿植租摆 + 定期智能养护，绿意常新、省心免操心。可租可买，按需选择，免费上门勘测。</p>
    <div class="hero-actions" style="margin-top:18px">
      <a class="btn btn-primary" href="tel:%(phone)s">电话咨询 %(owner)s %(phone)s</a>
      <a class="btn btn-ghost" href="/#contact">免费方案咨询</a>
    </div>
  </div>
</section>

<div class="page-banner"><div class="container"><img src="%(img)s" width="1536" height="640" loading="lazy" alt="植百汇%(name)s办公室绿植租摆与商业空间绿植设计场景示意"></div></div>

<section class="section">
  <div class="container prose">
    <h2>植百汇%(name)s绿植服务</h2>
    <p>%(intro)s</p>
    <p>服务覆盖区域：%(districts)s 等%(name)s主要商务区与园区。无论企业办公租摆 / 购买、商业空间与园区设计养护，均可预约免费上门勘测出方案。</p>
%(hq_block)s
    <h2>为什么%(name)s企业选择植百汇</h2>
    <ul>
      <li><strong>智能养护派单</strong>：按植物习性与环境数据安排上门，定期浇水、施肥、修剪、治虫。</li>
      <li><strong>植物身份证可追溯</strong>：每盆植物配二维码，扫码可见养护记录与维护报告。</li>
      <li><strong>状态不佳免费更换</strong>：近万平自建基地，A 类植物消杀擦拭后进场，替换更快。</li>
      <li><strong>专属客情经理 · 定期巡场</strong>：一对一对接，节假日陈设翻新，突发需求应急响应。</li>
      <li><strong>国家高新技术企业</strong>：自研养护系统与多项专利，AI 辅助设计快速出效果图。</li>
    </ul>

    <h2>适合哪些%(name)s空间</h2>
    <p>办公室、写字楼、商场中庭、酒店大堂、售楼处、展厅、产业园区与物业公共区域等室内外场景，
    覆盖从创业小办公室到 500 强总部、银行总部、五星级酒店等不同体量项目。</p>

    <h2 id="price">%(name)s绿植租摆价格参考</h2>
    <p>下表为常见租摆植物的<strong>均价区间（含养护，单位：元 / 株 / 月）</strong>，%(name)s实际价格以现场勘测报价为准。</p>
%(price)s
    <p class="price-note">* 以上为参考均价区间，含定期养护；具体方案与折扣以免费上门勘测后的正式报价为准。中小企业办公室租摆小植物低至约 <strong>4.5 元 / 株 / 月起</strong>。</p>

    <h2>%(name)s租还是买？</h2>
    <p>想省心、按月预算、形象常换新、短期 / 展会 → 选<strong>租摆</strong>；长期固定、想资产化、能自养或另签养护 → 选<a href="/qiye-goumai/"><strong>买断</strong></a>。两种方案可同时报价对比。详见 <a href="/lvzhi-zubai/">室内绿植租摆</a> 与 <a href="/qiye-goumai/">企业绿植购买</a>。</p>

    <h2>%(name)s联系方式</h2>
    <div class="branches">
      <div class="branch-card">
        <span class="loc-type">%(name)s</span>
        <div class="branch-info"><span class="loc-name">%(owner)s</span><a class="loc-tel" href="tel:%(phone)s">%(phone)s</a></div>
      </div>
    </div>
    <p class="price-note" style="margin-top:12px">电话微信同号，可预约%(name)s免费上门勘测与方案报价。</p>

    <h2>%(name)s绿植租摆常见问题</h2>
%(faq)s
  </div>
</section>

<section class="section section--soft">
  <div class="container">
    <p class="eyebrow">其他服务城市</p>
    <h2 class="section-title">全国连锁，服务体系一致</h2>
    <p class="section-lead">以南京为根据地，统一标准、统一数字化系统。切换到其他城市了解本地服务：</p>
    <div class="cities">
%(other)s    </div>
  </div>
</section>

%(footer)s

<script src="/js/main.js"></script>
</body>
</html>
""" % {
        "title": title, "desc": desc, "name": name, "slug": slug, "url": url, "img": img,
        "cos": COS, "jsonld": build_jsonld(c), "nav": NAV, "footer": FOOTER,
        "phone": c["phone"], "owner": c["owner"], "intro": c["intro"],
        "districts": districts_str, "hq_block": hq_block, "price": price_table(),
        "faq": faq_html, "other": other_cities_links(slug),
    }
    return html


def render_hub():
    cards = ""
    for c in CITIES:
        tag = '<span class="tag tag-p0">根据地</span>' if c["hq"] else ""
        cards += """      <a class="card" href="/chengshi/%(slug)s/">
        <h3>%(name)s绿植租摆%(tag)s</h3>
        <p>%(districts)s 等区域 · 办公室 / 写字楼绿植租摆与养护 · %(owner)s %(phone)s</p>
      </a>
""" % {"slug": c["slug"], "name": c["name"], "tag": tag,
       "districts": "、".join(c["districts"][:3]), "owner": c["owner"], "phone": c["phone"]}

    items = [
        {"@type": "ListItem", "position": i + 1, "name": "%s绿植租摆" % c["name"],
         "url": "%s/chengshi/%s/" % (SITE, c["slug"])}
        for i, c in enumerate(CITIES)
    ]
    itemlist = {"@context": "https://schema.org", "@type": "ItemList",
                "name": "植百汇服务城市", "itemListElement": items}
    jsonld = '<script type="application/ld+json">\n%s\n</script>' % json.dumps(
        itemlist, ensure_ascii=False, indent=2)

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>服务城市_南京上海苏州杭州深圳武汉合肥广州绿植租摆 | 植百汇</title>
<meta name="description" content="植百汇全国连锁绿植服务，覆盖南京、上海、苏州、杭州、深圳、武汉、合肥、广州等城市，提供企业绿植租摆、购买、商业空间设计与养护。各城市统一标准、统一数字化系统，可预约免费上门勘测。">
<link rel="canonical" href="%(site)s/chengshi/">
<meta property="og:title" content="植百汇服务城市 · 全国连锁绿植租摆与养护">
<meta property="og:type" content="website">
<meta property="og:url" content="%(site)s/chengshi/">
<meta property="og:image" content="%(cos)s/z100h-og-cover.jpg">
<link rel="icon" href="%(cos)s/z100h-favicon.png" type="image/png">
<link rel="stylesheet" href="/css/style.css">
%(jsonld)s
</head>
<body>

%(nav)s

<section class="page-hero">
  <div class="container">
    <div class="breadcrumb"><a href="/">首页</a> / 服务城市</div>
    <h1>服务城市 · 全国连锁绿植租摆与养护</h1>
    <p class="hero-sub">以南京为根据地，服务网络覆盖长三角与多座重点城市，统一标准、统一数字化系统。选择你所在的城市了解本地服务与联系方式。</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <p class="eyebrow">选择城市</p>
    <h2 class="section-title">8 座重点城市，本地团队就近服务</h2>
    <p class="section-lead">各城市均提供企业绿植租摆、企业绿植购买、商业空间绿植设计与园区养护，可预约免费上门勘测。</p>
    <div class="grid grid-3">
%(cards)s    </div>
  </div>
</section>

%(footer)s

<script src="/js/main.js"></script>
</body>
</html>
""" % {"site": SITE, "cos": COS, "jsonld": jsonld, "nav": NAV, "footer": FOOTER, "cards": cards}
    return html


def render_cities_redirect(canonical_path, label):
    """/cities/ 英文路径别名：noindex + canonical 指向 chengshi，即时跳转。"""
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, follow">
<title>跳转至%(label)s | 植百汇</title>
<link rel="canonical" href="%(site)s%(path)s">
<meta http-equiv="refresh" content="0;url=%(path)s">
<script>location.replace("%(path)s");</script>
</head>
<body>
<p>城市服务页正式地址为 <a href="%(path)s">%(path)s</a>，正在跳转…</p>
</body>
</html>
""" % {"site": SITE, "path": canonical_path, "label": label}


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("written:", os.path.relpath(path, ROOT))


def main():
    write(os.path.join(OUT_DIR, "index.html"), render_hub())
    for c in CITIES:
        write(os.path.join(OUT_DIR, c["slug"], "index.html"), render_city(c))

    alias_dir = os.path.join(ROOT, "cities")
    write(os.path.join(alias_dir, "index.html"), render_cities_redirect("/chengshi/", "服务城市"))
    for c in CITIES:
        write(
            os.path.join(alias_dir, c["slug"], "index.html"),
            render_cities_redirect("/chengshi/%s/" % c["slug"], "%s绿植租摆" % c["name"]),
        )

    print("done:", len(CITIES), "city pages + 1 hub +", len(CITIES) + 1, "cities alias redirects")


if __name__ == "__main__":
    main()
