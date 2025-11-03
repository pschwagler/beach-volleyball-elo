from typing import List
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import gspread_dataframe as gd
import math

#####################################################
# CONFIG STUFF                                      #
#####################################################
# Filename of file containing the credentials for   #
# accessing google services                         #
credentials_file = 'credentials.json'               #
# Name of the google sheet that should be used      #
# You can use either the sheet name or the ID       #
google_sheets_name = '1KZhd5prjzDjDTJCvg0b1fxVAM-uGDBxsHJJwKBKrBIA'#
#####################################################

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(
         credentials_file, scope)

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
    # """Calculate K-factor based on average games played."""
    # if avg_games > 100:
    #     return K
    # return 1 / (math.e**(avg_games - 5)) + K
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
# DATA LOADING AND PROCESSING                       #
#####################################################

def loadMatches(filename):
    """
    Load matches from a Google Sheet.
    
    Args:
        filename: Google Sheets name or ID
        
    Returns:
        List of Match objects
    """
    gc = gspread.authorize(credentials)
    
    # Try to open by ID first, then by name
    try:
        sh = gc.open_by_key(filename)
    except:
        sh = gc.open(filename)
    
    wks = sh.worksheet("Matches")
    data = wks.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)
    df.columns = ['DATE', 'T1P1', 'T1P2', 'T2P1', 'T2P2', 'T1SCORE', 'T2SCORE', 'T1ADJ', 'T2ADJ']

    match_list = []
    for _, row in df.iterrows():
        match = Match(
            row['T1P1'],
            row['T1P2'],
            row['T2P1'],
            row['T2P2'],
            [row['T1SCORE'], row['T2SCORE']],
            row['DATE']
        )
        match_list.append(match)
    
    return match_list


def computeStats(match_list, sheet_name):
    """
    Compute statistics for all matches and update the Google Sheet.
    
    Args:
        match_list: List of Match objects
        sheet_name: Google Sheets name or ID to update
    """
    # Process all matches
    tracker = StatsTracker()
    for match in match_list:
        tracker.process_match(match)
    
    # Generate output data
    ranking_df = create_ranking_dataframe(tracker)
    rank_changes_df = create_rank_changes_dataframe(tracker)
    elo_timeline_df = create_elo_timeline_dataframe(tracker)
    
    # Update spreadsheet
    update_spreadsheet(sheet_name, ranking_df, rank_changes_df, elo_timeline_df, tracker, match_list)


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


def create_rank_changes_dataframe(tracker):
    """
    Create a DataFrame with ELO history for all players.
    
    Args:
        tracker: StatsTracker object
        
    Returns:
        DataFrame with ELO history and Name column
    """
    # Build list of rows (one per player)
    data = []
    for player in tracker.players.values():
        row = {'Name': player.name}
        # Add each ELO value as a separate column
        for i, elo in enumerate(player.elo_history):
            row[f'Match{i+1}'] = convertNumber(elo)
        data.append(row)
    
    # Create DataFrame from list of dictionaries
    df = pd.DataFrame(data)
    
    return df


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


def create_player_partnership_dataframe(player_stats):
    """
    Create a DataFrame with partnership statistics for a single player.
    
    Args:
        player_stats: PlayerStats object
        
    Returns:
        DataFrame with partnership statistics (sorted by games played, descending)
    """
    data = []
    
    # Get all partners this player has played with
    all_partners = set(player_stats.games_with.keys())
    
    for partner in all_partners:
        games = player_stats.games_with.get(partner, 0)
        wins = player_stats.wins_with.get(partner, 0)
        losses = games - wins
        win_rate = round((wins / games), 3) if games > 0 else 0.0
        
        # Calculate average point differential with this partner
        total_pt_diff = player_stats.point_diff_with.get(partner, 0)
        avg_pt_diff = round(total_pt_diff / games, 1) if games > 0 else 0.0
        
        data.append({
            'Partner': partner,
            'Games': games,
            'Wins': wins,
            'Losses': losses,
            'Win Rate': win_rate,
            'Avg Pt Diff': avg_pt_diff
        })
    
    # Create DataFrame and sort by Games (descending)
    df = pd.DataFrame(data)
    df = df.sort_values('Games', ascending=False)
    
    return df


