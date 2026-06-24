# 植百汇官网 · 生产部署打包脚本
# 用法（在项目根目录或任意处执行）：
#   powershell -ExecutionPolicy Bypass -File "官网\deploy\pack.ps1"
#
# 输出：项目根目录 zhi100hui-deploy.zip（仅含 nginx 静态根目录所需文件）

$ErrorActionPreference = "Stop"
$Src  = Split-Path $PSScriptRoot -Parent
$Root = Split-Path $Src -Parent
$Out  = Join-Path $Root "zhi100hui-deploy.zip"
$Tmp  = Join-Path $env:TEMP ("zhi100hui-pack-" + [guid]::NewGuid().ToString())

if (-not (Test-Path (Join-Path $Src "index.html"))) {
    Write-Error "找不到 官网/index.html，请确认路径：$Src"
}

New-Item -ItemType Directory -Path $Tmp | Out-Null

function Copy-Rel($rel) {
    $from = Join-Path $Src $rel
    $to   = Join-Path $Tmp $rel
    if (-not (Test-Path $from)) {
        Write-Warning "缺失: $rel"
        return $false
    }
    $dir = Split-Path $to -Parent
    if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    Copy-Item $from $to -Force
    return $true
}

# 根文件（图片已迁 COS，不再打包 favicon / assets/img）
@(
    "index.html", "404.html", "robots.txt", "sitemap.xml"
) | ForEach-Object { Copy-Rel $_ | Out-Null }

# 静态资源
Copy-Rel "css\style.css" | Out-Null
Copy-Rel "js\main.js" | Out-Null

# 字体（仅部署 CSS 引用的子集）
@(
    "assets\fonts\AlibabaPuHuiTi-3-55-Regular.subset.woff2",
    "assets\fonts\AlibabaPuHuiTi-3-85-Bold.subset.woff2"
) | ForEach-Object { Copy-Rel $_ | Out-Null }

# 子页面（目录 + index.html）
$pages = @(
    "guanyu", "anli", "lvzhi-zubai", "qiye-goumai", "shangye-sheji",
    "yuanqu-yanghu", "jiating-jingguan", "tingyuan-jingguan",
    "huahui-shop", "lvzhi-huodong", "ai-sheji"
)
foreach ($p in $pages) {
    Copy-Rel "$p\index.html" | Out-Null
}

# nginx 配置单独放在包内 deploy/ 供参考（不会进 web root）
$deployDir = Join-Path $Tmp "deploy"
New-Item -ItemType Directory -Path $deployDir -Force | Out-Null
Copy-Item (Join-Path $Src "deploy\nginx-zhi100hui.conf") (Join-Path $deployDir "nginx-zhi100hui.conf")

# 打 zip
if (Test-Path $Out) { Remove-Item $Out -Force }
Compress-Archive -Path (Join-Path $Tmp "*") -DestinationPath $Out -Force
Remove-Item $Tmp -Recurse -Force

$sizeMB = [math]::Round((Get-Item $Out).Length / 1MB, 2)
Write-Host ""
Write-Host "打包完成: $Out"
Write-Host "大小: ${sizeMB} MB"
Write-Host "图片: 已迁 COS，请单独上传 zhi100hui-cos-images.zip" -ForegroundColor Cyan
Write-Host "服务器: 解压到 /var/www/zhi100hui/ (web root = index.html 所在层)"
