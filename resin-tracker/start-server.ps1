# start-server.ps1 — PP/PE 레진 대시보드 로컬 서버 시작
# 실행: .\start-server.ps1
# 브라우저: http://localhost:8080/index.html

$py = "C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe"
$port = 8080

# 포트 점유 확인
$existing = netstat -ano | Select-String ":$port " | Select-String "LISTENING"
if ($existing) {
    Write-Host "[알림] 포트 $port 가 이미 사용 중입니다." -ForegroundColor Yellow
    Write-Host "브라우저에서 http://localhost:$port/index.html 을 열어보세요."
    exit 0
}

if (-not (Test-Path $py)) {
    Write-Host "[오류] Python을 찾을 수 없습니다: $py" -ForegroundColor Red
    Write-Host "Python 3.12를 설치하거나 경로를 수정하세요."
    exit 1
}

Write-Host "서버 시작: http://localhost:$port/index.html" -ForegroundColor Green
Write-Host "종료하려면 Ctrl+C 를 누르세요."
Write-Host ""

Set-Location $PSScriptRoot
& $py -m http.server $port
