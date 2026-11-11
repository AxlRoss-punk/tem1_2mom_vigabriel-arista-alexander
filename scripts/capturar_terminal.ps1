param(
    [Parameter(Mandatory=$true)][string]$SqlFile,
    [Parameter(Mandatory=$true)][string]$OutputFile,
    [string]$Label = 'Hive - evidencia de ejecucion'
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$sqlAbsolute = [IO.Path]::GetFullPath((Join-Path $projectRoot $SqlFile))
$outputAbsolute = [IO.Path]::GetFullPath((Join-Path $projectRoot $OutputFile))
$scriptsRoot = (Join-Path $projectRoot 'scripts') + [IO.Path]::DirectorySeparatorChar
$evidenceRoot = (Join-Path $projectRoot 'evidencias') + [IO.Path]::DirectorySeparatorChar
if (-not $sqlAbsolute.StartsWith($scriptsRoot, [StringComparison]::OrdinalIgnoreCase) -or
    [IO.Path]::GetExtension($sqlAbsolute) -ne '.sql') {
    throw 'El SQL debe estar dentro de scripts/.'
}
if (-not $outputAbsolute.StartsWith($evidenceRoot, [StringComparison]::OrdinalIgnoreCase) -or
    [IO.Path]::GetExtension($outputAbsolute) -ne '.png') {
    throw 'La captura debe ser PNG y quedar dentro de evidencias/.'
}
$metadataPath = [IO.Path]::ChangeExtension($outputAbsolute, '.captura.json')
foreach ($destination in @($outputAbsolute, $metadataPath)) {
    if (Test-Path -LiteralPath $destination) { throw "Se rechaza sobrescribir: $destination" }
}
$sqlHash = (Get-FileHash -LiteralPath $sqlAbsolute -Algorithm SHA256).Hash.ToLowerInvariant()
$captureId = [Guid]::NewGuid().ToString('N')
$windowTitle = $Label + ' - ' + $captureId.Substring(0, 8)
$signalDirectory = Join-Path $projectRoot 'datos\tmp\capturas'
[IO.Directory]::CreateDirectory($signalDirectory) | Out-Null
$signalPath = Join-Path $signalDirectory ($captureId + '.json')

if (-not ('HiveEvidence.Native' -as [type])) {
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Text;
namespace HiveEvidence {
    [StructLayout(LayoutKind.Sequential)]
    public struct Rect { public int Left, Top, Right, Bottom; }
    public static class Native {
        public delegate bool EnumProc(IntPtr hwnd, IntPtr param);
        [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
        [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc proc, IntPtr param);
        [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hwnd, StringBuilder text, int size);
        [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hwnd);
        [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hwnd, int command);
        [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hwnd);
        [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
        [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hwnd, out Rect rect);
        [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr hwnd, uint message, IntPtr wparam, IntPtr lparam);
        [DllImport("dwmapi.dll")] public static extern int DwmGetWindowAttribute(IntPtr hwnd, int attribute, out Rect rect, int size);
        public static IntPtr FindTitle(string title) {
            IntPtr match = IntPtr.Zero;
            EnumWindows((hwnd, param) => {
                var text = new StringBuilder(1024);
                GetWindowText(hwnd, text, text.Capacity);
                if (IsWindowVisible(hwnd) && text.ToString().Contains(title)) {
                    match = hwnd;
                    return false;
                }
                return true;
            }, IntPtr.Zero);
            return match;
        }
    }
}
'@
}
[HiveEvidence.Native]::SetProcessDPIAware() | Out-Null
Add-Type -AssemblyName System.Drawing
$previousWindow = [HiveEvidence.Native]::GetForegroundWindow()

# Las comillas se escapan como literales de PowerShell, sin sustitucion de comandos.
$quotedRoot = $projectRoot.Replace("'", "''")
$quotedSql = $SqlFile.Replace("'", "''")
$quotedSignal = $signalPath.Replace("'", "''")
$childCode = @"
Set-Location -LiteralPath '$quotedRoot'
`$OutputEncoding = New-Object Text.UTF8Encoding(`$false)
[Console]::OutputEncoding = New-Object Text.UTF8Encoding(`$false)
Write-Host 'Consulta real de Apache Hive' -ForegroundColor Cyan
Write-Host 'wsl -d Ubuntu -- python3 -B scripts/mostrar_sql.py --sql $quotedSql'
& wsl.exe -d Ubuntu -- python3 -B scripts/mostrar_sql.py --sql '$quotedSql'
`$queryExit = `$LASTEXITCODE
Write-Host ('Consulta finalizada. Codigo de salida: ' + `$queryExit)
`$state = @{exit_code=`$queryExit; finished_at_utc=[DateTime]::UtcNow.ToString('o')}
[IO.File]::WriteAllText('$quotedSignal.tmp', (`$state | ConvertTo-Json), (New-Object Text.UTF8Encoding(`$false)))
[IO.File]::Move('$quotedSignal.tmp', '$quotedSignal')
Read-Host 'Resultado disponible para captura'
"@
$encodedChild = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($childCode))
$terminalArguments = '-w new --maximized new-tab --title "' + $windowTitle.Replace('"', '') +
    '" --suppressApplicationTitle powershell.exe -NoLogo -NoProfile -EncodedCommand ' + $encodedChild
