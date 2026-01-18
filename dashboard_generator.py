import json
import webbrowser
from pathlib import Path
from datetime import datetime
from analytics import STATS_FILE

DASHBOARD_FILE = "dashboard.html"

class DashboardGenerator:
    """Generates a beautiful HTML dashboard for DailyNewsBot analytics."""
    
    def __init__(self):
        self.stats = self._load_stats()
        
    def _load_stats(self):
        if Path(STATS_FILE).exists():
            try:
                return json.loads(Path(STATS_FILE).read_text())
            except:
                pass
        return {"history": [], "total_runs": 0, "total_errors": 0, "api_calls": 0}

    def generate(self):
        """Create the dashboard.html file."""
        html = self._build_html()
        Path(DASHBOARD_FILE).write_text(html, encoding="utf-8")
        print(f"[OK] Dashboard generated: {Path(DASHBOARD_FILE).absolute()}")
        return Path(DASHBOARD_FILE).absolute()

    def open(self):
        """Open the dashboard in browser."""
        path = self.generate()
        webbrowser.open(f"file://{path}")

    def _build_html(self):
        # Prepare data for charts
        history = self.stats.get("history", [])[:20] # Last 20 runs
        labels = [h["timestamp"][11:16] for h in reversed(history)] # HH:MM
        articles = [h["articles"] for h in reversed(history)]
        durations = [h["duration"] for h in reversed(history)]
        
        # Calculate success rate
        total = self.stats.get("total_runs", 1)
        errors = self.stats.get("total_errors", 0)
        success_rate = round(((total - errors) / total) * 100, 1)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DailyNewsBot Intelligence Center</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #0f172a; color: #e2e8f0; }}
        .card {{ background-color: #1e293b; border-radius: 1rem; padding: 1.5rem; border: 1px solid #334155; }}
        .metric-value {{ font-size: 2.5rem; font-weight: 700; color: #38bdf8; }}
        .metric-label {{ color: #94a3b8; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; }}
    </style>
</head>
<body class="p-8">
    <div class="max-w-7xl mx-auto">
        <!-- Header -->
        <div class="flex justify-between items-center mb-8">
            <div>
                <h1 class="text-3xl font-bold text-white mb-2">DailyNewsBot Command Center</h1>
                <p class="text-slate-400">System Status & Intelligence Briefing</p>
            </div>
            <div class="flex gap-4">
                <span class="px-3 py-1 bg-green-500/10 text-green-400 rounded-full border border-green-500/20 text-sm font-medium">
                    ● System Active
                </span>
                <span class="text-slate-500 text-sm">Last Update: {datetime.now().strftime('%H:%M:%S')}</span>
            </div>
        </div>

        <!-- KPI Grid -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="card">
                <div class="metric-label">Success Rate</div>
                <div class="metric-value text-green-400">{success_rate}%</div>
                <div class="text-sm text-slate-500 mt-2">Total Runs: {self.stats.get('total_runs', 0)}</div>
            </div>
            <div class="card">
                <div class="metric-label">Articles Processed</div>
                <div class="metric-value text-blue-400">{sum(articles)}</div>
                <div class="text-sm text-slate-500 mt-2">Latest Batch: {articles[-1] if articles else 0}</div>
            </div>
            <div class="card">
                <div class="metric-label">Avg Processing Time</div>
                <div class="metric-value text-purple-400">{round(sum(durations)/len(durations), 1) if durations else 0}s</div>
                <div class="text-sm text-slate-500 mt-2">Performance Metric</div>
            </div>
            <div class="card">
                <div class="metric-label">API Calls</div>
                <div class="metric-value text-orange-400">{self.stats.get('api_calls', 0)}</div>
                <div class="text-sm text-slate-500 mt-2">External Requests</div>
            </div>
        </div>

        <!-- Charts Row -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div class="card">
                <h3 class="text-lg font-semibold mb-4 text-white">Articles Fetched (Last 20 Runs)</h3>
                <canvas id="articlesChart"></canvas>
            </div>
            <div class="card">
                <h3 class="text-lg font-semibold mb-4 text-white">Processing Duration (Seconds)</h3>
                <canvas id="durationChart"></canvas>
            </div>
        </div>

        <!-- Recent Logs Table -->
        <div class="card">
            <h3 class="text-lg font-semibold mb-4 text-white">Recent Operations Log</h3>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-sm text-slate-400">
                    <thead class="bg-slate-800 text-slate-200 uppercase font-medium">
                        <tr>
                            <th class="px-4 py-3">Timestamp</th>
                            <th class="px-4 py-3">Status</th>
                            <th class="px-4 py-3">Duration</th>
                            <th class="px-4 py-3">Articles</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-700">
                        {self._generate_rows(history)}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        // Chart Config
        Chart.defaults.color = '#94a3b8';
        Chart.defaults.borderColor = '#334155';

        const ctx1 = document.getElementById('articlesChart').getContext('2d');
        new Chart(ctx1, {{
            type: 'line',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{{
                    label: 'Articles',
                    data: {json.dumps(articles)},
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }} }}
        }});

        const ctx2 = document.getElementById('durationChart').getContext('2d');
        new Chart(ctx2, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{{
                    label: 'Seconds',
                    data: {json.dumps(durations)},
                    backgroundColor: '#a855f7',
                    borderRadius: 4
                }}]
            }},
            options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }} }}
        }});
    </script>
</body>
</html>
"""

    def _generate_rows(self, history):
        rows = ""
        for h in history:
            status_color = "text-green-400" if h['success'] else "text-red-400"
            status_text = "SUCCESS" if h['success'] else "FAILED"
            rows += f"""
            <tr class="hover:bg-slate-800/50 transition">
                <td class="px-4 py-3">{h['timestamp'].replace('T', ' ')[:19]}</td>
                <td class="px-4 py-3 font-semibold {status_color}">{status_text}</td>
                <td class="px-4 py-3">{h['duration']}s</td>
                <td class="px-4 py-3">{h['articles']}</td>
            </tr>
            """
        return rows

if __name__ == "__main__":
    dg = DashboardGenerator()
    dg.generate()
