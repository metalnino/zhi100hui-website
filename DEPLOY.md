# 植百汇官网 · 部署与运维手册

> **最后更新**：2026-06-24  
> **线上地址**：https://www.zhi100hui.com/  
> **维护人必读**：改代码、换图、续证书、发版前先看本文。

---

## 1. 架构总览

```
用户浏览器
    │
    ▼
域名 zhi100hui.com / www.zhi100hui.com
    │  DNS → 120.27.118.87
    ▼
Nginx 1.8.1（/etc/nginx/conf.d/nginx-zhi100hui.conf）
    │  HTTP 80  → 301 → HTTPS www
    │  HTTPS 443 → 静态 HTML/CSS/JS/字体
    │
    ├─ /var/www/zhi100hui/          ← 网站文件（无图片）
    │
    └─ 图片不经过服务器 ──────────────► 腾讯云 COS
         mpfamily-1301068541 / website-z100h/
```

| 项目 | 值 |
|------|-----|
| 正式域名 | `www.zhi100hui.com`（canonical 统一指向此域） |
| 裸域 | `zhi100hui.com` → 301 → `https://www.zhi100hui.com`（路径不变） |
| 服务器 IP | `120.27.118.87` |
| SSH 用户 | `root` |
| Web 根目录 | `/var/www/zhi100hui/` |
| Nginx 版本 | 1.8.1（**无 HTTP/2、无 TLS 1.3**） |
| OpenSSL | 1.0.1e |
| 协议 | 仅 TLS 1.2 |
| 备案 | 苏ICP备17037731号 |

---

## 2. 本地仓库目录结构

```
植百汇GEO项目/                          ← Git 根目录
│
├── DEPLOY.md                           ← 本文（部署运维唯一权威文档）
├── README.md                           ← 项目说明 + GEO 方案维护约定
├── .gitignore
│
├── 25731470_zhi100hui.com_nginx.zip    ← SSL 证书原始包（DigiCert，不入 Git）
├── ssl-zhi100hui/                      ← 解压后的证书（不入 Git）
│   ├── zhi100hui.com.pem               ← 证书链（上传服务器后改名为 .crt）
│   └── zhi100hui.com.key               ← 私钥
│
├── zhi100hui-deploy.zip                ← 网站部署包（pack.ps1 生成，不入 Git）
├── zhi100hui-cos-images.zip            ← COS 图片包（prepare_cos_images.py 生成，不入 Git）
│
├── cos-upload/                         ← COS 图片本地整理目录
│   ├── manifest.json                   ← 本地路径 ↔ COS 文件名 ↔ 完整 URL 映射表
│   ├── README-COS上传.txt
│   └── website-z100h/                  ← 15 张重命名后的图片（上传 COS 用）
│
├── 官网/                               ← 静态站源码（开发主目录）
│   ├── index.html                      ← 首页
│   ├── 404.html
│   ├── robots.txt
│   ├── sitemap.xml                     ← 12 个 HTTPS URL
│   ├── llms.txt                        ← LLM/GEO 索引（llmstxt.org 规范）
│   ├── css/style.css
│   ├── js/main.js
│   ├── assets/
│   │   ├── fonts/                      ← 部署用字体子集（woff2，约 2 个文件）
│   │   └── img/                        ← 本地开发/备份原图（线上已迁 COS，仓库仅 .gitkeep）
│   ├── guanyu/index.html               ← 子页均为「目录 + index.html」
│   ├── anli/index.html
│   ├── lvzhi-zubai/index.html
│   ├── qiye-goumai/index.html
│   ├── shangye-sheji/index.html
│   ├── yuanqu-yanghu/index.html
│   ├── jiating-jingguan/index.html
│   ├── tingyuan-jingguan/index.html
│   ├── huahui-shop/index.html
│   ├── lvzhi-huodong/index.html
│   ├── ai-sheji/index.html
│   └── deploy/                         ← 打包 / 远程部署 / nginx 模板 / 工具脚本
│       ├── nginx-zhi100hui.conf        ← ★ 生产 nginx 配置模板（HTTPS 版）
│       ├── nginx.conf                  ← 本地预览用（可选）
│       ├── pack.ps1                    ← 打网站部署 zip
│       ├── prepare_cos_images.py       ← 整理图片 → cos-upload + zhi100hui-cos-images.zip
│       ├── apply_cos_urls.py           ← 批量把 HTML 图片路径改为 COS URL
│       ├── remote_deploy.py            ← SSH 上传 zip 并解压到 /var/www/zhi100hui
│       ├── remote_ssl_https.py         ← ★ 证书 + 网站 + HTTPS nginx 一键部署
│       ├── remote_finish_https.py      ← nginx reload + 验证
│       ├── remote_nginx_setup.py       ← 仅 HTTP 版（历史，证书上线前用过）
│       ├── remote_verify.py            ← 检查文件与权限
│       ├── verify_live.py              ← 本地验证 HTTPS 与 COS 可访问性
│       └── dev_server.py               ← 本地简易预览
│
├── 方案文档/                           ← GEO 方案 HTML（gitignore，不入官网仓库）
├── 资料/                               ← 业务资料（gitignore）
└── 官网/fonts/                         ← 完整字体包 500MB+（gitignore，仅本地.subset 用）
```

