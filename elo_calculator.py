"""
Beach Volleyball ELO Calculator - Core Logic

This module contains all the core ELO calculation logic extracted from match.py.
It's independent of Google Sheets and can work with any data source.
"""

import pandas as pd
import math
import json
import os

#####################################################
# CONSTANTS                                         #
#####################################################

K = 40
INITIAL_ELO = 1200
USE_POINT_DIFFERENTIAL = False  # Set to True to factor in margin of victory


#####################################################
# UTILITY FUNCTIONS                                 #
#####################################################

def convertNumber(x):
    """Round numbers to 2 decimal places."""
    try:
        return round(x, 2)
    except:
        return x


def expectedScore(eloA, eloB):
    """Calculate expected score for player A against player B using ELO formula."""
    return 1 / (1 + 10**((eloA - eloB) / 400))


def eloChange(k, old_elo, expectedV, win):
    """Calculate ELO rating change."""
    return k * (win - expectedV)


def kFunction(avg_games):
    """Calculate K-factor based on average games played."""
    return K


#####################################################
# CLASSES                                           #
#####################################################

class Match:
    """Represents a beach volleyball match between two teams."""
    
    def __init__(self, p1, p2, p3, p4, scores, date=None):
        """
        Initialize a match.
        
        Args:
            p1, p2: Players on team 0
            p3, p4: Players on team 1
            scores: List of [team0_score, team1_score]
            date: Optional date string for the match
        """
        self.players = [[p1, p2], [p3, p4]]
        self.date = date
        self.elo_deltas = [None, None]  # Will store [team0_delta, team1_delta]
        
        # Store original scores for point differential tracking
        self.original_scores = [int(scores[0]), int(scores[1])]
        
        # Determine winner
        if int(scores[0]) > int(scores[1]):
            self.winner = 0
        elif int(scores[1]) > int(scores[0]):
            self.winner = 1
        else:
            self.winner = -1
        
        # Normalize score to 0-1 range
        if self.winner != -1:
            if USE_POINT_DIFFERENTIAL:
                # Factor in point differential
                normalisation_factor = 10 - int(scores[self.winner])
                scores[0] = float(scores[0]) + normalisation_factor
                scores[1] = float(scores[1]) + normalisation_factor
                self.score = float(scores[0]) / (float(scores[0]) + float(scores[1]))
            else:
                # Simple win/loss: winner gets 1.0, loser gets 0.0
                self.score = 1.0 if self.winner == 0 else 0.0
        else:
            # Tie
            self.score = 0.5


class PlayerStats:
    """Encapsulates all statistics for a single player."""
    
    def __init__(self, name):
        self.name = name
        self.elo = INITIAL_ELO
        self.game_count = 0
        self.win_count = 0
        self.wins_with = {}      # wins partnered with each player
        self.games_with = {}     # games partnered with each player
        self.wins_against = {}   # wins against each player
        self.games_against = {}  # games against each player
        self.elo_history = []
        self.date_history = []   # dates corresponding to elo_history
        
        # Point differential tracking
        self.total_point_diff = 0
        self.point_diff_with = {}    # point differential with each partner
        self.point_diff_against = {} # point differential against each opponent
    
    @property
    def win_rate(self):
        """Calculate overall win rate."""
        if self.game_count == 0:
            return 0
        return self.win_count / self.game_count
    
    @property
    def avg_point_diff(self):
        """Calculate average point differential."""
        if self.game_count == 0:
            return 0
        return self.total_point_diff / self.game_count
    
    @property
    def points(self):
        """Calculate points: +3 for each win, +1 for each loss."""
        losses = self.game_count - self.win_count
        return (self.win_count * 3) + (losses * 1)
    
    def record_game_with(self, partner):
        """Record a game played with a partner."""
        if partner not in self.games_with:
            self.games_with[partner] = 0
        self.games_with[partner] += 1
    
    def record_win_with(self, partner):
        """Record a win with a partner."""
        if partner not in self.wins_with:
            self.wins_with[partner] = 0
        self.wins_with[partner] += 1
    
    def record_game_against(self, opponent):
        """Record a game played against an opponent."""
        if opponent not in self.games_against:
            self.games_against[opponent] = 0
        self.games_against[opponent] += 1
    
    def record_win_against(self, opponent):
        """Record a win against an opponent."""
        if opponent not in self.wins_against:
            self.wins_against[opponent] = 0
        self.wins_against[opponent] += 1
    
    def record_point_diff_with(self, partner, diff):
        """Record point differential with a partner."""
        if partner not in self.point_diff_with:
            self.point_diff_with[partner] = 0
        self.point_diff_with[partner] += diff
    
    def record_point_diff_against(self, opponent, diff):
        """Record point differential against an opponent."""
        if opponent not in self.point_diff_against:
            self.point_diff_against[opponent] = 0
        self.point_diff_against[opponent] += diff
    
    def update_elo(self, delta, date=None):
        """Update ELO rating and record history."""
        self.elo += delta
        self.elo_history.append(self.elo)
        self.date_history.append(date)


