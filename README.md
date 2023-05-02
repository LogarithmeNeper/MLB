# MLB

## Statcast
Using the [pybaseball](https://github.com/jldbc/pybaseball) package, we can pull Statcast data from Baseball Savant. The data is stored in a Pandas DataFrame, which can be manipulated and analyzed using the Pandas library. Thus far, I have used the data to create a few visualizations of the data, namely: 
- Pitcher report card on release (colour on pitch type) and homeplate (colour on result of the play).
- Team report on hits (colour on result of the play)
- Pitcher analysis for each pitch type on various metrics (e.g. release speed, effective speed, spin rate, extension, etc.)

## UmpScorecard
Using the [pybaseball](https://github.com/jldbc/pybaseball) package, we can also work on getting a report of the umpire's performance for the game. The data is stored in a Pandas DataFrame, which can be manipulated and analyzed using the Pandas library. Thus far, I have used the data to create a few visualizations of the data, namely:
- Plotting the wrong calls (balls inside the strike zone and strikes outside the strike zone) on a scatter plot of the strike zone.
- Computing the run value of wrong calls for both pitchers and batters, and for each team, from which we can derive the total run value of wrong calls for the game.

So far, the results are interesting but are far from the values computed by [@UmpScorecards](https://twitter.com/UmpScorecards) on Twitter. I am still working on figuring out why the values are so different.

## Next steps
Some features I would like to add:
- Add a feature by searching by pitcher or by team instead of by date (yesterday being the main use case, however)
- ...
- 