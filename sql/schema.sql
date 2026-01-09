-- AI CLI Contextual Memory System Schema
-- Supports Claude Code, Codex, Gemini, and other AI CLI tools

-- Main session tracking table
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cli_tool TEXT NOT NULL, -- 'claude', 'codex', 'gemini'
    session_id TEXT UNIQUE NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    working_dir TEXT NOT NULL,
    git_repo TEXT,
    git_branch TEXT,
    git_commit TEXT,
    exit_code INTEGER,
    duration_seconds INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Detailed context for each session
CREATE TABLE IF NOT EXISTS session_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    context_type TEXT NOT NULL, -- 'file_edit', 'command', 'decision', 'error', 'solution'
    context_data TEXT NOT NULL, -- JSON blob
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- Files modified during sessions
CREATE TABLE IF NOT EXISTS session_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    action TEXT NOT NULL, -- 'created', 'modified', 'deleted', 'read'
    language TEXT,
    lines_added INTEGER DEFAULT 0,
    lines_removed INTEGER DEFAULT 0,
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- Commands executed during sessions
CREATE TABLE IF NOT EXISTS session_commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    command TEXT NOT NULL,
    exit_code INTEGER,
    output_summary TEXT,
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- Key decisions and learnings
CREATE TABLE IF NOT EXISTS knowledge_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL, -- 'pattern', 'solution', 'gotcha', 'preference'
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    context TEXT, -- JSON: related files, technologies, etc.
    frequency INTEGER DEFAULT 1, -- How often this knowledge is accessed
    last_used DATETIME,
    source_sessions TEXT, -- JSON array of session_ids
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Project-specific memory
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_path TEXT UNIQUE NOT NULL,
    project_name TEXT,
    primary_language TEXT,
    framework TEXT,
    last_session_id TEXT,
    session_count INTEGER DEFAULT 0,
    total_time_seconds INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Project-specific patterns and preferences
CREATE TABLE IF NOT EXISTS project_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    pattern_type TEXT NOT NULL, -- 'architecture', 'testing', 'deployment', 'coding_style'
    pattern_data TEXT NOT NULL, -- JSON blob
    confidence REAL DEFAULT 0.5, -- 0.0 to 1.0
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Weekly summaries (compressed historical data)
CREATE TABLE IF NOT EXISTS weekly_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    week_number INTEGER NOT NULL,
    cli_tool TEXT NOT NULL,
    project_path TEXT,
    summary_data TEXT NOT NULL, -- JSON: key decisions, problems solved, patterns learned
    session_count INTEGER DEFAULT 0,
    total_time_seconds INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, week_number, cli_tool, project_path)
);

-- CLI tool versions and updates
CREATE TABLE IF NOT EXISTS cli_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_name TEXT NOT NULL,
    version TEXT NOT NULL,
    install_path TEXT,
    last_check DATETIME,
    update_available BOOLEAN DEFAULT 0,
    latest_version TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Cross-session entity tracking (integrates with MCP memory)
CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_name TEXT UNIQUE NOT NULL,
    entity_type TEXT NOT NULL, -- 'person', 'project', 'technology', 'file', 'concept'
    description TEXT,
    metadata TEXT, -- JSON blob
    reference_count INTEGER DEFAULT 0,
    last_referenced DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Relations between entities
CREATE TABLE IF NOT EXISTS entity_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_entity_id INTEGER NOT NULL,
    to_entity_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL, -- 'uses', 'depends_on', 'implements', 'fixes', 'blocks'
    strength REAL DEFAULT 0.5, -- 0.0 to 1.0
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_entity_id) REFERENCES entities(id),
    FOREIGN KEY (to_entity_id) REFERENCES entities(id),
    UNIQUE(from_entity_id, to_entity_id, relation_type)
);

-- Indexes for fast retrieval
CREATE INDEX IF NOT EXISTS idx_sessions_tool ON sessions(cli_tool);
CREATE INDEX IF NOT EXISTS idx_sessions_dir ON sessions(working_dir);
CREATE INDEX IF NOT EXISTS idx_sessions_start ON sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_context_session ON session_context(session_id);
CREATE INDEX IF NOT EXISTS idx_context_type ON session_context(context_type);
CREATE INDEX IF NOT EXISTS idx_files_session ON session_files(session_id);
CREATE INDEX IF NOT EXISTS idx_files_path ON session_files(file_path);
CREATE INDEX IF NOT EXISTS idx_commands_session ON session_commands(session_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_base(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_frequency ON knowledge_base(frequency DESC);
CREATE INDEX IF NOT EXISTS idx_projects_path ON projects(project_path);
CREATE INDEX IF NOT EXISTS idx_weekly_year_week ON weekly_summaries(year, week_number);
CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(entity_name);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_relations_from ON entity_relations(from_entity_id);
CREATE INDEX IF NOT EXISTS idx_relations_to ON entity_relations(to_entity_id);

-- Views for common queries
CREATE VIEW IF NOT EXISTS recent_sessions AS
SELECT
    s.session_id,
    s.cli_tool,
    s.working_dir,
    s.git_branch,
    s.start_time,
    s.duration_seconds,
    COUNT(DISTINCT sf.file_path) as files_modified,
    COUNT(DISTINCT sc.id) as commands_run
FROM sessions s
LEFT JOIN session_files sf ON s.session_id = sf.session_id
LEFT JOIN session_commands sc ON s.session_id = sc.session_id
WHERE s.start_time >= datetime('now', '-7 days')
GROUP BY s.session_id
ORDER BY s.start_time DESC;

CREATE VIEW IF NOT EXISTS project_stats AS
SELECT
    p.project_path,
    p.project_name,
    p.primary_language,
    p.session_count,
    p.total_time_seconds,
    COUNT(DISTINCT pp.id) as pattern_count,
    p.updated_at
FROM projects p
LEFT JOIN project_patterns pp ON p.id = pp.project_id
GROUP BY p.id
ORDER BY p.updated_at DESC;
