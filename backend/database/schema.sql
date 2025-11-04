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

-- Matches table: All match results (denormalized with player names)
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    team2_elo_change REAL
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

-- Indexes for read performance
CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(date DESC);
CREATE INDEX IF NOT EXISTS idx_matches_team1_p1 ON matches(team1_player1_id);
CREATE INDEX IF NOT EXISTS idx_matches_team1_p2 ON matches(team1_player2_id);
CREATE INDEX IF NOT EXISTS idx_matches_team2_p1 ON matches(team2_player1_id);
CREATE INDEX IF NOT EXISTS idx_matches_team2_p2 ON matches(team2_player2_id);
CREATE INDEX IF NOT EXISTS idx_partnership_stats_player ON partnership_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_opponent_stats_player ON opponent_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_elo_history_player ON elo_history(player_id);
CREATE INDEX IF NOT EXISTS idx_players_name ON players(name);