# La ventana visible es necesaria para la captura solicitada y ejecuta solo este trabajo.
Start-Process -FilePath 'wt.exe' -ArgumentList $terminalArguments -WindowStyle Normal | Out-Null
$deadline = [DateTime]::UtcNow.AddMinutes(3)
while (-not (Test-Path -LiteralPath $signalPath)) {
    if ([DateTime]::UtcNow -gt $deadline) { throw 'La consulta no termino dentro del plazo de captura.' }
    Start-Sleep -Milliseconds 300
}
$state = Get-Content -LiteralPath $signalPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($state.exit_code -ne 0) { throw 'La consulta fallo; no se guardara una captura como resultado valido.' }
$window = [HiveEvidence.Native]::FindTitle($windowTitle)
if ($window -eq [IntPtr]::Zero) { throw 'No se encontro la ventana exclusiva de la consulta.' }
[HiveEvidence.Native]::ShowWindow($window, 3) | Out-Null
[HiveEvidence.Native]::SetForegroundWindow($window) | Out-Null
Start-Sleep -Milliseconds 800
if ([HiveEvidence.Native]::GetForegroundWindow() -ne $window) {
    throw 'La ventana de consulta no esta delante; se evita capturar otra aplicacion.'
}
$bounds = New-Object HiveEvidence.Rect
$result = [HiveEvidence.Native]::DwmGetWindowAttribute($window, 9, [ref]$bounds, 16)
if ($result -ne 0) { [HiveEvidence.Native]::GetWindowRect($window, [ref]$bounds) | Out-Null }
$width = $bounds.Right - $bounds.Left
$height = $bounds.Bottom - $bounds.Top
if ($width -lt 600 -or $height -lt 400) { throw 'La ventana es demasiado pequena para una evidencia legible.' }
$bitmap = New-Object Drawing.Bitmap($width, $height)
$graphics = [Drawing.Graphics]::FromImage($bitmap)
try {
    $graphics.CopyFromScreen($bounds.Left, $bounds.Top, 0, 0, $bitmap.Size)
    $stream = New-Object IO.FileStream($outputAbsolute, [IO.FileMode]::CreateNew)
    try { $bitmap.Save($stream, [Drawing.Imaging.ImageFormat]::Png) } finally { $stream.Dispose() }
} finally {
    $graphics.Dispose()
    $bitmap.Dispose()
}
if ((Get-FileHash -LiteralPath $sqlAbsolute -Algorithm SHA256).Hash.ToLowerInvariant() -ne $sqlHash) {
    throw 'El archivo SQL cambio durante la captura; revisar la evidencia antes de usarla.'
}
$metadata = [ordered]@{
    captured_at_utc=[DateTime]::UtcNow.ToString('o')
    capture_method='Captura de pixeles de la ventana de Windows Terminal que ejecuto Beeline'
    sql_file=$SqlFile
    sql_sha256=$sqlHash
    native_exit_code=$state.exit_code
    query_finished_at_utc=$state.finished_at_utc
    png_file=$OutputFile
    png_sha256=(Get-FileHash -LiteralPath $outputAbsolute -Algorithm SHA256).Hash.ToLowerInvariant()
    width=$width
    height=$height
    image_content_edited=$false
}
$metadataStream = New-Object IO.FileStream($metadataPath, [IO.FileMode]::CreateNew)
$writer = New-Object IO.StreamWriter($metadataStream, (New-Object Text.UTF8Encoding($false)))
try { $writer.WriteLine(($metadata | ConvertTo-Json -Depth 4)) } finally { $writer.Dispose() }
# Solo se cierra la ventana creada aqui, despues de que haya terminado la consulta.
[HiveEvidence.Native]::PostMessage($window, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null
if ($previousWindow -ne [IntPtr]::Zero) { [HiveEvidence.Native]::SetForegroundWindow($previousWindow) | Out-Null }
$metadata | ConvertTo-Json -Depth 4