---

## 3. 服务器目录结构（/var/www/zhi100hui）

2026-06-24 线上实际布局（**不含图片**）：

```
/var/www/zhi100hui/
├── index.html
├── 404.html
├── robots.txt
├── sitemap.xml
├── llms.txt
├── css/
│   └── style.css
├── js/
│   └── main.js
├── assets/
│   └── fonts/
│       ├── AlibabaPuHuiTi-3-55-Regular.subset.woff2
│       └── AlibabaPuHuiTi-3-85-Bold.subset.woff2
├── deploy/
│   └── nginx-zhi100hui.conf            ← 配置模板备份（非 nginx 加载路径）
├── guanyu/index.html
├── anli/index.html
├── lvzhi-zubai/index.html
├── qiye-goumai/index.html
├── shangye-sheji/index.html
├── yuanqu-yanghu/index.html
├── jiating-jingguan/index.html
├── tingyuan-jingguan/index.html
├── huahui-shop/index.html
├── lvzhi-huodong/index.html
└── ai-sheji/index.html
```

**文件权限**：`root:root`，目录 `755`，文件 `644`（该机器无 `nginx` 系统用户）。

---

## 4. 静态资源存储

### 4.1 图片 → 腾讯云 COS（线上正式）

| 项 | 值 |
|----|-----|
| 存储桶 | `mpfamily-1301068541` |
| 地域 | 上海 `ap-shanghai` |
| COS 目录 | `website-z100h/` |
| 访问前缀 | `https://mpfamily-1301068541.cos.ap-shanghai.myqcloud.com/website-z100h/` |
| 文件数量 | 15 张（HTML 实际引用） |
| HTML 引用方式 | **COS 绝对 URL**（非 `/assets/img/` 相对路径） |
| 完整映射表 | `cos-upload/manifest.json` |

**COS 文件清单与命名：**

| COS 文件名 | 原本地路径 | 用途 |
|------------|-----------|------|
| `z100h-favicon.png` | `favicon.png` | favicon、apple-touch-icon、JSON-LD logo |
| `z100h-og-cover.jpg` | `assets/img/og-cover.jpg` | og:image、twitter:image、JSON-LD image |
| `z100h-hero-office.jpg` | `assets/img/hero-office.jpg` | 首页 Hero、租摆/购买 banner |
| `z100h-scene-commercial.jpg` | `assets/img/scene-commercial.jpg` | 商业/园区/AI 设计页 banner |
| `z100h-scene-home.jpg` | `assets/img/scene-home.jpg` | 家庭/庭院页 banner |
| `z100h-scene-retail.jpg` | `assets/img/scene-retail.jpg` | 零售/活动页 banner |
| `z100h-brand-logo.png` | `assets/img/brand/logo-xiaozhi.png` | 全站导航/页脚 Logo |
| `z100h-brand-mascot.png` | `assets/img/brand/xiaozhi-t.png` | 首页 IP、404 |
| `z100h-brand-mascot-pair.jpg` | `assets/img/brand/xiaozhi-pair.jpg` | 关于我们 IP 展示 |
| `z100h-cert-gaoxin.png` | `assets/img/gaoxin-zhengshu.png` | 高新证书 |
| `z100h-cert-miaomu.png` | `assets/img/honor-miaomu-fuhuizhang.png` | 苗木商会牌匾 |
| `z100h-patent-fm-108427359.png` | `assets/img/patent-fm-108427359.png` | 发明专利 |
| `z100h-patent-syxx-2018.png` | `assets/img/patent-syxx-2018.png` | 实用新型 |
| `z100h-patent-syxx-214902408.png` | `assets/img/patent-syxx-214902408.png` | 实用新型 |
| `z100h-patent-syxx-219555734.png` | `assets/img/patent-syxx-219555734.png` | 实用新型 |

