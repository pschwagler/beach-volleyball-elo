"""
Data service layer for database operations.
Handles all CRUD operations for the ELO system.
"""

from typing import List, Dict, Optional
from backend.database import db

def flush_and_repopulate(tracker, match_list):
    """
    Flush all data and repopulate from calculated statistics.
    
    Args:
        tracker: StatsTracker object with all calculated stats
        match_list: List of Match objects with ELO deltas
    """
    # Flush all tables
    db.flush_all_tables()
    
    # Get or create player IDs (need to do this first)
    player_id_map = {}
    
    with db.get_db() as conn:
        # Prepare all player data with explicit IDs
        player_data = []
        player_id_map = {}
        for player_id, (name, stats) in enumerate(tracker.players.items(), start=1):
            player_id_map[name] = player_id
            player_data.append((
                player_id, name, round(stats.elo, 2), stats.game_count, stats.win_count,
                stats.points, round(stats.win_rate, 3), round(stats.avg_point_diff, 1)
            ))

        # Single batch insert with explicit IDs
        conn.executemany(
            """INSERT INTO players (id, name, current_elo, games, wins, points, win_rate, avg_point_diff)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            player_data
        )
        
        # Prepare all match data with explicit IDs
        match_data = []
        match_id_map = {}
        for match_id, match in enumerate(match_list, start=1):
            match_id_map[id(match)] = match_id
            team1_p1_name, team1_p2_name = match.players[0]
            team2_p1_name, team2_p2_name = match.players[1]
            match_data.append((
                match_id,
                match.date or '',
                player_id_map[team1_p1_name], team1_p1_name,
                player_id_map[team1_p2_name], team1_p2_name,
                player_id_map[team2_p1_name], team2_p1_name,
                player_id_map[team2_p2_name], team2_p2_name,
                match.original_scores[0], match.original_scores[1],
                match.winner,
                round(match.elo_deltas[0], 1) if match.elo_deltas[0] else 0,
                round(match.elo_deltas[1], 1) if match.elo_deltas[1] else 0
            ))

        # Batch insert matches with explicit IDs
        conn.executemany(
            """INSERT INTO matches (
                id, date, team1_player1_id, team1_player1_name, team1_player2_id, team1_player2_name,
                team2_player1_id, team2_player1_name, team2_player2_id, team2_player2_name,
                team1_score, team2_score, winner, team1_elo_change, team2_elo_change
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            match_data
        )
        
        # Prepare all partnership data
        partnership_data = []
        for player_name, player_stats in tracker.players.items():
            player_id = player_id_map[player_name]
            for partner_name, games in player_stats.games_with.items():
                wins = player_stats.wins_with.get(partner_name, 0)
                losses = games - wins
                win_rate = wins / games if games > 0 else 0
                points = (wins * 3) + (losses * 1)
                total_pt_diff = player_stats.point_diff_with.get(partner_name, 0)
                avg_pt_diff = total_pt_diff / games if games > 0 else 0
                
                partnership_data.append((
                    player_id, player_name,
                    player_id_map[partner_name], partner_name,
                    games, wins, points,
                    round(win_rate, 3), round(avg_pt_diff, 1)
                ))

        # Batch insert partnerships
        if partnership_data:
            conn.executemany(
                """INSERT INTO partnership_stats (
                    player_id, player_name, partner_id, partner_name,
                    games, wins, points, win_rate, avg_point_diff
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                partnership_data
            )
        
        # Prepare all opponent data
        opponent_data = []
        for player_name, player_stats in tracker.players.items():
            player_id = player_id_map[player_name]
            for opponent_name, games in player_stats.games_against.items():
                wins = player_stats.wins_against.get(opponent_name, 0)
                losses = games - wins
                win_rate = wins / games if games > 0 else 0
                points = (wins * 3) + (losses * 1)
                total_pt_diff = player_stats.point_diff_against.get(opponent_name, 0)
                avg_pt_diff = total_pt_diff / games if games > 0 else 0
                
                opponent_data.append((
                    player_id, player_name,
                    player_id_map[opponent_name], opponent_name,
                    games, wins, points,
                    round(win_rate, 3), round(avg_pt_diff, 1)
                ))

        # Batch insert opponents
        if opponent_data:
            conn.executemany(
                """INSERT INTO opponent_stats (
                    player_id, player_name, opponent_id, opponent_name,
                    games, wins, points, win_rate, avg_point_diff
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                opponent_data
            )
        
        # Prepare all ELO history data
        elo_history_data = []
        for player_name, player_stats in tracker.players.items():
            player_id = player_id_map[player_name]
            for match_ref, elo_after, elo_change, date in player_stats.match_elo_history:
                match_id = match_id_map.get(match_ref)
                if match_id:
                    elo_history_data.append((
                        player_id, player_name, match_id,
                        date or '',
                        round(elo_after, 1),
                        round(elo_change, 1)
                    ))

        # Batch insert ELO history
        if elo_history_data:
            conn.executemany(
                """INSERT INTO elo_history (
                    player_id, player_name, match_id, date, elo_after, elo_change
                   ) VALUES (?, ?, ?, ?, ?, ?)""",
                elo_history_data
            )


def get_rankings() -> List[Dict]:
    """Get current player rankings ordered by points."""
    with db.get_db() as conn:
        cursor = conn.execute(
            """SELECT name, points, games, win_rate, wins, 
                      (games - wins) as losses, avg_point_diff, current_elo
               FROM players
               ORDER BY points DESC, name ASC"""
        )
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "Name": row["name"],
                "Points": row["points"],
                "Games": row["games"],
                "Win Rate": row["win_rate"],
                "Wins": row["wins"],
                "Losses": row["losses"],
                "Avg Pt Diff": row["avg_point_diff"],
                "ELO": int(row["current_elo"])
            })
        
        return results