class StatsTracker:
    """Tracks statistics for all players across multiple matches."""
    
    def __init__(self):
        self.players = {}
    
    def get_player(self, name):
        """Get or create a player's stats."""
        if name not in self.players:
            self.players[name] = PlayerStats(name)
        return self.players[name]
    
    def process_match(self, match):
        """Process a single match and update all relevant statistics."""
        # Ensure all players exist
        all_players = match.players[0] + match.players[1]
        for player_name in all_players:
            self.get_player(player_name)
        
        # Record games and partnerships
        self._record_games_and_partnerships(match)
        
        # Record wins if there was a winner
        if match.winner != -1:
            self._record_wins(match)
        
        # Record point differentials
        self._record_point_differentials(match)
        
        # Calculate and apply ELO changes
        self._update_elos(match)
    
    def _record_games_and_partnerships(self, match):
        """Record games played and partnerships."""
        for team_idx, team in enumerate(match.players):
            opponent_team = match.players[(team_idx + 1) % 2]
            
            # Handle teams (different logic for solo vs pair)
            if team[0] == team[1]:
                # Solo player (playing with themselves)
                player = self.get_player(team[0])
                player.game_count += 1
                player.record_game_with(team[0])
                
                # Record games against opponents
                for opponent in opponent_team:
                    if opponent != opponent_team[0] or opponent != opponent_team[1]:
                        player.record_game_against(opponent)
            else:
                # Pair of different players
                for player_name in team:
                    player = self.get_player(player_name)
                    player.game_count += 1
                    
                    # Record partnership
                    partner = team[1] if player_name == team[0] else team[0]
                    player.record_game_with(partner)
                    
                    # Record games against opponents
                    for opponent in opponent_team:
                        player.record_game_against(opponent)
    
    def _record_wins(self, match):
        """Record wins for the winning team."""
        winning_team = match.players[match.winner]
        losing_team = match.players[(match.winner + 1) % 2]
        
        if winning_team[0] == winning_team[1]:
            # Solo player win
            player = self.get_player(winning_team[0])
            player.win_count += 1
            player.record_win_with(winning_team[0])
            
            # Record wins against opponents
            for opponent in losing_team:
                player.record_win_against(opponent)
        else:
            # Pair win
            for player_name in winning_team:
                player = self.get_player(player_name)
                player.win_count += 1
                
                # Record win with partner
                partner = winning_team[1] if player_name == winning_team[0] else winning_team[0]
                player.record_win_with(partner)
                
                # Record wins against opponents
                for opponent in losing_team:
                    player.record_win_against(opponent)
    
    def _record_point_differentials(self, match):
        """Record point differentials for all players."""
        # Calculate point differential for each team
        point_diff_team0 = match.original_scores[0] - match.original_scores[1]
        point_diff_team1 = match.original_scores[1] - match.original_scores[0]
        
        # Record for team 0
        team0 = match.players[0]
        team1 = match.players[1]
        
        for player_name in team0:
            player = self.get_player(player_name)
            player.total_point_diff += point_diff_team0
            
            # Record with partner
            partner = team0[1] if player_name == team0[0] else team0[0]
            player.record_point_diff_with(partner, point_diff_team0)
            
            # Record against opponents
            for opponent in team1:
                player.record_point_diff_against(opponent, point_diff_team0)
        
        # Record for team 1
        for player_name in team1:
            player = self.get_player(player_name)
            player.total_point_diff += point_diff_team1
            
            # Record with partner
            partner = team1[1] if player_name == team1[0] else team1[0]
            player.record_point_diff_with(partner, point_diff_team1)
            
            # Record against opponents
            for opponent in team0:
                player.record_point_diff_against(opponent, point_diff_team1)
    
    def _update_elos(self, match):
        """Calculate and apply ELO changes for all players in the match."""
        # Calculate team average ELOs
        team_elos = []
        for team in match.players:
            player1 = self.get_player(team[0])
            player2 = self.get_player(team[1])
            team_elo = (player1.elo + player2.elo) / 2
            team_elos.append(team_elo)
        
        # Calculate expected scores
        expected = [
            expectedScore(team_elos[1], team_elos[0]),
            expectedScore(team_elos[0], team_elos[1])
        ]
        
        # Calculate K-factor based on average games played
        avg_games = sum(self.get_player(p).game_count for team in match.players for p in team) / 4
        k = kFunction(avg_games)
        
        # Calculate ELO deltas
        deltas = [
            eloChange(k, team_elos[0], expected[0], match.score),
            eloChange(k, team_elos[1], expected[1], 1 - match.score)
        ]
        
        # Store deltas in match object for later writing back to sheet
        match.elo_deltas = deltas
        
        # Apply ELO changes
        for team_idx, team in enumerate(match.players):
            for player_name in team:
                player = self.get_player(player_name)
                player.update_elo(deltas[team_idx], match.date)


