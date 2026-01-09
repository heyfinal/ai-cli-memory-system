#!/usr/bin/env python3
"""
AI CLI Memory Dashboard
Web-based visualization of your memory and stats
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template, jsonify, send_from_directory
from memory_manager import MemoryManager

app = Flask(__name__)
manager = MemoryManager()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def api_stats():
    """Get overall statistics"""
    stats = manager.get_stats()
    return jsonify(stats)

@app.route('/api/sessions/recent')
def api_recent_sessions():
    """Get recent sessions"""
    limit = request.args.get('limit', 50, type=int)

    conn = sqlite3.connect(manager.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM recent_sessions
        LIMIT ?
    """, (limit,))

    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(sessions)

@app.route('/api/projects')
def api_projects():
    """Get project statistics"""
    conn = sqlite3.connect(manager.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM project_stats")
    projects = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(projects)

@app.route('/api/knowledge')
def api_knowledge():
    """Get knowledge base entries"""
    category = request.args.get('category', None)

    conn = sqlite3.connect(manager.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if category:
        cursor.execute("""
            SELECT * FROM knowledge_base
            WHERE category = ?
            ORDER BY frequency DESC, last_used DESC
            LIMIT 100
        """, (category,))
    else:
        cursor.execute("""
            SELECT * FROM knowledge_base
            ORDER BY frequency DESC, last_used DESC
            LIMIT 100
        """)

    knowledge = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(knowledge)

@app.route('/api/timeline')
def api_timeline():
    """Get activity timeline"""
    days = request.args.get('days', 30, type=int)

    conn = sqlite3.connect(manager.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            DATE(start_time) as date,
            cli_tool,
            COUNT(*) as sessions,
            SUM(duration_seconds) as total_time
        FROM sessions
        WHERE start_time >= datetime('now', '-' || ? || ' days')
        GROUP BY DATE(start_time), cli_tool
        ORDER BY date DESC
    """, (days,))

    timeline = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(timeline)

@app.route('/api/files/top')
def api_top_files():
    """Get most modified files"""
    limit = request.args.get('limit', 20, type=int)

    conn = sqlite3.connect(manager.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            file_path,
            language,
            COUNT(*) as modifications,
            SUM(lines_added) as total_added,
            SUM(lines_removed) as total_removed
        FROM session_files
        GROUP BY file_path
        ORDER BY modifications DESC
        LIMIT ?
    """, (limit,))

    files = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(files)

@app.route('/api/search')
def api_search():
    """Search across memory"""
    query = request.args.get('q', '')

    if not query:
        return jsonify([])

    conn = sqlite3.connect(manager.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Search in knowledge base
    cursor.execute("""
        SELECT 'knowledge' as type, title, description, category, frequency
        FROM knowledge_base
        WHERE title LIKE ? OR description LIKE ?
        ORDER BY frequency DESC
        LIMIT 10
    """, (f'%{query}%', f'%{query}%'))

    results = [dict(row) for row in cursor.fetchall()]

    # Search in context
    cursor.execute("""
        SELECT DISTINCT 'context' as type, context_type, context_data
        FROM session_context
        WHERE context_data LIKE ?
        LIMIT 10
    """, (f'%{query}%',))

    results.extend([dict(row) for row in cursor.fetchall()])

    conn.close()

    return jsonify(results)

def create_html_template():
    """Create dashboard HTML template"""
    template_dir = os.path.expanduser("~/ai-cli-memory-system/templates")
    os.makedirs(template_dir, exist_ok=True)

    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI CLI Memory Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .stat-card h3 {
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        .stat-card .value {
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }
        .stat-card .label {
            color: #666;
            margin-top: 5px;
        }
        .content-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .panel {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .panel h2 {
            color: #667eea;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .session-item, .project-item, .knowledge-item {
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            background: #f8f9fa;
        }
        .session-item:hover, .project-item:hover, .knowledge-item:hover {
            background: #e9ecef;
        }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            margin-right: 5px;
        }
        .badge-claude { background: #8b5cf6; color: white; }
        .badge-codex { background: #22c55e; color: white; }
        .badge-gemini { background: #3b82f6; color: white; }
        .timeline {
            height: 200px;
            margin-top: 20px;
        }
        @media (max-width: 768px) {
            .content-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 AI CLI Memory Dashboard</h1>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Sessions</h3>
                <div class="value" id="total-sessions">-</div>
                <div class="label">All time</div>
            </div>
            <div class="stat-card">
                <h3>Total Time</h3>
                <div class="value" id="total-time">-</div>
                <div class="label">Hours tracked</div>
            </div>
            <div class="stat-card">
                <h3>Projects</h3>
                <div class="value" id="total-projects">-</div>
                <div class="label">Active projects</div>
            </div>
            <div class="stat-card">
                <h3>Knowledge Base</h3>
                <div class="value" id="total-knowledge">-</div>
                <div class="label">Learned patterns</div>
            </div>
        </div>

        <div class="content-grid">
            <div class="panel">
                <h2>Recent Sessions</h2>
                <div id="recent-sessions"></div>
            </div>

            <div class="panel">
                <h2>Top Projects</h2>
                <div id="top-projects"></div>
            </div>

            <div class="panel">
                <h2>Activity Timeline</h2>
                <div id="timeline" class="timeline"></div>
            </div>

            <div class="panel">
                <h2>Knowledge Base</h2>
                <div id="knowledge-base"></div>
            </div>
        </div>
    </div>

    <script>
        async function loadStats() {
            const res = await fetch('/api/stats');
            const stats = await res.json();

            let totalSessions = 0;
            let totalTime = 0;

            for (const [tool, data] of Object.entries(stats.by_tool || {})) {
                totalSessions += data.sessions;
                totalTime += data.total_time || 0;
            }

            document.getElementById('total-sessions').textContent = totalSessions;
            document.getElementById('total-time').textContent = Math.round(totalTime / 3600);
            document.getElementById('total-projects').textContent = stats.top_projects?.length || 0;
        }

        async function loadRecentSessions() {
            const res = await fetch('/api/sessions/recent?limit=10');
            const sessions = await res.json();

            const html = sessions.map(s => `
                <div class="session-item">
                    <span class="badge badge-${s.cli_tool}">${s.cli_tool}</span>
                    <strong>${s.working_dir.split('/').pop()}</strong>
                    <div style="font-size: 0.9em; color: #666; margin-top: 5px;">
                        ${new Date(s.start_time).toLocaleString()} • ${Math.round(s.duration_seconds / 60)}m
                    </div>
                </div>
            `).join('');

            document.getElementById('recent-sessions').innerHTML = html;
        }

        async function loadProjects() {
            const res = await fetch('/api/projects');
            const projects = await res.json();

            const html = projects.slice(0, 10).map(p => `
                <div class="project-item">
                    <strong>${p.project_name || 'Unknown'}</strong>
                    <div style="font-size: 0.9em; color: #666; margin-top: 5px;">
                        ${p.session_count} sessions • ${Math.round(p.total_time_seconds / 3600)}h
                    </div>
                </div>
            `).join('');

            document.getElementById('top-projects').innerHTML = html;
        }

        async function loadKnowledge() {
            const res = await fetch('/api/knowledge');
            const knowledge = await res.json();

            const html = knowledge.slice(0, 10).map(k => `
                <div class="knowledge-item">
                    <strong>${k.title}</strong>
                    <div style="font-size: 0.9em; color: #666; margin-top: 5px;">
                        ${k.description.substring(0, 100)}...
                    </div>
                    <div style="font-size: 0.8em; color: #999; margin-top: 5px;">
                        Used ${k.frequency} times
                    </div>
                </div>
            `).join('');

            document.getElementById('knowledge-base').innerHTML = html;
            document.getElementById('total-knowledge').textContent = knowledge.length;
        }

        // Load all data
        loadStats();
        loadRecentSessions();
        loadProjects();
        loadKnowledge();

        // Refresh every 30 seconds
        setInterval(() => {
            loadStats();
            loadRecentSessions();
        }, 30000);
    </script>
</body>
</html>"""

    with open(os.path.join(template_dir, 'dashboard.html'), 'w') as f:
        f.write(html)

if __name__ == '__main__':
    from flask import request

    # Create template
    create_html_template()

    # Set Flask template folder
    app.template_folder = os.path.expanduser("~/ai-cli-memory-system/templates")

    print("🚀 Starting AI CLI Memory Dashboard...")
    print("📊 Open: http://localhost:5555")
    print("Press Ctrl+C to stop")

    app.run(host='0.0.0.0', port=5555, debug=False)