def get_player_stats(player_name: str) -> Optional[Dict]:
    """
    Get detailed stats for a player including partnerships and opponents.
    
    Returns dict with structure:
    {
        "overview": {"ranking": 1, "points": 100, "rating": 1500},
        "stats": [
            {"Partner/Opponent": "OVERALL", "Points": ..., ...},
            {"Partner/Opponent": "", ...},  # blank row
            {"Partner/Opponent": "WITH PARTNERS", ...},
            {"Partner/Opponent": "partner_name", ...},
            ...
            {"Partner/Opponent": "", ...},  # blank row
            {"Partner/Opponent": "VS OPPONENTS", ...},
            {"Partner/Opponent": "opponent_name", ...},
            ...
        ]
    }
    """
    with db.get_db() as conn:
        # Get overall player stats
        cursor = conn.execute(
            "SELECT * FROM players WHERE name = ?",
            (player_name,)
        )
        player_row = cursor.fetchone()
        
        if not player_row:
            return None
        
        # Calculate player's ranking
        cursor = conn.execute(
            """SELECT name FROM players 
               ORDER BY points DESC, avg_point_diff DESC, win_rate DESC, current_elo DESC"""
        )
        all_players = [row["name"] for row in cursor.fetchall()]
        ranking = all_players.index(player_name) + 1 if player_name in all_players else None
        
        # Build overview
        overview = {
            "ranking": ranking,
            "points": player_row["points"],
            "rating": int(player_row["current_elo"])
        }
        
        # Build results list
        results = []
        
        # Overall stats
        results.append({
            "Partner/Opponent": "OVERALL",
            "Points": player_row["points"],
            "Games": player_row["games"],
            "Wins": player_row["wins"],
            "Losses": player_row["games"] - player_row["wins"],
            "Win Rate": player_row["win_rate"],
            "Avg Pt Diff": player_row["avg_point_diff"]
        })
        
        # Blank row
        results.append({
            "Partner/Opponent": "",
            "Points": "",
            "Games": "",
            "Wins": "",
            "Losses": "",
            "Win Rate": "",
            "Avg Pt Diff": ""
        })
        
        # Partnership header
        results.append({
            "Partner/Opponent": "WITH PARTNERS",
            "Points": "",
            "Games": "",
            "Wins": "",
            "Losses": "",
            "Win Rate": "",
            "Avg Pt Diff": ""
        })
        
        # Partnership stats
        cursor = conn.execute(
            """SELECT partner_name, games, wins, points, win_rate, avg_point_diff
               FROM partnership_stats
               WHERE player_name = ?
               ORDER BY points DESC, win_rate DESC""",
            (player_name,)
        )
        
        for row in cursor.fetchall():
            results.append({
                "Partner/Opponent": row["partner_name"],
                "Points": row["points"],
                "Games": row["games"],
                "Wins": row["wins"],
                "Losses": row["games"] - row["wins"],
                "Win Rate": row["win_rate"],
                "Avg Pt Diff": row["avg_point_diff"]
            })
        
        # Blank row
        results.append({
            "Partner/Opponent": "",
            "Points": "",
            "Games": "",
            "Wins": "",
            "Losses": "",
            "Win Rate": "",
            "Avg Pt Diff": ""
        })
        
        # Opponent header
        results.append({
            "Partner/Opponent": "VS OPPONENTS",
            "Points": "",
            "Games": "",
            "Wins": "",
            "Losses": "",
            "Win Rate": "",
            "Avg Pt Diff": ""
        })
        
        # Opponent stats
        cursor = conn.execute(
            """SELECT opponent_name, games, wins, points, win_rate, avg_point_diff
               FROM opponent_stats
               WHERE player_name = ?
               ORDER BY points DESC, win_rate DESC""",
            (player_name,)
        )
        
        for row in cursor.fetchall():
            results.append({
                "Partner/Opponent": row["opponent_name"],
                "Points": row["points"],
                "Games": row["games"],
                "Wins": row["wins"],
                "Losses": row["games"] - row["wins"],
                "Win Rate": row["win_rate"],
                "Avg Pt Diff": row["avg_point_diff"]
            })
        
        return {
            "overview": overview,
            "stats": results
        }