#####################################################
# DATAFRAME CREATION FUNCTIONS                      #
#####################################################

def create_ranking_dataframe(tracker):
    """
    Create a DataFrame with player rankings and statistics.
    
    Args:
        tracker: StatsTracker object with all player stats
        
    Returns:
        DataFrame with rankings (sorted by Points)
    """
    # Sort players by Points (highest to lowest)
    sorted_players = sorted(
        tracker.players.values(),
        key=lambda p: p.points,
        reverse=True
    )
    
    # Create DataFrame
    data = []
    for player in sorted_players:
        losses = player.game_count - player.win_count
        win_rate = round(player.win_rate, 3)  # Rate from 0 to 1
        avg_pt_diff = round(player.avg_point_diff, 1)
        
        data.append({
            'Name': player.name,
            'Points': player.points,
            'Games': player.game_count,
            'Win Rate': win_rate,
            'Wins': player.win_count,
            'Losses': losses,
            'Avg Pt Diff': avg_pt_diff,
            'ELO': int(round(player.elo))
        })
    
    return pd.DataFrame(data)


def create_elo_timeline_dataframe(tracker):
    """
    Create a DataFrame with ELO timeline data for graphing.
    
    Args:
        tracker: StatsTracker object
        
    Returns:
        DataFrame with Date column and one column per player showing ELO over time
    """
    # Collect all unique dates and create a timeline
    all_dates = set()
    for player in tracker.players.values():
        all_dates.update([d for d in player.date_history if d])
    
    if not all_dates:
        # No dates available, return empty dataframe
        return pd.DataFrame()
    
    # Sort dates
    sorted_dates = sorted(list(all_dates))
    
    # Build the timeline data
    timeline_data = {'Date': sorted_dates}
    
    for player_name, player in sorted(tracker.players.items()):
        # Create a mapping of date to ELO for this player
        elo_by_date = {}
        current_elo = INITIAL_ELO
        
        for date, elo in zip(player.date_history, player.elo_history):
            if date:
                elo_by_date[date] = elo
                current_elo = elo
        
        # Fill in ELO values for each date (carry forward last known ELO)
        player_elos = []
        last_elo = INITIAL_ELO
        
        for date in sorted_dates:
            if date in elo_by_date:
                last_elo = elo_by_date[date]
            player_elos.append(round(last_elo, 1))
        
        timeline_data[player_name] = player_elos
    
    return pd.DataFrame(timeline_data)


