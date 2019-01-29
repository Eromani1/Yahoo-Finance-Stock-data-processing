# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 11:51:39 2019

@author: Romani Edoardo
"""
# Importing required packages
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup


"""
Stock Ticker symbols to look for on Yahoo Finance Historical Data Pages; 
let's say you want to compare Netflix and Disney"""
tickers=["NFLX","DIS"]

"""Initiating empty dictionary where stock data will be collected"""
result_dict={}

"""for every ticker symbol, do the following"""
for ticker in tickers: 
    """
    Launch a web request that scrapes the stock's Yahoo Finance 
    data for that ticket and retrieve html content;
    """
    url="https://finance.yahoo.com/quote/{}/history/".format(ticker)
    request=requests.get(url)
    request_html=request.text
    
    soup=BeautifulSoup(request_html,features="lxml")
    
    """
    First,
    To get table headers, I fetch all html elements of type <th> and 
    store their content in a list, called columns
    """
    table_headers=soup.find_all("th")
    columns=[item.text for item in table_headers]
    del columns[0]
    """
    Then,
    To get table rows data, I fetch all html elements of type <tr> and 
    store their content in a list, tr_list; each element of the list corresponds
    to an table row on the Yahoo page of stock data
    """
    tr=soup.find_all("td")      
    tr_lst=[item.text for item in tr]
    
    """
    After inspecting the table row data, I find that some dates/rows are related to divident distributions,
    which lead to date multiplications and the addition of rows that do not report stock data;
    
    Therefore, I initialize two regular expressions (One for dividend, one for the related date, 
    to run through the data and remove the unnecessary row when a match is encountered.
    """
    
    """Dividend regular expression"""
    
    div_reg=re.compile("Dividend$")
    
    """ Date regular expression accounting for date format on Yahoo Finance"""
    
    date_reg=re.compile("\w{3}\s\d{2},\s\d{4}")
    
    """
    DATA CLEANING 1 Mapping the dividend reg expression on the table rows and 
    creating a new list in which only table rows for which the reg expressions does not match
    """
    tr_lst_clean=[item for item in tr_lst if div_reg.search(item) is None]
    
    
    """
    DATA CLEANING 2 Mapping the date reg expression on the table rows and 
    creating a new list in which only table rows for which the reg expressions does not match
    
    I run results through a loop and filter them according to the regular expression match object;
    I collect filtered results in a list called final_lst
    """
    
    final_lst=[]
    
    for item in tr_lst_clean:
        
        match=date_reg.search(item)
        
        if match is None:
            final_lst.append(item)
        else:
            if match.group() in final_lst:
                continue
            else:
                final_lst.append(item)
                
    """
    I delete the last element of the result list as i do not need it 
    
    (it features a descriptive string description derived from the Yahoo page)
    """
    
    del final_lst[-1]
    
    
    """"
    
    With the filtered data available, i now proceed to create my dataset columns from the result list
    
    Date, Open, High, Low, Close, Adj Close and volume are 
    created using list comprehensions which account for different formats in the input data
    
    The date column is converted to a datetime object from a string format, whereas all other columns are 
    converted to float numbers
    
    """
    
    date=[pd.to_datetime(final_lst[i],format="%b %d, %Y") for i in range(0,len(final_lst),7)]
    
    Open=[float(final_lst[i].replace(",",".").replace(".",""))/100 if len(final_lst[i])>=7 else float(final_lst[i]) for i in range(1,len(final_lst),7)]
    
    High=[float(final_lst[i].replace(",",".").replace(".",""))/100 if len(final_lst[i])>=7 else float(final_lst[i]) for i in range(2,len(final_lst),7)]
    
    Low=[float(final_lst[i].replace(",",".").replace(".",""))/100 if len(final_lst[i])>=7 else float(final_lst[i]) for i in range(3,len(final_lst),7)]
    
    Close=[float(final_lst[i].replace(",",".").replace(".",""))/100 if len(final_lst[i])>=7 else float(final_lst[i]) for i in range(4,len(final_lst),7)]
    
    Adj_Close=[float(final_lst[i].replace(",",".").replace(".",""))/100 if len(final_lst[i])>=7 else float(final_lst[i]) for i in range(5,len(final_lst),7)]
    
    Volume=[int(final_lst[i].replace(",",".").replace(".","")) for i in range(6,len(final_lst),7)]
    
    """ 
    Create final dictionary which puts together processed data
    
    """
    
    df_dict={"Date":date,
            "Open":Open,
             "High":High,
             "Low":Low,
             "Close":Close,
             "Adj Close":Adj_Close,
             "Volume":Volume}
    
    
    """"
    Creating pandas dataframe using the dictionary, setting the datetime 
    results as index and dropping the redundant date column
    
    """
    
    df=pd.DataFrame.from_dict(df_dict)
    df=df.set_index(df["Date"])
    df=df.drop(columns="Date")
    
    """"
    Calculating Daily Return column as: 
        
    (Close Price of Day X - Close Price of Day X -1)/ Close Price of Day X
    
    """
    
    df["Daily Return"]=(df["Close"].shift(1)-df["Close"])/df["Close"]
    
    """
    Append the daily return into final dict object and exiting the loop; after this ends,
    we now have dataset with all daily return stock data for seached ticker symbols
    """
    result_dict[ticker]=df["Daily Return"]

"""

Convert final dictionary result to data frame

"""

result_df=pd.DataFrame.from_dict(result_dict)

"""
Creating Daily Return graph and displaying it

"""

graph=result_df.plot(title="Daily Stock Return: {} vs {}".format(tickers[0],tickers[1]),colormap="jet")

graph.set_ylabel("Daily Return")