def get_matches(limit: Optional[int] = None) -> List[Dict]:
    """Get all matches, optionally limited."""
    with db.get_db() as conn:
        query = """
            SELECT date, team1_player1_name, team1_player2_name,
                   team2_player1_name, team2_player2_name,
                   team1_score, team2_score, winner,
                   team1_elo_change, team2_elo_change
            FROM matches
            ORDER BY date DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor = conn.execute(query)
        
        results = []
        for row in cursor.fetchall():
            winner_text = "Tie"
            if row["winner"] == 1:
                winner_text = "Team 1"
            elif row["winner"] == 2:
                winner_text = "Team 2"
            
            results.append({
                "Date": row["date"],
                "Team 1 Player 1": row["team1_player1_name"],
                "Team 1 Player 2": row["team1_player2_name"],
                "Team 2 Player 1": row["team2_player1_name"],
                "Team 2 Player 2": row["team2_player2_name"],
                "Team 1 Score": row["team1_score"],
                "Team 2 Score": row["team2_score"],
                "Winner": winner_text,
                "Team 1 ELO Change": row["team1_elo_change"],
                "Team 2 ELO Change": row["team2_elo_change"]
            })
        
        return results


def get_player_match_history(player_name: str) -> List[Dict]:
    """Get match history for a specific player."""
    with db.get_db() as conn:
        # Get player ID
        cursor = conn.execute("SELECT id FROM players WHERE name = ?", (player_name,))
        player_row = cursor.fetchone()
        
        if not player_row:
            return []
        
        player_id = player_row["id"]
        
        # Get all matches where player participated, joined with ELO history
        cursor = conn.execute(
            """SELECT m.*, eh.elo_after
               FROM matches m
               LEFT JOIN elo_history eh ON eh.match_id = m.id AND eh.player_id = ?
               WHERE team1_player1_id = ? OR team1_player2_id = ?
                  OR team2_player1_id = ? OR team2_player2_id = ?
               ORDER BY m.id DESC""",
            (player_id, player_id, player_id, player_id, player_id)
        )
        
        results = []
        for row in cursor.fetchall():
            # Determine which team the player was on
            if row["team1_player1_id"] == player_id or row["team1_player2_id"] == player_id:
                # Player on team 1
                partner = row["team1_player2_name"] if row["team1_player1_id"] == player_id else row["team1_player1_name"]
                opponent1 = row["team2_player1_name"]
                opponent2 = row["team2_player2_name"]
                player_score = row["team1_score"]
                opponent_score = row["team2_score"]
                elo_change = row["team1_elo_change"]
                
                if row["winner"] == 1:
                    result = "W"
                elif row["winner"] == -1:
                    result = "T"
                else:
                    result = "L"
            else:
                # Player on team 2
                partner = row["team2_player2_name"] if row["team2_player1_id"] == player_id else row["team2_player1_name"]
                opponent1 = row["team1_player1_name"]
                opponent2 = row["team1_player2_name"]
                player_score = row["team2_score"]
                opponent_score = row["team1_score"]
                elo_change = row["team2_elo_change"]
                
                if row["winner"] == 2:
                    result = "W"
                elif row["winner"] == -1:
                    result = "T"
                else:
                    result = "L"
            
            results.append({
                "Date": row["date"],
                "Partner": partner,
                "Opponent 1": opponent1,
                "Opponent 2": opponent2,
                "Result": result,
                "Score": f"{player_score}-{opponent_score}",
                "ELO Change": elo_change,
                "ELO After": row["elo_after"]
            })
        
        return results


def get_elo_timeline() -> List[Dict]:
    """Get ELO timeline data for all players."""
    with db.get_db() as conn:
        # Get all unique dates
        cursor = conn.execute(
            "SELECT DISTINCT date FROM elo_history ORDER BY date ASC"
        )
        dates = [row["date"] for row in cursor.fetchall()]
        
        if not dates:
            return []
        
        # Get all players
        cursor = conn.execute("SELECT name FROM players ORDER BY name ASC")
        player_names = [row["name"] for row in cursor.fetchall()]
        
        # Build timeline data
        timeline = []
        for date in dates:
            row_data = {"Date": date}
            
            for player_name in player_names:
                # Get the ELO at this date for this player
                cursor = conn.execute(
                    """SELECT elo_after FROM elo_history
                       WHERE player_name = ? AND date <= ?
                       ORDER BY date DESC, id DESC
                       LIMIT 1""",
                    (player_name, date)
                )
                result = cursor.fetchone()
                
                if result:
                    row_data[player_name] = result["elo_after"]
                else:
                    # Player hasn't played yet at this date, use initial ELO
                    from backend.utils.constants import INITIAL_ELO
                    row_data[player_name] = INITIAL_ELO
            
            timeline.append(row_data)
        
        return timeline


def is_database_empty() -> bool:
    """Check if database is empty (no players)."""
    return db.is_database_empty()


def get_setting(key: str) -> Optional[str]:
    """
    Get a setting value by key.
    
    Args:
        key: Setting key (e.g., 'whatsapp_group_id')
        
    Returns:
        Setting value or None if not found
    """
    with db.get_db() as conn:
        cursor = conn.execute(
            "SELECT value FROM settings WHERE key = ?",
            (key,)
        )
        row = cursor.fetchone()
        return row["value"] if row else None


def set_setting(key: str, value: str) -> None:
    """
    Set a setting value (upsert).
    
    Args:
        key: Setting key
        value: Setting value
    """
    with db.get_db() as conn:
        conn.execute(
            """INSERT INTO settings (key, value, updated_at)
               VALUES (?, ?, CURRENT_TIMESTAMP)
               ON CONFLICT(key) DO UPDATE SET 
                   value = excluded.value,
                   updated_at = CURRENT_TIMESTAMP""",
            (key, value)
        )

