# Tesseract OCR Windows安装助手脚本
# 使用方法: 以管理员身份运行PowerShell，然后执行: .\setup_tesseract_windows.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Tesseract OCR Windows安装助手" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "⚠️  警告: 需要管理员权限来添加到PATH" -ForegroundColor Yellow
    Write-Host "   请以管理员身份运行PowerShell" -ForegroundColor Yellow
    Write-Host ""
}

# 检查是否已安装
Write-Host "检查Tesseract安装状态..." -ForegroundColor Yellow
try {
    $version = tesseract --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Tesseract已安装: $version" -ForegroundColor Green
        Write-Host ""
        Write-Host "检查Python依赖..." -ForegroundColor Yellow
        python -c "import pytesseract; print('✅ pytesseract已安装')" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠️  pytesseract未安装" -ForegroundColor Yellow
            Write-Host "安装Python依赖..." -ForegroundColor Yellow
            pip install pytesseract Pillow
        }
        Write-Host ""
        Write-Host "✅ 安装完成！" -ForegroundColor Green
        exit 0
    }
} catch {
    Write-Host "❌ Tesseract未安装" -ForegroundColor Red
}

Write-Host ""
Write-Host "请选择安装方式:" -ForegroundColor Cyan
Write-Host "1. 手动下载安装（推荐）"
Write-Host "2. 使用Chocolatey安装（需要先安装Chocolatey）"
Write-Host "3. 使用Scoop安装（需要先安装Scoop）"
Write-Host "4. 仅显示安装说明"
Write-Host ""

$choice = Read-Host "请输入选项 (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "手动安装步骤:" -ForegroundColor Cyan
        Write-Host "1. 访问: https://github.com/UB-Mannheim/tesseract/wiki"
        Write-Host "2. 下载最新Windows安装包"
        Write-Host "3. 运行安装程序，选择安装中文语言包"
        Write-Host "4. 安装完成后，添加到PATH: C:\Program Files\Tesseract-OCR"
        Write-Host ""
        Write-Host "是否打开下载页面？(Y/N)" -ForegroundColor Yellow
        $open = Read-Host
        if ($open -eq "Y" -or $open -eq "y") {
            Start-Process "https://github.com/UB-Mannheim/tesseract/wiki"
        }
    }
    "2" {
        Write-Host ""
        Write-Host "检查Chocolatey..." -ForegroundColor Yellow
        if (Get-Command choco -ErrorAction SilentlyContinue) {
            Write-Host "✅ Chocolatey已安装" -ForegroundColor Green
            Write-Host "安装Tesseract..." -ForegroundColor Yellow
            choco install tesseract -y
            Write-Host "✅ 安装完成！" -ForegroundColor Green
        } else {
            Write-Host "❌ Chocolatey未安装" -ForegroundColor Red
            Write-Host "请先安装Chocolatey: https://chocolatey.org/install" -ForegroundColor Yellow
        }
    }
    "3" {
        Write-Host ""
        Write-Host "检查Scoop..." -ForegroundColor Yellow
        if (Get-Command scoop -ErrorAction SilentlyContinue) {
            Write-Host "✅ Scoop已安装" -ForegroundColor Green
            Write-Host "安装Tesseract..." -ForegroundColor Yellow
            scoop install tesseract
            Write-Host "✅ 安装完成！" -ForegroundColor Green
        } else {
            Write-Host "❌ Scoop未安装" -ForegroundColor Red
            Write-Host "请先安装Scoop: https://scoop.sh/" -ForegroundColor Yellow
        }
    }
    "4" {
        Write-Host ""
        Write-Host "安装说明:" -ForegroundColor Cyan
        Write-Host "1. 下载安装包: https://github.com/UB-Mannheim/tesseract/wiki"
        Write-Host "2. 运行安装程序，选择中文语言包"
        Write-Host "3. 添加到PATH: C:\Program Files\Tesseract-OCR"
        Write-Host "4. 安装Python依赖: pip install pytesseract Pillow"
        Write-Host ""
        Write-Host "详细说明请查看: INSTALL_TESSERACT_WINDOWS.md" -ForegroundColor Yellow
    }
    default {
        Write-Host "无效选项" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "安装完成后，请运行以下命令验证:" -ForegroundColor Cyan
Write-Host "  tesseract --version" -ForegroundColor White
Write-Host "  python -c \"import pytesseract; print('OK')\"" -ForegroundColor White
Write-Host ""
