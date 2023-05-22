import os
import pybaseball
import pandas as pd
import matplotlib.pyplot as plt

def get_player_id(name: str) -> int:
    player_id = pybaseball.playerid_lookup(name.split()[1], name.split()[0])
    return player_id['key_mlbam'][0]

def get_pitcher_data(player_id: int, year: str) -> pd.DataFrame:
    """
    Get the data of a pitcher.

    Parameters
    ----------
    player_id : int
        The player id of the pitcher.
    year : str
        The year of the data.

    Returns
    -------
    pd.DataFrame
        The data of the pitcher.
    """
    return pybaseball.statcast_pitcher(f'{year}-01-01', f'{year}-12-31', player_id)

def create_report_pitcher(data: pd.DataFrame, pitcher_name: str, year: str) -> None:
    """
    Create a report of the release speed, effective speed and release spin rate of a pitcher during a year.

    Parameters
    ----------
    data : pd.DataFrame
        The data of the pitcher.
    pitcher_name : str
        The name of the pitcher.
    year : str
        The year of the data.

    Returns
    -------
    None
    """
    data = data[data['pitch_type'].notna()]
    outfolder = f"report_{pitcher_name}_{year}"
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)
    cols = ['release_speed', 'effective_speed', 'release_spin_rate']
    for col in cols:
        pitch_types = data['pitch_type'].unique()
        for pitch_type in pitch_types:
            pitch_data = data[data['pitch_type'] == pitch_type]
            dates = pitch_data['game_date'].unique()
            fig = plt.figure(figsize=(12, 8))
            for i in range(len(dates)):
                date = dates[i]
                gameday_data = pitch_data[pitch_data['game_date'] == date]
                plt.boxplot(gameday_data[col], positions=[i], widths=0.5, labels=[date])
            # Set the title of the figure
            plt.title(f"{pitcher_name}'s {pitch_type} {col} during {year}")
            plt.xlabel("Date")
            plt.ylabel(col)
            plt.savefig(f"{outfolder}/{pitch_type}_{col}.png")
            plt.close(fig)

def create_report(pitcher_name: str, year: str):
    """
    Aggregate the functions to create a report of the release speed, effective speed and release spin rate of a pitcher during a year.

    Parameters
    ----------
    pitcher_name : str
        The name of the pitcher.
    year : str
        The year of the data.
    """
    pitcher_id = get_player_id(pitcher_name)
    data = get_pitcher_data(pitcher_id, year)
    create_report_pitcher(data, pitcher_name, year)

if __name__ == "__main__":
    create_report("Chris Sale", "2023")