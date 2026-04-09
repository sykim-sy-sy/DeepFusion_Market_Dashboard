$task_name = "DeepFusion_Daily_Morning_Report"
$working_dir = $PSScriptRoot
$launcher_path = Join-Path $working_dir "launcher.ps1"

# 1. Unregister if exists
Unregister-ScheduledTask -TaskName $task_name -Confirm:$false -ErrorAction SilentlyContinue

# 2. Create Base64 encoded command to avoid Task Scheduler Unicode corruption
$script_to_run = "& `"$launcher_path`""
$bytes = [System.Text.Encoding]::Unicode.GetBytes($script_to_run)
$encoded_command = [Convert]::ToBase64String($bytes)

# 3. Create action
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -EncodedCommand $encoded_command"

# 4. Create trigger (Daily at 8:00 AM)
$trigger = New-ScheduledTaskTrigger -Daily -At 8:00am

# 5. Set settings
# StartWhenAvailable ensures it runs if the PC was off at 8:00 AM
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 6. Register task
Register-ScheduledTask -TaskName $task_name -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null

Write-Output "Successfully registered scheduled task: $task_name"
Write-Output "Next execution scheduled at 8:00 AM daily (will run on startup if missed)."
