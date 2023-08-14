from bs4 import BeautifulSoup
import pandas as pd
import requests
import matplotlib.pyplot as plt
import sklearn.linear_model
import seaborn as sns
import numpy as np

def get_page(url: str) -> BeautifulSoup:
    """
    Get the page of a url.

    Parameters
    ----------
    url : str
        The url of the page.

    Returns
    -------
    BeautifulSoup
        The page of the url.
    """
    page = requests.get(url)
    return BeautifulSoup(page.content, 'html.parser')

def get_data_from_html(page: BeautifulSoup) -> pd.DataFrame:
    """
    Get the table as a Pandas Dataframe from the html page.

    Parameters
    ----------
    page : BeautifulSoup
        The page of the url.

    Returns
    -------
    pd.DataFrame
        The table as a Pandas Dataframe.
    """
    table = page.find('table', class_='rgMasterTable')
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')

    # Get name of columns
    header = table.find('thead')
    header_row = header.find_all('tr')
    header_cols = header_row[1].find_all('th')
    header_cols = [element.text.strip() for element in header_cols]

    # Get data
    data = []
    for row in rows:
        cols = row.find_all('td')
        cols = [element.text.strip() for element in cols]
        data.append(cols)
    
    # Create dataframe
    df = pd.DataFrame(data, columns=header_cols)
    # Remove '#' column
    df = df.drop('#', axis=1)
    # Remove empty rows
    df = df[df['Name'] != '']
    return df

def get_stats(season: str, stats: str, month: str = '0', league: str='all', min_ip: str='y', team: str='0', max_players: str = '500') -> pd.DataFrame:
    """	
    Get the stats of a season.

    Parameters
    ----------
    season : str
        The season as a string.
    stats : str
        The stats to get. Must be one of 'pit', 'bat' or 'fld', which account for pitching, batting and fielding, respectively.
    month : str, optional
        The month of the season. The default is '0', which means the whole season.
    league : str, optional
        The league. The default is 'all'.
    min_ip : str, optional
        The minimum innings pitched. The default is 'y', which means qualified.
    team : str, optional
        The team. The default is '0', which means all teams. Otherwise, it must be '1' to '30'.
    max_players : str, optional
        The maximum number of players. The default is '500', which should suffice generally.

    Returns
    -------
    pd.DataFrame
        The stats of the season.
    """
    
    if stats in ['pit', 'bat', 'fld']:
        url = f"https://www.fangraphs.com/leaders.aspx?pos=all&stats={stats}&lg={league}&qual={min_ip}&type=8&season={season}&month={month}&season1={season}&ind=0&team={team}&page=1_{max_players}"
    else:
        raise ValueError('stats must be one of pit, bat or fld')
    
    page = get_page(url)
    table = get_data_from_html(page)
    # Convert everything we can to numeric
    table = table.apply(pd.to_numeric, errors='ignore')
    return table

def correlation_columns(df: pd.DataFrame, col1: str, col2: str, idx: str = None) -> None:
    """
    Create a scatterplot of two columns in a dataframe, and add linear regression.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe.
    col1 : str
        The first column.
    col2 : str
        The second column.
    idx : str, optional
        The index of the dataframe. The default is None.

    Returns
    -------
    None
    """
    # Linear regression
    x = df[col1].values.reshape(-1, 1)
    y = df[col2].values.reshape(-1, 1)
    reg = sklearn.linear_model.LinearRegression()
    reg.fit(x, y)
    y_pred = reg.predict(x)
    # Plot the scatterplot
    plt.scatter(df[col1], df[col2])
    if idx is not None:
        for i, txt in enumerate(df[idx]):
            plt.annotate(txt, (df[col1][i], df[col2][i]))
    plt.xlabel(col1)
    plt.ylabel(col2)
    plt.plot(x, y_pred, color='red')
    plt.title(f'{col1} vs {col2}, R^2 = {reg.score(x, y)}')
    plt.show()

def correlation_matrix(df: pd.DataFrame) -> None:
    """
    Create a correlation matrix of a dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe.

    Returns
    -------
    None
    """
    # Remove all non-numeric columns
    df = df.select_dtypes(include=['float64', 'int64'])
    corr = df.corr()
    # Keep only the upper triangle
    mask = np.triu(np.ones_like(corr, dtype=bool))
    corr = corr.mask(mask)
    # Plot the heatmap
    sns.heatmap(corr, xticklabels=corr.columns, yticklabels=corr.columns, annot=True, cmap=sns.diverging_palette(220, 20, as_cmap=True), vmin=-1, vmax=1, center=0, square=True, linewidths=.5, cbar_kws={"shrink": .5})
    plt.show()

def report_histogram(df: pd.DataFrame, cols: list) -> None:
    """
    Create a histogram for each column given for a dataframe, and show them all in one.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe.
    cols : list
        The list of columns.

    Returns
    -------
    None
    """
    fig, axes = plt.subplots(ncols=1, nrows=len(cols), figsize=(5, 30))
    for i, col in enumerate(cols):
        sns.histplot(data=df, x=col, ax=axes[i], kde=True)
        mean = df[col].mean()
        axes[i].axvline(mean, color='r', linestyle='--')
        axes[i].text(0.05, 0.9, f'Mean: {round(mean, 2)}', transform=axes[i].transAxes)
    plt.show()

def report_boxplot(df: pd.DataFrame, cols: list) -> None:
    """
    Create a boxplot for each column given for a dataframe, and show them all in one, with the same x-axis.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe.
    cols : list
        The list of columns.

    Returns
    -------
    None
    """
    fig, axes = plt.subplots(ncols=1, nrows=len(cols), figsize=(5, 30))
    for i, col in enumerate(cols):
        sns.boxplot(x=df[col], ax=axes[i])
        mean = df[col].mean()
        axes[i].axvline(mean, color='r', linestyle='--')
        # Add the numerical value of the quartiles, median and mean, rounded to 2 decimals
        axes[i].text(0.05, 0.9, f'Q1: {round(df[col].quantile(0.25), 2)}', transform=axes[i].transAxes)
        axes[i].text(0.05, 0.8, f'Median: {round(df[col].median(), 2)}', transform=axes[i].transAxes)
        axes[i].text(0.05, 0.7, f'Q3: {round(df[col].quantile(0.75), 2)}', transform=axes[i].transAxes)
        axes[i].text(0.05, 0.6, f'Mean: {round(mean, 2)}', transform=axes[i].transAxes)
        #axes[i].set_title(col)
    plt.show()

if __name__=='__main__':
    df = get_stats('2023', 'pit', min_ip='y')
    correlation_columns(df, 'IP', 'ERA', 'Name')
    report_histogram(df, ['ERA', 'FIP'])
    report_boxplot(df, ['ERA', 'FIP'])