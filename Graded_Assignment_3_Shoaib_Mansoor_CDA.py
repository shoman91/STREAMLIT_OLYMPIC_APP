import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
st.set_page_config(layout="wide")


st.title('Olympic History Dashboard')
st.header('Shoaib Mansoor')

#reading the CSV File
df_athletes = pd.read_csv('athlete_events.csv')
df_regions=pd.read_csv('noc_regions.csv') 
#after initially cleaning the data using "athlete_events.csv" ONLY, I realized that the REGIONS column have a critical role, since the countries
#are reffered and listed correctly in 'region' column ONLY in "noc_regions.csv"

#completing the dataframe
df1=pd.merge(df_athletes,df_regions, on="NOC",how = "left")

#----------------------------------BEGIN DATA CLEANING--------------------------------------------------------------------------------------------
#1385 rows as duplicates
df1=df1.drop_duplicates()

#null values in 'age','Height','Weight' and 'Medal' Columns.
#using average age with respect to EACH SPORT to fill missing age values, got the transfrom('mean') function by GOOGLING
df1['Age'] = df1['Age'].fillna(df1.groupby("Sport")["Age"].transform("mean"))

#using average Height with respect to EACH SPORT to fill missing Height values
df1['Height']=df1['Height'].fillna(df1.groupby("Sport")["Height"].transform("mean"))

#using average Weight with respect to EACH SPORT to fill missing Weight values
df1['Weight']=df1['Weight'].fillna(df1.groupby("Sport")["Weight"].transform("mean"))

#still missing values in 'Height' and 'Weight' Column, HENCE, NOW filling in the missing values using average height and weight respect to GENDER
df1['Height']=df1['Height'].fillna(df1.groupby("Sex")["Height"].transform("mean"))

df1['Weight']=df1['Weight'].fillna(df1.groupby("Sex")["Weight"].transform("mean"))

#filling the empty values for 'Medal' Column
df1['Medal']=df1['Medal'].fillna('NA')

#dropping notes column, merged from 'noc_regions'
df1=df1.drop(columns=['notes'])

#Creating GOLD, SILVER, and BRONZE columns from MEDAL column
df1['Gold']= df1['Medal'].apply(lambda x: 1 if x=='Gold' else None)
df1['Silver']= df1['Medal'].apply(lambda x: 1 if x=='Silver' else None)
df1['Bronze']= df1['Medal'].apply(lambda x: 1 if x=='Bronze' else None)

#----------------------------------------END DATA CLEANING------------------------------------------------------------------------------------------

#---------------------------------------BEGIN EDA---------------------------------------------------------------------------------------------------

#Q1. TOP 10 years with MOST GOLDS in the Olympic History
x = df1.groupby('Year')['Gold'].count().sort_values(ascending=False).head(10)
#Most GOLDs in 1.2008 2.2016 3. 2004. LED ME TO A STRANGE FACT: THE ONLY TIME OLYMPICS HAPPENED IN A NON LEAP YEAR WAS THE YEAR 1900 and 2021.

#Q2. Most distributed category of medals, over the years in Olympic History
x1=df1.groupby('Medal')['Name'].count()
# 1. GOLD=13369 2. BRONZE= 13295 3. SILVER=13108

#Q3. Most Medals won by an athlete in the Olympic History
medals = df1[df1['Medal']!='NA']
x2=medals.groupby('Name')['Medal'].count().sort_values(ascending=False).head(1)
# Michael Fred Phelps, II = 28

#Q4. Most Medals were distrubted in which sport?
x3=medals.groupby('Sport')['Medal'].count().sort_values(ascending=False).head(1)
# ATHLETICS

#Q5. Age of Athletes with most amount of medals?
x4=medals.groupby('Age')['Medal'].count().sort_values(ascending=False).head(1)
# 23 years if age with 3396 Medals

#------------------------------------------END EDA-----------------------------------------------------------------------------------------------

#--------------------------------------------BEGIN STREAMLIT-------------------------------------------------------------------------------------



# using Country to filter data
#Creating the first container
#A=st.container()

#1st CONTAINER
with st.container():
    # ONE COLUMN INSIDE THE CONTAINER
    col1=st.columns(1) 
    all_countries = df1['region'].unique()
    #SELECT BOX WITH RESPECT TO COUNTRIES - I TRIED SORTING IT WITH ALPHABETICAL ORDER but COULDNT
    selection = st.selectbox('Select Country', all_countries)

    #SUBSET FOR COUNTRY SELECTION
    subset = df1[df1['region'] == selection] 

    #SUBSET WHICH INLCUDES GOLD, SILVER AND BRONZE MEDALS
    medals = df1[df1['Medal']!='NA']

    #SUBSET FOR COUNTRY SELECTION & MEDALS(Gold, Silver, Bronze)
    y_medals = subset[subset['Medal']!='NA']

