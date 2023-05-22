import os
import pybaseball
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

def create_boxplot_report_pitcher(data: pd.DataFrame, pitcher_name: str, year: str) -> None:
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
                home_team = gameday_data['home_team'].unique()[0]
                away_team = gameday_data['away_team'].unique()[0]
                plt.boxplot(gameday_data[col], positions=[len(dates) - i], widths=0.5, labels=[date + '\n' + away_team + ' @ ' + home_team])
            # Set the title of the figure
            plt.title(f"{pitcher_name}'s {pitch_type} {col} during {year}")
            plt.xlabel("Date")
            plt.ylabel(col)
            plt.savefig(f"{outfolder}/{pitch_type}_{col}.png")
            plt.close(fig)

def create_boxplot_report(pitcher_name: str, year: str):
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
    create_boxplot_report_pitcher(data, pitcher_name, year)

def create_kernel_report_pitcher(data: pd.DataFrame, pitcher_name: str, year: str) -> None:
    data = data[data['pitch_type'].notna()]
    pitch_types = data['pitch_type'].unique()
    outfolder = f"report_{pitcher_name}_{year}"
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)
    
    for pitch_type in pitch_types:
        pitch_data = data[data['pitch_type'] == pitch_type]
        title_plot  = f"{pitcher_name}'s {pitch_type} pitch location during {year}"
        plt.rcParams["figure.figsize"] = (9.6, 7.2)
        plt.title(title_plot)

        # Taken from statcast.py
        plt.xlim(-1.5, 1.5)
        plt.ylim(1, 4)
        # Plot the strike zone
        plt.gca().add_patch(plt.Rectangle((-0.7083, 1.5), 0.7083*2, 3.5-1.5, fill=False))
        plt.gca().add_patch(plt.Rectangle((-0.7083, 1.5), 0.7083*2, 3.5-1.5, fill=True, alpha=0.1))
        # Separate the strike zone into 9 squares 
        plt.vlines(x=-0.2361, color='grey', ymin=1.5, ymax=3.5)
        plt.vlines(x=0.2361, color='grey', ymin=1.5, ymax=3.5)
        plt.hlines(y=2.1666, color='grey', xmin=-0.7083, xmax=0.7083)
        plt.hlines(y=2.8334, color='grey', xmin=-0.7083, xmax=0.7083)

        # Plot a kernel estimate of the pitch location plate_x and plate_z using seaborn
        sns.kdeplot(pitch_data['plate_x'], pitch_data['plate_z'], cmap='Reds', shade=True, thresh=0.05, n_levels=25)

        # Save the plot
        plt.savefig(f"{outfolder}/{pitch_type}_heatmap.png")
        plt.close()

def create_kernel_report(pitcher_name: str, year: str):
    pitcher_id = get_player_id(pitcher_name)
    data = get_pitcher_data(pitcher_id, year)
    create_kernel_report_pitcher(data, pitcher_name, year)

if __name__ == "__main__":
    # create_boxplot_report("Corey Kluber", "2023")
    create_kernel_report("Chris Sale", "2018")
    create_kernel_report("Chris Sale", "2023")