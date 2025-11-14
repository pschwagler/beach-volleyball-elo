-- Beach Volleyball ELO Database Schema
-- Denormalized schema optimized for flush & repopulate pattern

-- Players table: Core player data and current stats
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    current_elo REAL NOT NULL DEFAULT 1200,
    games INTEGER NOT NULL DEFAULT 0,
    wins INTEGER NOT NULL DEFAULT 0,
    points INTEGER NOT NULL DEFAULT 0,
    win_rate REAL NOT NULL DEFAULT 0.0,
    avg_point_diff REAL NOT NULL DEFAULT 0.0
);

-- Sessions table: Gaming sessions grouped by date/time
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    name TEXT NOT NULL,
    is_pending INTEGER NOT NULL DEFAULT 1,  -- 1 = pending, 0 = submitted
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Matches table: All match results (denormalized with player names)
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,  -- NULL for legacy matches
    date TEXT NOT NULL,
    team1_player1_id INTEGER NOT NULL,
    team1_player1_name TEXT NOT NULL,
    team1_player2_id INTEGER NOT NULL,
    team1_player2_name TEXT NOT NULL,
    team2_player1_id INTEGER NOT NULL,
    team2_player1_name TEXT NOT NULL,
    team2_player2_id INTEGER NOT NULL,
    team2_player2_name TEXT NOT NULL,
    team1_score INTEGER NOT NULL,
    team2_score INTEGER NOT NULL,
    winner INTEGER NOT NULL,  -- 1 = team1, 2 = team2, -1 = tie
    team1_elo_change REAL,
    team2_elo_change REAL,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

-- Partnership stats: How each player performs WITH each partner (denormalized with names)
CREATE TABLE IF NOT EXISTS partnership_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    player_name TEXT NOT NULL,
    partner_id INTEGER NOT NULL,
    partner_name TEXT NOT NULL,
    games INTEGER NOT NULL DEFAULT 0,
    wins INTEGER NOT NULL DEFAULT 0,
    points INTEGER NOT NULL DEFAULT 0,
    win_rate REAL NOT NULL DEFAULT 0.0,
    avg_point_diff REAL NOT NULL DEFAULT 0.0
);

-- Opponent stats: How each player performs AGAINST each opponent (denormalized with names)
CREATE TABLE IF NOT EXISTS opponent_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    player_name TEXT NOT NULL,
    opponent_id INTEGER NOT NULL,
    opponent_name TEXT NOT NULL,
    games INTEGER NOT NULL DEFAULT 0,
    wins INTEGER NOT NULL DEFAULT 0,
    points INTEGER NOT NULL DEFAULT 0,
    win_rate REAL NOT NULL DEFAULT 0.0,
    avg_point_diff REAL NOT NULL DEFAULT 0.0
);

-- ELO history: Track ELO changes over time for charting
CREATE TABLE IF NOT EXISTS elo_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    player_name TEXT NOT NULL,
    match_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    elo_after REAL NOT NULL,
    elo_change REAL NOT NULL
);

-- Settings table: Application configuration
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Users table: User accounts with phone-based authentication
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT NOT NULL,  -- E.164 format, NOT unique (allows multiple unverified)
    password_hash TEXT,  -- nullable for passwordless users
    name TEXT,
    email TEXT,
    is_verified INTEGER NOT NULL DEFAULT 0,  -- 0 = unverified, 1 = verified
    failed_verification_attempts INTEGER NOT NULL DEFAULT 0,  -- Track failed verification attempts
    locked_until TEXT,  -- ISO timestamp when account lock expires (NULL if not locked)
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Verification codes table: SMS verification codes
CREATE TABLE IF NOT EXISTS verification_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT NOT NULL,
    code TEXT NOT NULL,  -- 6-digit code
    expires_at TEXT NOT NULL,
    used INTEGER NOT NULL DEFAULT 0,  -- 0 = unused, 1 = used
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Refresh tokens table: JWT refresh tokens for token rotation
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT NOT NULL UNIQUE,  -- The refresh token itself
    expires_at TEXT NOT NULL,  -- ISO timestamp when token expires
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for read performance
CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_pending ON sessions(is_pending);
CREATE INDEX IF NOT EXISTS idx_matches_session ON matches(session_id);
CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(date DESC);
CREATE INDEX IF NOT EXISTS idx_matches_team1_p1 ON matches(team1_player1_id);
CREATE INDEX IF NOT EXISTS idx_matches_team1_p2 ON matches(team1_player2_id);
CREATE INDEX IF NOT EXISTS idx_matches_team2_p1 ON matches(team2_player1_id);
CREATE INDEX IF NOT EXISTS idx_matches_team2_p2 ON matches(team2_player2_id);
CREATE INDEX IF NOT EXISTS idx_partnership_stats_player ON partnership_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_opponent_stats_player ON opponent_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_elo_history_player ON elo_history(player_id);
CREATE INDEX IF NOT EXISTS idx_players_name ON players(name);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number);
CREATE INDEX IF NOT EXISTS idx_users_phone_verified ON users(phone_number, is_verified);
CREATE INDEX IF NOT EXISTS idx_verification_codes_phone ON verification_codes(phone_number);
CREATE INDEX IF NOT EXISTS idx_verification_codes_expires ON verification_codes(expires_at);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires ON refresh_tokens(expires_at);

