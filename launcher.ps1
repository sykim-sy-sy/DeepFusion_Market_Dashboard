$WORKING_DIR = $PSScriptRoot
$SCRIPT_PATH = Join-Path $WORKING_DIR "Agents\agent1_market_analyst.py"
$LOG_DIR = Join-Path $WORKING_DIR "Market_Analyst_Data\logs"
$LOG_FILE = Join-Path $LOG_DIR "launcher_log.txt"

# Ensure log directory exists
if (-not (Test-Path $LOG_DIR)) {
    New-Item -Path $LOG_DIR -ItemType Directory -Force | Out-Null
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"[$timestamp] Launcher starting... (Path: $WORKING_DIR)" | Out-File -FilePath $LOG_FILE -Append -Encoding UTF8

try {
    # Set encoding to UTF8 for stdout
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    
    # Run the python script
    & python "$SCRIPT_PATH" 2>&1 | Out-File -FilePath $LOG_FILE -Append -Encoding UTF8
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$timestamp] Launcher finished successfully." | Out-File -FilePath $LOG_FILE -Append -Encoding UTF8
} catch {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$timestamp] Launcher caught error: $_" | Out-File -FilePath $LOG_FILE -Append -Encoding UTF8
    exit 1
}
