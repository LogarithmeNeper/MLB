# MLB

## Statcast

Using the [pybaseball](https://github.com/jldbc/pybaseball) package, we can pull Statcast data from Baseball Savant. The data is stored in a Pandas DataFrame, which can be manipulated and analyzed using the Pandas library. Thus far, I have used the data to create a few visualizations of the data, namely: 
- Pitcher report card on release (colour on pitch type) and homeplate (colour on result of the play).
- Team report on hits (colour on result of the play)
- Pitcher analysis for each pitch type on various metrics (e.g. release speed, effective speed, spin rate, extension, etc.)

## Pitcher Report

Using the [pybaseball](https://github.com/jldbc/pybaseball), I created a way to analyse release speed, effective speed and spin rate at release for a pitcher through time. I also added a kernel estimator for the position of pitches during a year, using the [seaborn](https://seaborn.pydata.org/) library.

Some features I would like to add:
- Dupe of UmpScorecard, with Statcast data, with effective plate coverage of the umpire (vertical depending ont the batter stance)
- Add a feature by searching by pitcher or by team instead of by date (yesterday being the main use case, however)
- ...