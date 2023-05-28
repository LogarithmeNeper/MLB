import pybaseball
import statsapi
import pandas as pd
import matplotlib.pyplot as plt
import os
import time

# Create list of MLB teams
mlb_teams = ['AZ', 'ATL', 'BAL', 'BOS', 'CHC', 'CWS', 'CIN', 'CLE', 'COL', 'DET', 'HOU', 'KC', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK', 'PHI', 'PIT', 'SD', 'SEA', 'SF', 'STL', 'TB', 'TEX', 'TOR', 'WSH']

# Create dictionary pitch type to colour
pitch_type_colour = {
    'FF': 'red',
    'FT': 'blue', 
    'FC': 'green', 
    'FS': 'yellow', 
    'FO': 'orange', 
    'SI': 'purple', 
    'SL': 'pink', 
    'CU': 'black', 
    'KC': 'brown', 
    'EP': 'grey', 
    'CH': 'cyan', 
    'SC': 'magenta', 
    'KN': 'lightgrey',
    'UN': 'lightblue',
    'PO': 'lightgreen',
    'IN': 'lightyellow',
    'PO': 'lightpink',
}

called_pitch_colour = {
    'foul': 'pink',
    'hit_into_play': 'blue',
    'ball': 'green',
    'called_strike': 'red',
    'swinging_strike_blocked': 'orange',
    'swinging_strike': 'yellow',
}

in_play_colour = {
    'single': 'blue',
    'double': 'green',
    'triple': 'pink',
    'home_run': 'red',
    'field_out': 'lightgrey',
    'grounded_into_double_play': 'brown',
}

def create_report(
        data: pd.DataFrame,
        plotting_columns: list,
        legend: str,
        mapping_dictionary: dict,
        title_plot: str,
        outfolder: str,
        outfile: str,
        strike_zone: bool = False) -> None:
    """
    Create a report of the data given a dataframe, the columns to plot, the legend and the mapping dictionary.

    Parameters
    ----------
    data : pd.DataFrame
        The dataframe containing the data to plot

    plotting_columns : list
        The columns to plot

    legend : str
        The column to use as legend

    mapping_dictionary : dict
        The mapping dictionary to use to map the legend to a colour

    title_plot : str
        The title of the plot

    outfolder : str
        The name of the output folder
    
    outfile : str
        The name of the output file

    strike_zone : bool
        Whether to plot the strike zone or not

    Returns
    -------
    None
    """
    data['colour'] = data[legend].map(mapping_dictionary)
    # Drop rows when the value in the colour column is NaN
    data = data.dropna(subset=['colour'])
    data.plot.scatter(x=plotting_columns[0], y=plotting_columns[1], c=data['colour'], figsize=(9.6, 7.2), edgecolors='black', linewidths=0.5)
    handles = [plt.Line2D([0], [0], marker='o', color='w', label=k, markerfacecolor=v, markersize=10) for k,v in mapping_dictionary.items()]
    
    if strike_zone:
        plt.xlim(-3, 3)
        plt.ylim(0, 5)
        # Plot the strike zone
        plt.gca().add_patch(plt.Rectangle((-0.7083, 1.5), 0.7083*2, 3.5-1.5, fill=False))
        plt.gca().add_patch(plt.Rectangle((-0.7083, 1.5), 0.7083*2, 3.5-1.5, fill=True, alpha=0.1))
        # Add an extended strikezone (1 ball width up and down, 1 ball width to the left and right)
        plt.gca().add_patch(plt.Rectangle((-0.7083-0.241667/2, 1.5-0.241667/2), (0.7083+0.241667/2)*2, 3.5-1.5+0.241667/2*2, fill=False, linestyle='--', color='grey'))

        handles.append(plt.Line2D([0], [0], linestyle='--', color='grey', label='Extended strike zone'))
        handles.append(plt.Line2D([0], [0], linestyle='-', color='grey', label='Strike zone'))

        # Separate the strike zone into 9 squares 
        plt.vlines(x=-0.2361, color='grey', ymin=1.5, ymax=3.5)
        plt.vlines(x=0.2361, color='grey', ymin=1.5, ymax=3.5)
        plt.hlines(y=2.1666, color='grey', xmin=-0.7083, xmax=0.7083)
        plt.hlines(y=2.8334, color='grey', xmin=-0.7083, xmax=0.7083)
        
    plt.legend(handles=handles)
    plt.title(title_plot)

    if not os.path.exists(outfolder):
        os.makedirs(outfolder)
    plt.savefig(os.path.join(outfolder, outfile))
    plt.close()

def get_statcast(team: str, start_date:str = None, end_date: str = None) -> pd.DataFrame:
    """Get the last game statcast data for a team""
    
    Parameters
    ----------
    team : str
        The team's abbreviation (e.g. 'BOS' for Boston Red Sox)
    
    start_date : str
        The start date of the period to get the data from (format: 'YYYY-MM-DD') (default: None)

    end_date : str
        The end date of the period to get the data from (format: 'YYYY-MM-DD') (default: None)
    
    Returns
    -------
    pd.DataFrame
        The last game statcast data for the team
    """
    return pybaseball.statcast(team=team, start_dt=start_date, end_dt=end_date)

def get_statcast_gamePk(gamePk: int) -> pd.DataFrame:
    """Get the statcast data for a gamePk
    
    Parameters
    ----------
    gamePk : int
        The gamePk of the game
    
    Returns
    -------
    pd.DataFrame
        The statcast data for the game
    """
    return pybaseball.statcast_single_game(gamePk)

def get_lastgame_pitchers(data: pd.DataFrame) -> list:
    """Get the pitchers who pitched in the last game

    Parameters
    ----------
    data : pd.DataFrame
        The last game statcast data for the team
    
    Returns
    -------
    list
        The list of pitchers who pitched in the last game
    """
    return data['player_name'].unique().tolist()

def generate_release_by_pitcher(data: pd.DataFrame, pitcher: str) -> None:
    """Generate a scatter plot of the release position for a pitcher and colour by pitch type
    
    Parameters
    ----------
    data : pd.DataFrame
        The last game statcast data for the team

    pitcher : str
        The pitcher's name

    Returns
    -------
    None
    """
    gamedate = str(data['game_date'].unique()[0])[:10]
    home_team = data['home_team'].unique()[0]
    away_team = data['away_team'].unique()[0]
    pitcher_data = data[data['player_name'] == pitcher]
    pitcher_data = pitcher_data[['pitch_type', 'release_pos_x', 'release_pos_z']]
    # Generate report
    create_report(
        pitcher_data,
        ['release_pos_x', 'release_pos_z'],
        'pitch_type',
        pitch_type_colour,
        f"{pitcher} on {gamedate} [{away_team}@{home_team}] (release point)",
        f"release_{gamedate}",
        f"{pitcher}_release_{gamedate}.png"
    )
    
def generate_all_release(data: pd.DataFrame) -> None:
    """
    Generate a scatter plot of the release position for all pitchers and colour by pitch type

    Parameters
    ----------
    data : pd.DataFrame
        The last game statcast data for the team

    Returns
    -------
    None
    """
    pitchers = get_lastgame_pitchers(data)
    for pitcher in pitchers:
        generate_release_by_pitcher(data, pitcher)

def generate_homeplate_by_pitcher(data: pd.DataFrame, pitcher:str) -> None:
    """
    Generate a scatter plot of the home plate position for a pitcher and colour by called pitch type

    Parameters
    ----------
    data : pd.DataFrame
        The last game statcast data for the team

    pitcher : str
        The pitcher's name

    Returns
    -------
    None
    """
    gamedate = str(data['game_date'].unique()[0])[:10]
    home_team = data['home_team'].unique()[0]
    away_team = data['away_team'].unique()[0]
    pitcher_data = data[data['player_name'] == pitcher]
    pitcher_data = pitcher_data[['description', 'plate_x', 'plate_z']]
    # Create report
    create_report(
        pitcher_data,
        ['plate_x', 'plate_z'],
        'description',
        called_pitch_colour,
        f"{pitcher} on {gamedate} [{away_team}@{home_team}] (homeplate)",
        f"homeplate_{gamedate}",
        f"{pitcher}_homeplate_{gamedate}.png",
        True
    )

def generate_all_homeplate(data: pd.DataFrame) -> None:
    """
    Generate a scatter plot of the home plate position for all pitchers and colour by called pitch type

    Parameters
    ----------
    data : pd.DataFrame
        The last game statcast data for the team
    
    Returns
    -------
    None
    """
    pitchers = get_lastgame_pitchers(data)
    for pitcher in pitchers:
        generate_homeplate_by_pitcher(data, pitcher)

def generate_boxplot_report_by_pitcher(data: pd.DataFrame, pitcher: str) -> None:
    """ 
    Generate a boxplot report for a pitcher
    
    Parameters
    ----------
    data : pd.DataFrame
        The last game statcast data for the team
        
    pitcher : str
        The pitcher's name

    Returns
    -------
    None
    """
    gamedate = str(data['game_date'].unique()[0])[:10]
    home_team = data['home_team'].unique()[0]
    away_team = data['away_team'].unique()[0]
    outfolder = f"boxplot_{gamedate}"
    # Create folder if it doesn't exist
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)
    pitcher_data = data[data['player_name'] == pitcher]
    pitcher_data = pitcher_data[['pitch_type', 'release_speed', 'effective_speed', 'release_pos_x', 'release_pos_z', 'release_spin_rate', 'release_extension']]
    # Drop nan values
    pitcher_data = pitcher_data.dropna()
    # Get the pitch types
    pitch_types = pitcher_data['pitch_type'].unique().tolist()
    for pitch in pitch_types:
        pitch_data = pitcher_data[pitcher_data['pitch_type'] == pitch]
        # Create a matplotlib figure
        fig = plt.figure(figsize=(10, 10))
        # Create a boxplot for both release and effective speed on a single row in the figure
        pitch_data.boxplot(column=['release_speed', 'effective_speed'], ax=fig.add_subplot(3, 1, 1), grid=False)
        for i, col in enumerate(pitch_data.columns[3:]):
            # Create a boxplot for the column
            ax = fig.add_subplot(3, 2, i+3)
            ax.boxplot(pitch_data[col], vert=False)
            ax.set_yticks([])
            # Add title to the y axis vertically
            ax.set_ylabel(col, rotation=90, labelpad=20)
        # Save the figure
        fig.suptitle(f"{pitch} for {pitcher} on {gamedate} [{away_team}@{home_team}]")
        filename = f"{pitcher}_{pitch}_{gamedate}.png"
        fig.savefig(os.path.join(outfolder, filename))
        plt.close(fig)

