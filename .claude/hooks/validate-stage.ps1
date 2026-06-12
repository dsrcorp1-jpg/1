# validate-stage.ps1
$raw = [Console]::In.ReadToEnd().Trim()
if (-not $raw) { exit 0 }
try { $inputData = $raw | ConvertFrom-Json } catch { exit 0 }

$filePath = $inputData.tool_input.file_path
if (-not ($filePath -and $filePath -like '*data.json')) { exit 0 }

$hooksDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$validStages = Get-Content "$hooksDir\valid-stages.json" -Encoding UTF8 | ConvertFrom-Json

try {
    $content = Get-Content $filePath -Raw -Encoding UTF8 | ConvertFrom-Json
} catch { Write-Error "data.json 파싱 실패: $_"; exit 2 }

# Check 1: Valid stage values
$bad = $content.orders | Where-Object { $_ -and ($validStages -notcontains $_.stage) }
if ($bad) {
    $ids = ($bad | ForEach-Object { "$($_.id) [stage='$($_.stage)']" }) -join ', '
    Write-Error "[data.json 검증 실패] 잘못된 stage: $ids"
    exit 2
}

# Check 2: Required fields
$requiredFields = @('id', 'product', 'stage', 'unit')
$missingRequired = @()
foreach ($order in $content.orders) {
    if (-not $order) { continue }
    foreach ($field in $requiredFields) {
        $value = $order.$field
        if ($null -eq $value -or $value -eq '') {
            $missingRequired += "Order '$($order.id)': 필드 '$field' 누락"
        }
    }
    if (-not $order.quantity -and $order.quantity -ne 0) {
        $missingRequired += "Order '$($order.id)': 필드 'quantity' 누락"
    }
}
if ($missingRequired.Count -gt 0) {
    Write-Error "[data.json 검증 실패] 필수 필드 누락:`n$($missingRequired -join "`n")"
    exit 2
}

# Check 3: Date format (YYYY-MM-DD) — only non-empty dates
$datePattern = '^\d{4}-\d{2}-\d{2}$'
$badDates = @()
$dateFields = @(
    @{ path = 'negotiation'; field = 'date' },
    @{ path = 'contract';    field = 'signDate' },
    @{ path = 'shipment';    field = 'etd' },
    @{ path = 'shipment';    field = 'eta' },
    @{ path = 'customs';     field = 'arrivalDate' },
    @{ path = 'customs';     field = 'declarationDate' },
    @{ path = 'customs';     field = 'clearanceDate' },
    @{ path = 'dispatch';    field = 'date' }
)
foreach ($order in $content.orders) {
    if (-not $order) { continue }
    foreach ($df in $dateFields) {
        $obj = $order.($df.path)
        if (-not $obj) { continue }
        $val = $obj.($df.field)
        if ($val -and $val -ne '' -and $val -notmatch $datePattern) {
            $badDates += "Order '$($order.id)': '$($df.path).$($df.field)' 형식 오류 (값: '$val', 필요: YYYY-MM-DD)"
        }
    }
}
if ($badDates.Count -gt 0) {
    Write-Error "[data.json 검증 실패] 날짜 형식 오류:`n$($badDates -join "`n")"
    exit 2
}

# Check 4: Numeric fields must be positive (if present)
$badNums = @()
foreach ($order in $content.orders) {
    if (-not $order) { continue }
    $n = $order.negotiation
    if ($n) {
        foreach ($field in @('offerPrice', 'counterPrice')) {
            $val = $n.$field
            if ($null -ne $val) {
                $num = $null
                if (-not [decimal]::TryParse([string]$val, [ref]$num) -or $num -le 0) {
                    $badNums += "Order '$($order.id)': 'negotiation.$field' 양수 필요 (값: $val)"
                }
            }
        }
    }
    $qty = $order.quantity
    if ($null -ne $qty) {
        $num = $null
        if (-not [decimal]::TryParse([string]$qty, [ref]$num) -or $num -le 0) {
            $badNums += "Order '$($order.id)': 'quantity' 양수 필요 (값: $qty)"
        }
    }
}
if ($badNums.Count -gt 0) {
    Write-Error "[data.json 검증 실패] 숫자 필드 오류:`n$($badNums -join "`n")"
    exit 2
}

exit 0