**换图流程：**

1. 替换 `官网/assets/img/` 下对应原图（或新增后改 manifest）
2. `python 官网/deploy/prepare_cos_images.py` → 生成 `cos-upload/` 与 `zhi100hui-cos-images.zip`
3. 上传 `website-z100h/` 内文件到 COS（可覆盖同名）
4. 若文件名变了：`python 官网/deploy/apply_cos_urls.py` 更新 HTML
5. 重新 `pack.ps1` + 部署网站包

**验证 COS 单张图：**

```
https://mpfamily-1301068541.cos.ap-shanghai.myqcloud.com/website-z100h/z100h-brand-logo.png
```

### 4.2 字体 → 服务器自托管

| 项 | 值 |
|----|-----|
| 字体 | 阿里巴巴普惠体 3.0（子集 woff2） |
| 路径 | `/var/www/zhi100hui/assets/fonts/` |
| 源码 | `官网/assets/fonts/*.subset.woff2` |
| 完整包 | `官网/fonts/`（500MB+，仅本地 subset 用，不入 Git） |
| CSS 引用 | `/assets/fonts/...`（相对 Web 根，走 nginx 静态缓存 30 天） |

### 4.3 CSS / JS → 服务器自托管

| 文件 | 路径 |
|------|------|
| 样式 | `/css/style.css` |
| 脚本 | `/js/main.js` |

---

## 5. SSL 证书

### 5.1 当前证书信息

| 项 | 值 |
|----|-----|
| 签发机构 | DigiCert Encryption Everywhere DV TLS CA - G2 |
| 域名 | `zhi100hui.com`、`www.zhi100hui.com` |
| **签发日** | **2026-06-24** |
| **到期日** | **2026-09-21 23:59:59 GMT** |
| 有效期 | **约 3 个月**（DigiCert 免费 DV，需季度续期） |
| 原始下载包 | `25731470_zhi100hui.com_nginx.zip`（项目根目录，**勿提交 Git**） |
| 本地解压 | `ssl-zhi100hui/zhi100hui.com.pem` + `zhi100hui.com.key` |

### 5.2 服务器上的证书路径

| 文件 | 路径 | 权限 |
|------|------|------|
| 证书链 | `/etc/nginx/ssl/zhi100hui.com.crt` | 644 |
| 私钥 | `/etc/nginx/ssl/zhi100hui.com.key` | 600 |

> nginx 配置中 `ssl_certificate` 指向 `.crt`，内容由 DigiCert 包的 `.pem` 重命名而来。

### 5.3 续期日历（务必写入日程）

| 节点 | 日期 | 动作 |
|------|------|------|
| 上线 | 2026-06-24 | ✅ 已部署 |
| **提醒续期** | **2026-09-07**（到期前 2 周） | 登录 DigiCert/腾讯云重新申请 |
| **必须完成** | **2026-09-21 前** | 上传新证书并 reload nginx |
| 下一周期预估 | 2026-12 中旬 | 再续 3 个月 |

### 5.4 证书更新步骤

1. 下载新的 `*_zhi100hui.com_nginx.zip` 到项目根目录
2. 解压到 `ssl-zhi100hui/`（覆盖旧文件）
3. 设置 SSH 密码环境变量（**不要把密码写进代码或本文**）：
   ```powershell
   $env:DEPLOY_SSH_PASSWORD = '<你的 root 密码>'
   ```
4. 一键部署：
   ```powershell
   python 官网\deploy\remote_ssl_https.py
   ```
5. 验证：
   ```powershell
   python 官网\deploy\verify_live.py
   ```