def create_player_opponent_dataframe(player_stats):
    """
    Create a DataFrame with opponent statistics for a single player.
    
    Args:
        player_stats: PlayerStats object
        
    Returns:
        DataFrame with opponent statistics (sorted by games played, descending)
    """
    data = []
    
    # Get all opponents this player has played against
    all_opponents = set(player_stats.games_against.keys())
    
    for opponent in all_opponents:
        games = player_stats.games_against.get(opponent, 0)
        wins = player_stats.wins_against.get(opponent, 0)
        losses = games - wins
        win_rate = round((wins / games), 3) if games > 0 else 0.0
        
        # Calculate average point differential against this opponent
        total_pt_diff = player_stats.point_diff_against.get(opponent, 0)
        avg_pt_diff = round(total_pt_diff / games, 1) if games > 0 else 0.0
        
        data.append({
            'Opponent': opponent,
            'Games': games,
            'Wins': wins,
            'Losses': losses,
            'Win Rate': win_rate,
            'Avg Pt Diff': avg_pt_diff
        })
    
    # Create DataFrame and sort by Games (descending)
    df = pd.DataFrame(data)
    df = df.sort_values('Games', ascending=False)
    
    return df


def write_elo_deltas_to_matches(sh, match_list):
    """
    Write ELO delta columns back to the Matches sheet.
    
    Args:
        sh: Spreadsheet object
        match_list: List of Match objects with calculated deltas
    """
    wks = sh.worksheet("Matches")
    
    # Fixed column positions for ELO deltas (columns 8 and 9)
    # DATE, T1P1, T1P2, T2P1, T2P2, T1SCORE, T2SCORE, T1ADJ, T2ADJ
    team1_col = 8
    team2_col = 9
    
    # Get current header to check if columns exist
    header_row = wks.row_values(1)
    
    # Write headers if they don't exist or are different
    if len(header_row) < team1_col or header_row[team1_col-1] != "Team 1 ELO +/-":
        wks.update_cell(1, team1_col, "Team 1 ELO +/-")
    if len(header_row) < team2_col or header_row[team2_col-1] != "Team 2 ELO +/-":
        wks.update_cell(1, team2_col, "Team 2 ELO +/-")
    
    # Prepare delta data and write in batch
    delta_values: List[List[float]] = []
    for match in match_list:
        if match.elo_deltas[0] is not None:
            delta_values.append([
                round(match.elo_deltas[0], 1),
                round(match.elo_deltas[1], 1)
            ])
        else:
            delta_values.append(['', ''])
    
    # Write all delta values at once (more efficient)
    if delta_values:
        end_row = len(delta_values) + 1
        range_name = f'H2:I{end_row}'
        wks.update(values=delta_values, range_name=range_name)


