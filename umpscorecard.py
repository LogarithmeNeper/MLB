import pybaseball

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
    advantage = 0
    # Keep only the columns we need
    data = data[['plate_x', 'plate_z', 'description', 'delta_run_exp']]
    # Iterate over all pitches
    for i in range(len(data)):
        pos_x, pos_z, description, delta_run_exp = data.iloc[i]
        # Probably not that simple. 
        # TODO: Need to figure out how the 'delta_run_exp' works (who is favoured by a positive value?)
        # Situation 1: called strike outside the strikezone, favouring the pitcher
        if description == 'called_strike' and not inside_static_strikezone(pos_x, pos_z):
            advantage -= delta_run_exp # Unsure about the sign.
        # Situation 2: called strike inside the strikezone, favouring the batter
        if description == 'ball' and inside_static_strikezone(pos_x, pos_z):
            advantage += delta_run_exp # Unsure about the sign, but should be the opposite of the previous one.
    return advantage

def inside_static_strikezone(pos_x: float, pos_z: float) -> bool:
    """
    Computes whether a pitch is inside the static strikezone. (independent of the batter's stance)

    Parameters
    ----------
    pos_x : float
        The x position of the pitch.

    pos_z : float
        The z position of the pitch.

    Returns
    -------
    bool
        Whether the pitch is inside the static strikezone.
    """
    return (pos_x >= -0.7083 and pos_x <= 0.7083 and pos_z >= 1.6 and pos_z <= 3.5)

if __name__ == '__main__':
    # Get umpire scorecard
    data = pybaseball.statcast(team='BOS')
    print(compute_static_scorecard_team(data))

    data2 = pybaseball.statcast(team='CLE')
    print(compute_static_scorecard_team(data2))

    # So far, this is incoherent with the @UmpScorecards twitter account.
    # Check GitHub repo for more info: www.github.com/panzarino/umpire-scorecards