6. **更新本文 §5.1 的签发日/到期日**

---

## 6. Nginx 配置

### 6.1 配置文件位置

| 位置 | 说明 |
|------|------|
| **生产生效** | `/etc/nginx/conf.d/nginx-zhi100hui.conf` |
| **Git 模板** | `官网/deploy/nginx-zhi100hui.conf` |
| **Web 根备份** | `/var/www/zhi100hui/deploy/nginx-zhi100hui.conf` |

### 6.2 当前逻辑（HTTPS 已启用，2026-06-24）

```
:80  zhi100hui.com / www.zhi100hui.com
     → 301 https://www.zhi100hui.com$request_uri

:443 zhi100hui.com
     → 301 https://www.zhi100hui.com$request_uri

:443 www.zhi100hui.com
     → 静态站 root=/var/www/zhi100hui
     → try_files $uri $uri/ =404
     → 404 走 /404.html
```

**干净 URL 映射**（目录式，非 `.html`）：

| URL | 文件 |
|-----|------|
| `/` | `index.html` |
| `/guanyu/` | `guanyu/index.html` |
| `/anli/` | `anli/index.html` |
| `/lvzhi-zubai/` | `lvzhi-zubai/index.html` |
| `/qiye-goumai/` | `qiye-goumai/index.html` |
| `/shangye-sheji/` | `shangye-sheji/index.html` |
| `/yuanqu-yanghu/` | `yuanqu-yanghu/index.html` |
| `/jiating-jingguan/` | `jiating-jingguan/index.html` |
| `/tingyuan-jingguan/` | `tingyuan-jingguan/index.html` |
| `/huahui-shop/` | `huahui-shop/index.html` |
| `/lvzhi-huodong/` | `lvzhi-huodong/index.html` |
| `/ai-sheji/` | `ai-sheji/index.html` |

### 6.3 同机其他站点（勿删、勿整体禁用 default.conf）

| 配置 | 用途 |
|------|------|
| **`/etc/nginx/conf.d/default.conf`** | **应用服务器反代（ca/mp/wx/sc/erp 等子域）— 必须保留** |
| `/etc/nginx/conf.d/default.conf.bak.20260624` | 2026-06-24 上线官网前的完整备份 |
| `/etc/nginx/conf.d/jtyjt.conf` | jtyjt.cn 跳转，与植百汇无冲突 |
| `/etc/nginx/conf.d/nginx-zhi100hui.conf` | **仅** `www` / 裸域静态官网 + HTTPS |

> **重要（2026-06-24 事故复盘）**  
> 上线官网时曾把 `default.conf` 整体改名为 `.bak` 并禁用，导致 **`ca.zhi100hui.com` 等应用子域全部不可用**（被 `nginx-zhi100hui.conf` 的默认 443 块误接管并 301 到 www）。  
> **已修复**：从 `default.conf.bak.20260624` 恢复 `default.conf`，**仅注释**原文件中把 `www.zhi100hui.com` / `zhi100hui.com` 反代到 `120.26.196.120:8443` 的那段（约第 169–206 行）。  
> 恢复脚本：`官网/deploy/remote_restore_default.py`

**`default.conf` 中仍生效的主要子域（示例）：**

| 子域 | 用途（概要） |
|------|----------------|
| `ca.zhi100hui.com` | HTTPS 443 → 反代 `https://120.26.196.120:8443`（主应用入口） |
| `qr.zhi100hui.com` | 二维码静态页 |
| `sh.zhi100hui.com` | 静态前端 `/home/test/dist` |
| `mall.zhi100hui.com` | 反代应用 |
| `mp/wx/sc/erp.zhi100hui.com` | 跳转或反代至 ca 路径 |
| `static/update.zhi100hui.com` | 静态资源 / 更新服务 |

**证书（ca 子域，与官网证书分开）：**

| 文件 | 路径 |
|------|------|
| ca 证书 | `/etc/nginx/ca.zhi100hui.com.pem` |
| ca 私钥 | `/etc/nginx/ca.zhi100hui.com.key` |

**今后部署官网时禁止：**

