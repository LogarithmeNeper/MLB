import pybaseball
import pandas as pd
from statcast import create_report

calls = {
    'ball': 'green',
    'called_strike': 'red',
}

def prune_dataset(data: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only the rows that are called strikes outside the strikezone or balls inside the strikezone.

    Parameters
    ----------
    data : pd.DataFrame
        The data of the team.

    Returns
    -------
    pd.DataFrame
        The data of the team with only the rows that are called strikes outside the strikezone or balls inside the strikezone.
    """
    data = data[['plate_x', 'plate_z', 'description', 'delta_run_exp']]
    data = data[(data['description'] == 'called_strike') & (data.apply(lambda row: not inside_static_strikezone(row['plate_x'], row['plate_z']), axis=1)) | (data['description'] == 'ball') & (data.apply(lambda row: inside_static_strikezone(row['plate_x'], row['plate_z']), axis=1))]
    return data

def report_wrong_calls(data: pd.DataFrame, team: str) -> None:
    """
    Create a report of the wrong calls of an umpire.

    Parameters
    ----------
    data : pd.DataFrame
        The data of the team. 
            # It would be better to have the data of the whole game (both teams) but we can work with this for now.
    
    Returns
    -------
    None
    """
    gamedate = str(data['game_date'].unique()[0])[:10]
    home_team = data['home_team'].unique()[0]
    away_team = data['away_team'].unique()[0]
    outfolder = f"boxplot_{gamedate}"
    data = prune_dataset(data)
    return create_report(data, ['plate_x', 'plate_z'], 'description', calls, f"Wrong calls against {team} on {gamedate} [{away_team} @ {home_team}]", 'ump_report', f"ump_report_{team}_{gamedate}", True)

# TODO refactor using prune_dataset function.
def compute_static_scorecard_team(data: pd.DataFrame) -> float:
    """
    Computes the run advantage of a team based on the umpire's calls on the strikezone.

    Parameters
    ----------
    data : pd.DataFrame
        The data of the team's games.

    Returns
    -------
    float
        The run advantage of the team. (WIP)
    """
    batter_advantage, pitcher_advantage = 0, 0
    # Keep only the columns we need
    data = data[['plate_x', 'plate_z', 'description', 'delta_run_exp']]
    # Iterate over all pitches
    for i in range(len(data)):
        pos_x, pos_z, description, delta_run_exp = data.iloc[i]
        # Situation 1: called strike outside the strikezone, favouring the pitcher
        if description == 'called_strike' and not inside_static_strikezone(pos_x, pos_z):
            pitcher_advantage += abs(delta_run_exp)
        # Situation 2: called strike inside the strikezone, favouring the batter
        if description == 'ball' and inside_static_strikezone(pos_x, pos_z):
            batter_advantage += abs(delta_run_exp)
    return pitcher_advantage, batter_advantage

def inside_static_strikezone(pos_x: float, pos_z: float) -> bool:
    """
    Computes whether a pitch is inside the static strikezone. (independent of the batter's stance)

    Parameters
    ----------
    pos_x : float
        The x position of the pitch at the plate.

    pos_z : float
        The z position of the pitch at the plate.

    Returns
    -------
    bool
        Whether the pitch is inside the static strikezone.
    """
    return (pos_x >= -0.7083 and pos_x <= 0.7083 and pos_z >= 1.6 and pos_z <= 3.5)

if __name__ == '__main__':
    # Be careful with the dates especially when working at midnight ;)
    data = pybaseball.statcast(team='BOS')
    report_wrong_calls(data, 'BOS')

    data2 = pybaseball.statcast(team='TOR')
    report_wrong_calls(data2, 'TOR')
    # So far, this is (maybe still) incoherent with the @UmpScorecards twitter account. Have to double check.