import pybaseball
import pandas as pd
from statcast import create_report, mlb_teams

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
    data = data[['plate_x', 'plate_z', 'description', 'delta_run_exp', 'sz_top', 'sz_bot']]
    data = data.dropna()
    data = data[(data['description'] == 'called_strike') & (data.apply(lambda row: not inside_variable_strikezone(row['plate_x'], row['plate_z'], row['sz_top'], row['sz_bot']), axis=1)) | (data['description'] == 'ball') & (data.apply(lambda row: inside_variable_strikezone(row['plate_x'], row['plate_z'], row['sz_top'], row['sz_bot']), axis=1))]
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
    outfolder = f"ump_report_{gamedate}"
    data = prune_dataset(data)
    data.to_csv('data.csv')
    pitcher_advantage, batter_advantage = compute_scorecard_team(data)
    return create_report(
        data,
        ['plate_x', 'plate_z'],
        'description',
        calls,
        f"Wrong calls for {team}'s pitchers on {gamedate} [{away_team}@{home_team}]\n Pitcher advantage: {pitcher_advantage:.2f} runs \n Opp. batters advantage: {batter_advantage:.2f} runs",
        outfolder, 
        f"ump_report_{team}_{gamedate}",
        radar_zone=False,
        strike_zone=True)

def compute_scorecard_team(data: pd.DataFrame) -> float:
    """
    Computes the run advantage of a team based on the umpire's calls on the strikezone.

    Parameters
    ----------
    data : pd.DataFrame
        The data of the team's games.

    Returns
    -------
    float, float
        The run advantage of the team's pitchers and opponent's batters.
    """
    batter_advantage, pitcher_advantage = 0, 0
    # Prune the dataset
    data = prune_dataset(data)
    # Iterate over all pitches
    for i in range(len(data)):
        _, _, description, delta_run_exp, _, _ = data.iloc[i]
        # For both ifs, we already pruned the dataset accordingly so we don't have to check if the pitch is inside the strikezone.
        if description == 'called_strike':
            pitcher_advantage += abs(delta_run_exp)
        if description == 'ball':
            batter_advantage += abs(delta_run_exp)
    return pitcher_advantage, batter_advantage

def inside_variable_strikezone(pos_x: float, pos_z: float, sz_top: float, sz_bot: float) -> bool:
    """
    Computes whether a pitch is inside the static strikezone. (independent of the batter's stance)

    Parameters
    ----------
    pos_x : float
        The x position of the pitch at the plate.

    pos_z : float
        The z position of the pitch at the plate.

    sz_top : float
        The top of the strikezone.

    sz_bot : float
        The bottom of the strikezone.

    Returns
    -------
    bool
        Whether the pitch is inside the strikezone.
    """
    return (pos_x >= -0.7083-0.241667/2 and pos_x <= 0.7083+0.241667/2 and pos_z >= sz_bot-0.241667/2 and pos_z <= sz_top+0.241667/2)

if __name__ == '__main__':
    # Be careful with the dates especially when working at midnight ;)
    for team in mlb_teams:
        data = pybaseball.statcast(team=team)
        if not data.empty:
            report_wrong_calls(data, team)
    # So far, this is (maybe still) incoherent with the @UmpScorecards twitter account. Have to double check.