def generate_all_boxplot_report(data: pd.DataFrame) -> None:
    """
    Generate a boxplot report for all pitchers

    Parameters
    ----------
    data : pd.DataFrame
        The last game statcast data for the team

    Returns
    -------
    None
    """
    pitchers = get_lastgame_pitchers(data)
    for pitcher in pitchers:
        generate_boxplot_report_by_pitcher(data, pitcher)

def in_play_report(data: pd.DataFrame, team: str) -> None:
    """
    Generate a report of the in play results given a game statcast data.

    Parameters
    ----------
    data : pd.DataFrame
        The last game statcast data for the team
    
    Returns
    -------
    None
    """
    gamedate = str(data['game_date'].unique()[0])[:10]
    home_team = data['home_team'].unique()[0]
    away_team = data['away_team'].unique()[0]
    in_play_data = data[data['description'] == 'hit_into_play']
    in_play_data = in_play_data[['events', 'description', 'plate_x', 'plate_z']]
    # Keep only the events in the keys of the in_play_colour dictionary
    in_play_data = in_play_data[in_play_data['events'].isin(in_play_colour.keys())]
    create_report(
        in_play_data,
        ['plate_x', 'plate_z'],
        'events', in_play_colour,
        f"{away_team}@{home_team} on {gamedate} (in-play) [hits against {team}'s pitchers]",
        f"in_play_{gamedate}",
        f"in_play_{team}_{gamedate}.png",
        strike_zone=True
    )

if __name__ == '__main__':
    for team in mlb_teams:
        data = get_statcast(team)
        if data.empty:
            print(f"Team {team} has no data")
            continue
        generate_all_release(data)
        generate_all_homeplate(data)
        in_play_report(data, team)
        generate_all_boxplot_report(data)