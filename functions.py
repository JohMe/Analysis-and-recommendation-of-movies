# Import packages
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import numpy as np
from scipy.sparse import csr_matrix
import warnings; warnings.simplefilter('ignore')

print('imported successfully')

# Funtion 0: Creating extra column for year of movies and clean data
def cleaning_dataset(movies):
    new = movies["title"].str.split("(", n = 1, expand = True)
    movies["movie title"]= new[0].str.lower()
    movies["year"]= new[1]
    movies["genres"] = movies["genres"].str.lower()
    movies["year"].replace(regex=True,inplace=True,to_replace=r'\D',value=r'')
    movies.drop(columns =["title"], inplace = True)
    movies = movies[['movieId', 'movie title', 'year', 'genres']]
    movies.dropna(inplace = True)
    
    #Create a column with the length of years in each row
    movies["year length"]= movies["year"].str.len()
    #Get indexes for which column year's length is not 4
    indexvalues = movies[movies['year length'] != 4 ].index
    #Delete these row indexes from dataFrame
    movies.drop(indexvalues , inplace=True)
    
    return movies


# First function, allow to get information about the dataset
def statsfunction(ratings, movies):
    
    #Give general info about the dataset
    print('The dataset contains: ', len(ratings), ' ratings of ', len(movies), ' movies.')

    #Data for first graph: number of movies per genre 
    genres = ["action", "adventure", "animation", "children", "comedy", "crime", "documentary", "drama", "fantasy", "film-noir", "horror", "musical", "mystery", "romance", "sci-fi", "thriller", "war", "western"]
    number=[]

    for genre in genres:
        count = len(movies[movies['genres'].str.contains(genre)])
        number.append(count)

    d={'genre':genres,'number':number}
    df=pd.DataFrame(d)

    #Data for second graph: average rating per genre
    average_rating=[]

    for genre in genres:
        genre_movies = movies[movies['genres'].str.contains(genre)]
        avg_genre = ratings[ratings['movieId'].isin(genre_movies['movieId'])].loc[:, 'rating'].mean()
        average_rating.append(round(avg_genre,2))

    e={'genre':genres,'average rating':average_rating}
    table=pd.DataFrame(e)


    #Plot graphs 1 and 2 together:        
    fig, axes = plt.subplots(ncols=2, sharey=False, figsize=(25,10))
    axes[0].bar(df['genre'], df['number'], align='center', color='royalblue', zorder=10)
    axes[0].set(title='Number of movies per genre')
    axes[1].bar(table['genre'], table['average rating'], align='center', color='royalblue', zorder=10)
    axes[1].set(title='Average rating per genre')

    axes[0].tick_params(
        axis='both',
        colors='black',
        labelrotation=90)

    axes[1].tick_params(
        axis='both',  
        colors='black',
        labelrotation=90)

    fig.tight_layout()
    fig.subplots_adjust(wspace=0.035)
    plt.show()

    #Print third graph: Number of movies per year
    years=[]
    for x in movies['year']:
        if x not in years:
            years.append(x)
    years.sort()

    movie_count_year=[]
    for year in years:
        count = len(movies[movies['year'].str.contains(year)])
        movie_count_year.append(count)

    f={'year':years,'number of movies':movie_count_year}
    df2=pd.DataFrame(f)
    df2.plot(title='Number of movies per year',kind="bar", rot=90, x='year', y='number of movies', color='royalblue', figsize=(30,20))
    
    plt.tick_params(
        axis='both',  
        colors='black')
    
    plt.show()


# Second function, allow to look for a movie by title
def movie_info(ratings, movies, title):
    #Find Movie info
    search=movies[movies['movie title'].str.contains(title)]
    movie_name=movies[movies['movieId'].isin(search['movieId'])].groupby('movieId')['movie title'].sum()
    movie_year=movies[movies['movieId'].isin(search['movieId'])].groupby('movieId')['year'].sum()
    average_rating=ratings[ratings['movieId'].isin(search['movieId'])].groupby('movieId')['rating'].mean().round(2)
    number_of_ratings=ratings[ratings['movieId'].isin(search['movieId'])].groupby('movieId')['rating'].count()
    
    #Get output
    output=pd.concat([movie_name, movie_year, average_rating, number_of_ratings,], axis = 1)
    output.columns=['Movie','year', 'avg rating', 'nbr of ratings']
    if output.empty == True:
         return """Sorry we could not find what you're looking for!
Make sure you spelled it correctly! 
        """
    else:
        return output
    
# Third function, allow to find movies that fit criteria (years, genre, avg. rating, number of ratings)

def find_movies(movies, ratings, start, end, genre, times_rated, avg_rating):
    #Filter movies data set for input
    years=movies[(movies['year']>=start) & (movies['year']<=end)]
    genre=years[years['genres'].str.contains(genre)]
    
    #Find average rating and number of ratings for the filtered movies
    average_rating=ratings[ratings['movieId'].isin(genre['movieId'])].groupby('movieId')['rating'].mean().round(2).reset_index()
    number_of_ratings=ratings[ratings['movieId'].isin(genre['movieId'])].groupby('movieId')['rating'].count().reset_index()
    rating_frame=average_rating.merge(number_of_ratings, on='movieId')
    rating_frame.columns=('movieId','average','count')
    
    #Filter for minimum number of ratings and minimum average rating
    minimum_count=rating_frame[rating_frame['count']>=times_rated]
    minimum_average=minimum_count[minimum_count['average']>=avg_rating]
    movie_name=movies[movies['movieId'].isin(minimum_average['movieId'])].groupby('movieId')['movie title'].sum()    
    output_data=minimum_average.merge(movie_name, on='movieId')
    output_data.columns=('movieId','avg rating','nbr of ratings','movie name')
    output_data = output_data[['movieId','movie name','avg rating','nbr of ratings']]
    output_data = output_data.sort_values(by=['avg rating'], ascending=False)

    if output_data.empty == True: 
        return """Sorry we could not find what you're looking for!
Make sure you spelled it correctly! 
            """
    else:
        return output_data[['movie name', 'avg rating', 'nbr of ratings']]
    