#2nd CONTAINER
with st.container():
    #Defining 4 columns inside container no. 2
    col1,col2,col3,col4 = st.columns(4)

    #No of Participants with respect to COUNTRY
    with col1:
        col1.metric('No of Participants', subset['ID'].nunique())
    #GOLD MEDALS
    with col2:
        col2.metric('No of Gold Medals', subset['Gold'].count())
    #SILVER MEDALS
    with col3:
        col3.metric('No of Silver Medals', subset['Silver'].count())
    #BRONZE MEDALS
    with col4:
        col4.metric('No of Bronze Medals', subset['Bronze'].count())

#3rd CONTAINER
with st.container():
    #Defining 3 columns inside container no '3'
    col5,col6,col7 = st.columns(3)
#B=st.container()
    with col5: #FOR LINE CHART (multiple lines on same chart)- WITH RESPECT TO GOLD SILVER & BRONZE
        Gold_plot=subset.groupby('Year')['Gold'].count()
        Silver_plot=subset.groupby('Year')['Silver'].count()
        Bronze_plot=subset.groupby('Year')['Bronze'].count()

        #SOMETHING FOUND BY GOOGLING --> DEIFING X & Y, with respect to INDEX AND VALUES
        For_line_plot = pd.DataFrame({
        'Year': Gold_plot.index,
        'Gold': Gold_plot.values,
        'Silver': Silver_plot.values,
        'Bronze': Bronze_plot.values})

        st.set_option('deprecation.showPyplotGlobalUse', False) #IGNORABLE --> JUST TO AVOID A WARNING WITH RESPECT TO SEABORN, SUGGESTED BY SEABORN
                                                                
        #LINE PLOT IN SNS, THE MELT PART IS TO MAKE THE LINES MORE SMOOTHER RATHER THAN BROKEN
        figA=sns.lineplot(x='Year', y='value', hue='variable', data=pd.melt(For_line_plot,['Year'])) 
        figA.set(xlabel='Year', ylabel='No of Medals') #LABELLING THE AXIS
        col5.pyplot()

    with col6: #HORIZONTAL BARCHART
        #GROUPING BY NAME & COUNTING THE AWARDED MEDALS
        x_medals = y_medals.groupby('Name')['Medal'].count().sort_values(ascending=False).head(5)
        #Plotting the horizontal barchart
        plt.barh(x_medals.index,x_medals.values, color=['black', 'red', 'green', 'blue', 'cyan'])
        plt.xlabel("No of Medals")
        col6.pyplot()

    with col7: # TABLE
        #GROUPING BY SPORT & COUNTING THE MEDALS RELEVANT TO SPORT
        subset_sport = y_medals.groupby('Sport')['Medal'].count().sort_values(ascending=False).head(5)
        col7.table(subset_sport)

with st.container():#FORTH CONTAINER
    col8,col9,col10 = st.columns(3) #COLUMNS CAN BE NUMBER 1,2 3 as well, but for my own ease

    with col8: #HISTOGRAM
        figB=sns.histplot(x='Age', data=subset, bins=10)
        figB.set(ylabel='No of Medals')
        col8.pyplot()

    with col9:#PIECHART 
        gender= y_medals.groupby(['Sex','Medal'])['Medal'].count()
   
        fig = plt.pie(gender, labels=gender.index, autopct='%.2f')
        col9.pyplot()

    with col10: #No of Medals according to Season - BAR CHART
        seasons_medals = y_medals.groupby('Season')['Medal'].count()
        plt.bar(seasons_medals.index,seasons_medals.values, color=['blue', 'orange'])
        plt.ylabel("No of Medals")
        col10.pyplot()

#WAS JUST TRYING SOMETHING - KEEPING IT FOR LATER    
#with st.container():
    #all_ = df1['region'].unique()
    #selection = st.selectbox('Select Country', all_countries)

    #get unique sources from the selected country
    #seasons__ = sorted(subset['Season'].unique())

    #display multi select option on source
    #selected_season = st.selectbox('Select Summer/Winter Olympics', seasons__)

    #plt.style.use('ggplot')
    #seasons_medals1 = subset[subset['Medal']!='NA']
    #seasons_GOLD = seasons_medals1.groupby('Season')['Gold'].count()
    #seasons_Silver = seasons_medals1.groupby('Season')['Silver'].count()
    #seasons_Bronze= seasons_medals1.groupby('Season')['Bronze'].count()
    
    
    #seaons_golden=subset.groupby('Season')['Gold'].count()
    #seasons_silvery=subset.groupby('Season')['Silver'].count()
    #seasons_bronzy=subset.groupby('Season')['Bronze'].count()

    #n=seaons_golden.index
    #index = np.arange(n)

    #fig, ax = plt.subplots()
    #bar_width = 0.3
    #opacity = 0.9
    #ax.bar(index, seaons_golden, bar_width, alpha=opacity, color='r', label='Gold')
    #ax.bar(index+bar_width, seasons_silvery, bar_width, alpha=opacity, color='b', label='Silver')
    #ax.bar(index+2*bar_width, bar_width, alpha=opacity,color='k', label='Bronze')
    #st.pyplot()