def create_player_combined_dataframe(player_stats):
    """
    Create a combined DataFrame with overall, partnership, and opponent statistics for a single player.
    
    Args:
        player_stats: PlayerStats object
        
    Returns:
        DataFrame with all player statistics
    """
    data = []
    
    # Add overall summary at the top
    overall_losses = player_stats.game_count - player_stats.win_count
    data.append({
        'Partner/Opponent': 'OVERALL',
        'Points': player_stats.points,
        'Games': player_stats.game_count,
        'Wins': player_stats.win_count,
        'Losses': overall_losses,
        'Win Rate': round(player_stats.win_rate, 3),
        'Avg Pt Diff': round(player_stats.avg_point_diff, 1)
    })
    
    # Add spacing
    data.append({
        'Partner/Opponent': '',
        'Points': '',
        'Games': '',
        'Wins': '',
        'Losses': '',
        'Win Rate': '',
        'Avg Pt Diff': ''
    })
    
    # Add partnership section
    data.append({
        'Partner/Opponent': 'WITH PARTNERS',
        'Points': '',
        'Games': '',
        'Wins': '',
        'Losses': '',
        'Win Rate': '',
        'Avg Pt Diff': ''
    })
    
    # Get all partners
    all_partners = set(player_stats.games_with.keys())
    partner_data = []
    
    for partner in all_partners:
        games = player_stats.games_with.get(partner, 0)
        wins = player_stats.wins_with.get(partner, 0)
        losses = games - wins
        win_rate = round((wins / games), 3) if games > 0 else 0.0
        
        total_pt_diff = player_stats.point_diff_with.get(partner, 0)
        avg_pt_diff = round(total_pt_diff / games, 1) if games > 0 else 0.0
        partner_points = (wins * 3) + (losses * 1)
        
        partner_data.append({
            'Partner/Opponent': partner,
            'Points': partner_points,
            'Games': games,
            'Wins': wins,
            'Losses': losses,
            'Win Rate': win_rate,
            'Avg Pt Diff': avg_pt_diff
        })
    
    # Sort by games and add to data
    partner_data.sort(key=lambda x: x['Games'], reverse=True)
    data.extend(partner_data)
    
    # Add spacing
    data.append({
        'Partner/Opponent': '',
        'Points': '',
        'Games': '',
        'Wins': '',
        'Losses': '',
        'Win Rate': '',
        'Avg Pt Diff': ''
    })
    
    # Add opponent section
    data.append({
        'Partner/Opponent': 'VS OPPONENTS',
        'Points': '',
        'Games': '',
        'Wins': '',
        'Losses': '',
        'Win Rate': '',
        'Avg Pt Diff': ''
    })
    
    # Get all opponents
    all_opponents = set(player_stats.games_against.keys())
    opponent_data = []
    
    for opponent in all_opponents:
        games = player_stats.games_against.get(opponent, 0)
        wins = player_stats.wins_against.get(opponent, 0)
        losses = games - wins
        win_rate = round((wins / games), 3) if games > 0 else 0.0
        
        total_pt_diff = player_stats.point_diff_against.get(opponent, 0)
        avg_pt_diff = round(total_pt_diff / games, 1) if games > 0 else 0.0
        opponent_points = (wins * 3) + (losses * 1)
        
        opponent_data.append({
            'Partner/Opponent': opponent,
            'Points': opponent_points,
            'Games': games,
            'Wins': wins,
            'Losses': losses,
            'Win Rate': win_rate,
            'Avg Pt Diff': avg_pt_diff
        })
    
    # Sort by games and add to data
    opponent_data.sort(key=lambda x: x['Games'], reverse=True)
    data.extend(opponent_data)
    
    return pd.DataFrame(data)


#####################################################
# COMPUTATION FUNCTION                              #
#####################################################

def process_matches(match_list):
    """
    Process a list of matches and return the stats tracker.
    
    Args:
        match_list: List of Match objects
        
    Returns:
        StatsTracker object with all computed stats
    """
    tracker = StatsTracker()
    for match in match_list:
        tracker.process_match(match)
    return tracker


#####################################################
# JSON OUTPUT FUNCTIONS                             #
#####################################################