# Fourth function, allow to plot the top 15 movies from the selection:

def plot_movies(movies, ratings, start, end, genre):    
    #Filter movies data set for input
    years=movies[(movies['year']>=start) & (movies['year']<=end)]
    genre=years[years['genres'].str.contains(genre)]
    
    #Find average rating and number of ratings for the filtered movies
    average_rating=ratings[ratings['movieId'].isin(genre['movieId'])].groupby('movieId')['rating'].mean().round(2).reset_index()
    number_of_ratings=ratings[ratings['movieId'].isin(genre['movieId'])].groupby('movieId')['rating'].count().reset_index()
    rating_frame=average_rating.merge(number_of_ratings, on='movieId')
    rating_frame.columns=('movieId','average','count')
    
    #Filter for minimum number of ratings and minimum average rating
    minimum_count=rating_frame[rating_frame['count']>=10]
    movie_name=movies[movies['movieId'].isin(minimum_count['movieId'])].groupby('movieId')['movie title'].sum()
    #Include movie name in the table
    output_data=minimum_count.merge(movie_name, on='movieId')
    output_data.columns=('movieId','average','count','movie name')
    output_data = output_data[['movieId','movie name','average','count']]
    output_data = output_data.sort_values(by=['average'], ascending=True)
    output_data = output_data.tail(15)
    
    #Plot the output
    
    #If the sub-dataframe is empty, show an error message
    if output_data.empty == True: 
        return """Sorry we could not find what you're looking for!
Make sure you spelled it correctly! 
            """
    #Otherwise, plot the sub-dataframe
    else:        
        fig, axes = plt.subplots(ncols=2, sharey=True, figsize=(15,10))
        axes[0].barh(output_data['movie name'], output_data['average'], align='center', color='royalblue', zorder=10)
        axes[0].set(title='Average rating per movie')
        axes[1].barh(output_data['movie name'], output_data['count'], align='center', color='grey', zorder=10)
        axes[1].set(title='Number of ratings per movie')

        axes[0].invert_xaxis()
        axes[0].set(yticklabels=output_data['movie name'])
        axes[0].yaxis.tick_left()
        axes[0].tick_params(
            axis='both',
            colors='black')
        
        axes[1].tick_params(
            axis='y',  
            left='off')
        
        axes[1].tick_params(
            axis='x',  
            colors='black') 
        
        fig.tight_layout()
        fig.subplots_adjust(wspace=0.035)
        plt.show()

#Sixth function, allow for user interaction - Put everything together
def interaction(movies, ratings):
    while True:
        action=input("""Hello please enter the number corresponding to your desired action.
        [1] Get information about the dataset
        [2] Search for a movie by title
        [3] Find movies according to certain criteria
        [4] Plot average ratings and number of ratings for top 15 movies of a genre and time period
        [5] Exit
        """)

        if action == '1':
            print(statsfunction(ratings, movies))


        elif action == '2':
            while True:
                title=input("What movie are you looking for? ").lower()
                print("Results for", title)
                print(movie_info(ratings, movies, title)) # have to use print here which makes the output uglier and also prints "none" in case there is no output. If we'll leave it like that I'd suggest we get rid of the "sorry we couldn't find what you are..."
                restart=input('Do you want to try again? [y] or [n]').lower()
                if restart !='y':
                    break

        elif action == '3':
            while True:
                #Define the input variable for function
                try:
                    start,end=input("What period of time are you interest in? Enter start and end year separated by a comma: ").split(',')
                    start=str(start)
                    end=str(end)
                    genre=str(input("""What genre are you looking for? : 
    Genres available: action, adventure, animation, children, comedy, crime, documentary, drama, fantasy, film-Noir, 
    horror, musical, mystery, romance, sci-fi, thriller, war, western
                                """)).lower()
                    times_rated= int(input("How often should a movie at least be rated? "))
                    avg_rating=float(input("What is the minimum average rating you want? "))
                    #Print Function
                    print(find_movies(movies, ratings, start, end, genre, times_rated, avg_rating))                    
                    restart=input('Do you want to try again? [y] or [n]')
                    if restart !='y':
                        break
                except ValueError:
                    print("Error - Please make sure that you follow the instructions and enter the correct type of data")

        elif action == '4':
            while True:
                #Define the input variable for function
                try:
                    start,end=input("What period of time are you interest in? Enter start and end year separated by a comma: ").split(',')
                    start=str(start)
                    end=str(end)
                    genre=str(input("""What genre are you looking for? : 
    Genres available: action, adventure, animation, children, comedy, crime, documentary, drama, fantasy, film-Noir, 
    horror, musical, mystery, romance, sci-fi, thriller, war, western
                                """)).lower()
                    #Print Function
                    print(plot_movies(movies, ratings, start, end, genre))
                    restart=input('Do you want to try again? [y] or [n]')
                    if restart !='y':
                        break
                except ValueError:
                    print("Error - Please make sure that you follow the instructions and enter the correct type of data")

        end=input('Do you want to end the program? [y] or [n]').lower()
        if end == 'y':
            print("Thank you, bye!")
            break