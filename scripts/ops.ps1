param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("status","health","logs","init-pi3","init-pi4","deploy-pi3","deploy-pi4","restart-pi3","restart-pi4","backup","test")]
    [string]$Action
)

$Pi3 = "worldnews-pi3"
$Pi4 = "worldnews-pi4"

switch ($Action) {
    "status" {
        Write-Host "=== Pi3 Services Status ==="
        ssh $Pi3 "systemctl --user status world-news-collector.service --no-pager 2>/dev/null || true"
        Write-Host ""
        Write-Host "=== Pi4 Services Status ==="
        ssh $Pi4 "systemctl --user status world-news-analyzer.service world-news-api.service llama-server.service --no-pager 2>/dev/null || true"
    }
    "health" {
        Write-Host "=== Pi3 Health ==="
        ssh $Pi3 "hostname; uptime; free -h; df -h /; (vcgencmd measure_temp 2>/dev/null || cat /sys/class/thermal/thermal_zone0/temp)"
        Write-Host ""
        Write-Host "=== Pi4 Health ==="
        ssh $Pi4 "hostname; uptime; free -h; df -h /; (vcgencmd measure_temp 2>/dev/null || cat /sys/class/thermal/thermal_zone0/temp)"
    }
    "logs" {
        Write-Host "=== Pi3 Recent Logs ==="
        ssh $Pi3 "journalctl --user -u world-news-collector.service -n 50 --no-pager 2>/dev/null || true"
        Write-Host ""
        Write-Host "=== Pi4 Recent Logs ==="
        ssh $Pi4 "journalctl --user -u world-news-analyzer.service -u world-news-api.service -u llama-server.service -n 50 --no-pager 2>/dev/null || true"
    }
    "init-pi3" {
        Write-Host "=== Initializing Pi3 Directory & Virtual Environment ==="
        ssh $Pi3 "mkdir -p ~/world_news ~/.config/systemd/user && python3 -m venv ~/world_news/venv"
        Write-Host "Pi3 environment initialized at ~/world_news/venv"
    }
    "init-pi4" {
        Write-Host "=== Initializing Pi4 Directory & Virtual Environment ==="
        ssh $Pi4 "mkdir -p ~/world_news ~/.config/systemd/user && python3 -m venv ~/world_news/venv"
        Write-Host "Pi4 environment initialized at ~/world_news/venv"
    }
    "deploy-pi3" {
        Write-Host "=== Deploying to Pi3 ==="
        ssh $Pi3 "mkdir -p ~/world_news/src ~/.config/systemd/user"
        scp -r ./src/* "${Pi3}:~/world_news/src/"
        scp ./config.example.yaml "${Pi3}:~/world_news/config.example.yaml"
        scp ./systemd/world-news-collector.service "${Pi3}:~/.config/systemd/user/"
        ssh $Pi3 "systemctl --user daemon-reload"
        Write-Host "Pi3 deployment completed."
    }
    "deploy-pi4" {
        Write-Host "=== Deploying to Pi4 ==="
        ssh $Pi4 "mkdir -p ~/world_news/src ~/.config/systemd/user"
        scp -r ./src/* "${Pi4}:~/world_news/src/"
        scp ./config.example.yaml "${Pi4}:~/world_news/config.example.yaml"
        scp ./systemd/world-news-analyzer.service "${Pi4}:~/.config/systemd/user/"
        scp ./systemd/world-news-api.service "${Pi4}:~/.config/systemd/user/"
        scp ./systemd/llama-server.service "${Pi4}:~/.config/systemd/user/"
        ssh $Pi4 "systemctl --user daemon-reload"
        Write-Host "Pi4 deployment completed."
    }
    "restart-pi3" {
        Write-Host "Restarting Pi3 collector service..."
        ssh $Pi3 "systemctl --user restart world-news-collector.service 2>/dev/null || true"
    }
    "restart-pi4" {
        Write-Host "Restarting Pi4 analyzer, api, llama-server services..."
        ssh $Pi4 "systemctl --user restart world-news-analyzer.service world-news-api.service llama-server.service 2>/dev/null || true"
    }
    "backup" {
        Write-Host "Backup placeholder. Database path: ~/world_news/data.db"
    }
    "test" {
        if (Test-Path ".\tests") {
            $env:PYTHONPATH = "src"
            python -m pytest
        } else {
            Write-Host "No tests directory found."
        }
    }
}