def create_matches_dataframe(match_list):
    """
    Create a DataFrame with all match data.
    
    Args:
        match_list: List of Match objects
        
    Returns:
        DataFrame with match details (sorted by date, most recent first)
    """
    data = []
    
    for match in match_list:
        data.append({
            'Date': match.date or '',
            'Team 1 Player 1': match.players[0][0],
            'Team 1 Player 2': match.players[0][1],
            'Team 2 Player 1': match.players[1][0],
            'Team 2 Player 2': match.players[1][1],
            'Team 1 Score': match.original_scores[0],
            'Team 2 Score': match.original_scores[1],
            'Winner': f"Team {match.winner + 1}" if match.winner != -1 else "Tie",
            'Team 1 ELO Change': round(match.elo_deltas[0], 1) if match.elo_deltas[0] is not None else 0,
            'Team 2 ELO Change': round(match.elo_deltas[1], 1) if match.elo_deltas[1] is not None else 0
        })
    
    df = pd.DataFrame(data)
    
    # Sort by date (most recent first) if dates are available
    if 'Date' in df.columns and df['Date'].notna().any():
        df = df.sort_values('Date', ascending=False)
    
    return df


def create_player_match_history(match_list, player_name):
    """
    Create a DataFrame with match history for a specific player.
    
    Args:
        match_list: List of Match objects
        player_name: Name of the player
        
    Returns:
        DataFrame with player's match history (most recent first)
    """
    data = []
    
    for match in match_list:
        # Check if player is in this match
        all_players = match.players[0] + match.players[1]
        if player_name not in all_players:
            continue
        
        # Determine which team the player was on
        if player_name in match.players[0]:
            player_team = 0
            opponent_team = 1
            partner = match.players[0][1] if match.players[0][0] == player_name else match.players[0][0]
        else:
            player_team = 1
            opponent_team = 0
            partner = match.players[1][1] if match.players[1][0] == player_name else match.players[1][0]
        
        # Determine W/L
        if match.winner == player_team:
            result = 'W'
        elif match.winner == -1:
            result = 'T'
        else:
            result = 'L'
        
        # Get opponents
        opponent1 = match.players[opponent_team][0]
        opponent2 = match.players[opponent_team][1]
        
        # Get scores
        player_score = match.original_scores[player_team]
        opponent_score = match.original_scores[opponent_team]
        
        # Get ELO change for player's team
        elo_change = match.elo_deltas[player_team] if match.elo_deltas[player_team] is not None else 0
        
        data.append({
            'Date': match.date or '',
            'Partner': partner,
            'Opponent 1': opponent1,
            'Opponent 2': opponent2,
            'Result': result,
            'Score': f"{player_score}-{opponent_score}",
            'ELO Change': round(elo_change, 1)
        })
    
    df = pd.DataFrame(data)
    
    # Sort by date (most recent first) if dates are available
    if not df.empty and 'Date' in df.columns and df['Date'].notna().any():
        df = df.sort_values('Date', ascending=False)
    
    return df


def save_results_to_json(tracker, match_list, output_dir='output'):
    """
    Save all computed statistics to JSON files.
    
    Args:
        tracker: StatsTracker object with computed stats
        match_list: List of Match objects
        output_dir: Directory to save JSON files (default: 'output')
    """
    # Create output directories
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(f"{output_dir}/players", exist_ok=True)
    
    # Save rankings
    ranking_df = create_ranking_dataframe(tracker)
    ranking_df.to_json(f"{output_dir}/rankings.json", orient="records", indent=2)
    
    # Save ELO timeline
    timeline_df = create_elo_timeline_dataframe(tracker)
    if not timeline_df.empty:
        timeline_df.to_json(f"{output_dir}/elo_timeline.json", orient="records", indent=2)
    
    # Save all matches
    matches_df = create_matches_dataframe(match_list)
    matches_df.to_json(f"{output_dir}/matches.json", orient="records", indent=2)
    
    # Save individual player stats and match history
    for player_name, player_stats in tracker.players.items():
        player_df = create_player_combined_dataframe(player_stats)
        player_matches_df = create_player_match_history(match_list, player_name)
        
        # Sanitize filename (remove invalid characters)
        safe_name = "".join(c for c in player_name if c.isalnum() or c in (' ', '-', '_'))
        player_df.to_json(f"{output_dir}/players/{safe_name}.json", orient="records", indent=2)
        player_matches_df.to_json(f"{output_dir}/players/{safe_name}_matches.json", orient="records", indent=2)
    
    return {
        'rankings': f"{output_dir}/rankings.json",
        'timeline': f"{output_dir}/elo_timeline.json",
        'matches': f"{output_dir}/matches.json",
        'player_count': len(tracker.players)
    }