- ❌ 删除或整体禁用 `default.conf`
- ❌ 在 `nginx-zhi100hui.conf` 里添加 `ca.` 等子域
- ✅ 只维护 `nginx-zhi100hui.conf` 中的 `www` / 裸域

### 6.4 常用运维命令（SSH 登录后）

```bash
nginx -t                          # 检查配置
nginx -s reload                   # 热加载
openssl x509 -in /etc/nginx/ssl/zhi100hui.com.crt -noout -dates   # 查看证书有效期
curl -sI http://www.zhi100hui.com/ | head -5    # 应 301 到 HTTPS
curl -skI https://www.zhi100hui.com/ | head -5  # 应 200
```

---

## 7. 发布流程（日常改代码）

### 7.1 仅改 HTML/CSS/JS/字体（不换图）

```powershell
# 1. 本地改 官网/ 下文件

# 2. 打包（输出到项目根 zhi100hui-deploy.zip，约 0.35 MB）
powershell -ExecutionPolicy Bypass -File 官网\deploy\pack.ps1

# 3. 上传部署
$env:DEPLOY_SSH_PASSWORD = '<密码>'
python 官网\deploy\remote_deploy.py

# 4. 验证
python 官网\deploy\verify_live.py
```

### 7.2 改图片

见 §4.1 换图流程（COS 与网站包分开更新）。

### 7.3 证书 + 网站全量

```powershell
python 官网\deploy\remote_ssl_https.py
```

---

## 8. 部署脚本速查

| 脚本 | 作用 |
|------|------|
| `pack.ps1` | 打 `zhi100hui-deploy.zip`（无图片） |
| `prepare_cos_images.py` | 整理 COS 图片包 + manifest |
| `apply_cos_urls.py` | HTML 批量替换为 COS URL |
| `remote_deploy.py` | SSH 上传网站 zip |
| `remote_restore_default.py` | **恢复 default.conf（ca 等应用子域）** |
| `remote_ssl_https.py` | 证书 + 网站 + HTTPS nginx |
| `remote_finish_https.py` | reload nginx + 远程自检 |
| `verify_live.py` | 本地 curl 验证 HTTPS/COS |
| `remote_nginx_setup.py` | ⚠️ 仅 HTTP 版，证书上线后勿用 |
| `dev_server.py` | 本地预览 |

**SSH 连接要求：**

- 环境变量：`DEPLOY_SSH_PASSWORD`（不要写入仓库）
- Python 依赖：`paramiko`、`scp`（建议 paramiko 2.12+ 以兼容老服务器 ssh-rsa）

---

## 9. SEO / 抓取

| 文件 | 地址 |
|------|------|
| Sitemap | https://www.zhi100hui.com/sitemap.xml |
| Robots | https://www.zhi100hui.com/robots.txt |
| llms.txt | https://www.zhi100hui.com/llms.txt（裸域同路径 301 到 www） |
| llms.txt 维护 | 源码 `官网/llms.txt`；须含品牌实体、FAQ 标准答案、价格摘录、案例摘要、联系方式（GEO 可引用级，非仅链接目录） |
| Canonical | 全站指向 `https://www.zhi100hui.com/...` |

**待办（可选）：** 百度/Google/Bing 站长平台提交 sitemap（HTTPS 版）。

---

## 10. 安全提醒

- ❌ **勿将** SSL 私钥、SSH 密码、`25731470_*.zip` 提交 Git
- ✅ 私钥仅存在于：本地 `ssl-zhi100hui/`、服务器 `/etc/nginx/ssl/`
- ✅ 建议定期更换服务器 root 密码
- ✅ 证书到期前 2 周必须续期（§5.3）

---

## 11. 变更日志

| 日期 | 变更 |
|------|------|
| 2026-06-24 | **修复**：恢复 `default.conf`，`ca.zhi100hui.com` 等应用子域重新可用 |
| 2026-06-24 | HTTPS 上线；图片迁 COS；nginx 切换 `nginx-zhi100hui.conf` HTTPS 三件套 |
| 2026-06-24 | 裸域/zhi100hui.com 301 → www；禁用 default.conf |
| 2026-06-23 | 首版 HTTP 上线；目录式 URL（`guanyu/index.html`） |

---

*文档路径：`DEPLOY.md`（项目根目录）。有部署相关变更请同步更新本文。*
