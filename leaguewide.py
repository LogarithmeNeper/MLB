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
    if stats in ['pit', 'bat', 'fld']:
        url = f"https://www.fangraphs.com/leaders.aspx?pos=all&stats={stats}&lg={league}&qual={min_ip}&type=8&season={season}&month={month}&season1=2023&ind=0&team={team}&page=1_{max_players}"
    else:
        raise ValueError('stats must be one of pit, bat or fld')
    
    page = get_page(url)
    table = get_data_from_html(page)
    # Convert everything we can to numeric
    table = table.apply(pd.to_numeric, errors='ignore')
    return table

def correlation_columns(df: pd.DataFrame, col1: str, col2: str) -> None:
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

if __name__=='__main__':
    df = get_stats('2023', 'pit')
    # correlation_columns(df, 'ERA', 'FIP')
    correlation_matrix(df)