def update_spreadsheet(sheet_name, ranking_df, rank_changes_df, elo_timeline_df, tracker, match_list):
    """
    Update Google Sheets with computed statistics.
    
    Args:
        sheet_name: Google Sheets name or ID
        ranking_df: DataFrame with player rankings
        rank_changes_df: DataFrame with ELO history
        elo_timeline_df: DataFrame with ELO timeline for graphing
        tracker: StatsTracker object with all player data
        match_list: List of Match objects with calculated deltas
    """
    gc = gspread.authorize(credentials)
    
    # Try to open by ID first, then by name
    try:
        sh = gc.open_by_key(sheet_name)
    except:
        sh = gc.open(sheet_name)

    # Update Points worksheet
    try:
        ranking_wks = sh.worksheet("Points")
    except gspread.exceptions.WorksheetNotFound:
        # Create the worksheet if it doesn't exist
        ranking_wks = sh.add_worksheet(title="Points", rows=100, cols=20)
    gd.set_with_dataframe(ranking_wks, ranking_df)
    
    # Update Rank Changes worksheet
    try:
        rank_changes_wks = sh.worksheet("Rank Changes")
    except gspread.exceptions.WorksheetNotFound:
        # Create the worksheet if it doesn't exist
        rank_changes_wks = sh.add_worksheet(title="Rank Changes", rows=100, cols=100)
    gd.set_with_dataframe(rank_changes_wks, rank_changes_df)
    
    # Update ELO Timeline worksheet
    if not elo_timeline_df.empty:
        try:
            timeline_wks = sh.worksheet("ELO Timeline")
        except gspread.exceptions.WorksheetNotFound:
            # Create the worksheet if it doesn't exist
            timeline_wks = sh.add_worksheet(title="ELO Timeline", rows=500, cols=50)
        gd.set_with_dataframe(timeline_wks, elo_timeline_df)
    
    # Create/update individual player sheets with partnership and opponent stats
    print(f"Updating {len(tracker.players)} player sheets...")
    for idx, (player_name, player_stats) in enumerate(tracker.players.items()):
        print(f"  [{idx+1}/{len(tracker.players)}] Updating {player_name}...")
        
        partnership_df = create_player_partnership_dataframe(player_stats)
        opponent_df = create_player_opponent_dataframe(player_stats)
        
        # Combine both tables into one dataframe with headers
        # Create a combined dataframe with section headers
        combined_data = []
        
        # Add overall summary at the top
        overall_losses = player_stats.game_count - player_stats.win_count
        combined_data.append({
            'Section': 'OVERALL',
            'Col2': player_stats.points,
            'Col3': player_stats.game_count,
            'Col4': player_stats.win_count,
            'Col5': overall_losses,
            'Col6': round(player_stats.win_rate, 3),
            'Col7': round(player_stats.avg_point_diff, 1)
        })
        
        # Add spacing
        combined_data.append({'Section': '', 'Col2': '', 'Col3': '', 'Col4': '', 'Col5': '', 'Col6': '', 'Col7': ''})
        
        # Add partnership section
        combined_data.append({'Section': 'WITH PARTNERS', 'Col2': '', 'Col3': '', 'Col4': '', 'Col5': '', 'Col6': '', 'Col7': ''})
        for _, row in partnership_df.iterrows():
            # Calculate points for this partnership
            partner_games = row['Games']
            partner_wins = row['Wins']
            partner_losses = partner_games - partner_wins
            partner_points = (partner_wins * 3) + (partner_losses * 1)
            
            combined_data.append({
                'Section': row['Partner'],
                'Col2': partner_points,
                'Col3': row['Games'],
                'Col4': row['Wins'],
                'Col5': row['Losses'],
                'Col6': row['Win Rate'],
                'Col7': row['Avg Pt Diff']
            })
        
        # Add spacing
        combined_data.append({'Section': '', 'Col2': '', 'Col3': '', 'Col4': '', 'Col5': '', 'Col6': '', 'Col7': ''})
        
        # Add opponent section
        combined_data.append({'Section': 'VS OPPONENTS', 'Col2': '', 'Col3': '', 'Col4': '', 'Col5': '', 'Col6': '', 'Col7': ''})
        for _, row in opponent_df.iterrows():
            # Calculate points against this opponent
            opp_games = row['Games']
            opp_wins = row['Wins']
            opp_losses = opp_games - opp_wins
            opp_points = (opp_wins * 3) + (opp_losses * 1)
            
            combined_data.append({
                'Section': row['Opponent'],
                'Col2': opp_points,
                'Col3': row['Games'],
                'Col4': row['Wins'],
                'Col5': row['Losses'],
                'Col6': row['Win Rate'],
                'Col7': row['Avg Pt Diff']
            })
        
        combined_df = pd.DataFrame(combined_data)
        combined_df.columns = ['Partner/Opponent', 'Points', 'Games', 'Wins', 'Losses', 'Win Rate', 'Avg Pt Diff']
        
        # Try to find or create the player's worksheet
        try:
            player_wks = sh.worksheet(player_name)
        except gspread.exceptions.WorksheetNotFound:
            # Create the worksheet if it doesn't exist
            player_wks = sh.add_worksheet(title=player_name, rows=100, cols=10)
        
        # Write everything in ONE API call
        player_wks.clear()
        gd.set_with_dataframe(player_wks, combined_df, include_index=False, include_column_header=True, resize=True)
    
    # Write ELO deltas back to Matches sheet
    print("Writing ELO deltas to Matches sheet...")
    write_elo_deltas_to_matches(sh, match_list)
    
    # Also export rank changes to CSV
    rank_changes_df.to_csv("rank_changes.csv", index=False)


#####################################################
# MAIN EXECUTION                                    #
#####################################################

if __name__ == "__main__":
    match_list = loadMatches(google_sheets_name)
    computeStats(match_list, google_sheets_name)
