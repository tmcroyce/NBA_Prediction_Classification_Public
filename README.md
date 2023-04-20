
# NBA Machine Learning Prediction (Classification) for Team Wins

![Basketball](images/ball.png)

# Intro
This repository contains much more than just the Machine Learning Prediction Classification Files, as it also contains all of the ancilary applications built off of the data that underpins the prediction. With that being said, here are the necessary scraping and prediction files:

# Files
- [PDF Presentation](https://github.com/tmcroyce/NBA_Prediction_Classification_Public/blob/master/Printed_PDF_Notebooks/NBA%20Prediction%20Presentation%20PDF.pdf)
- Video Presentation of Streamlit Application *NOT COMPLETE*
- Scraping Notebooks
  - [Player Data Scraping](https://github.com/tmcroyce/NBA_Prediction_Classification_Public/blob/master/Printed_PDF_Notebooks/1a_Player_Data_Scraping.pdf)
  - [Team Data Scraping](https://github.com/tmcroyce/NBA_Prediction_Classification_Public/blob/master/Printed_PDF_Notebooks/1b_Team_Data_Scraping.pdf)
  - [Contract Scraping](https://github.com/tmcroyce/NBA_Prediction_Classification_Public/blob/master/Printed_PDF_Notebooks/1c_Contracts_Scrape.pdf)
  - [Extra Features](https://github.com/tmcroyce/NBA_Prediction_Classification_Public/blob/master/Printed_PDF_Notebooks/1d_Extra_Feature_Scraping.pdf)
  - [Position by Year](https://github.com/tmcroyce/NBA_Prediction_Classification_Public/blob/master/Printed_PDF_Notebooks/1e_Position_By_Year_Scraping.pdf)
- Feature Notebooks
    -  [Initial Team Features](https://github.com/tmcroyce/NBA_Prediction_Classification_Public/blob/master/Printed_PDF_Notebooks/2a_Initial_Team_Features.pdf)
    -  [More Team Features](https://github.com/tmcroyce/NBA_Prediction_Classification_Public/blob/master/Printed_PDF_Notebooks/2b_More_Team_Features.pdf)
    -  [Odds & Refs Features](https://github.com/tmcroyce/NBA_Prediction_Classification_Public/blob/master/Printed_PDF_Notebooks/2f_Odds_and_Refs_Features.pdf)
- [Modeling Notebook](https://github.com/tmcroyce/NBA_Prediction_Classification_Public/blob/master/Printed_PDF_Notebooks/3_Win_Classification.pdf)


# Project Overview
The purpose of this project is to create a model to predict the outcome of NBA (National Basketball Association) games. 

The final model tested at 83 percent (rounded). 

# Business Understanding
The business question for this project was “can I predict NBA games with high accuracy?”

This question is important for both sides of the recently-legalized sports betting world; both oddsmakers and speculators (bettors) need to model sporting events at the highest accuracy possible. For oddsmakers, this allows them to set optimal odds spreads. For individual speculators, it allows them to calculate expected value with increased accuracy.

# Data
The data comes from a plethora of different scraped sources, the most important being [Nba.com](http://Nba.com) statistics. Other sources include:

- Oddsshark
- Rotowire
- Draftkings
- Spotrac
- BigDataBall
- BasketballReference

The variables include thousands of individual and team metrics which are eventually boiled down to a number slightly under 1000 for the final testing. This is because many of the final variables needed intermediate variables to be able to calculate them. For instance, I needed to keep in the in-game statistics for each game (such as points scored, assists, blocks, etc) in order to calculate the running averages for each team for each of these variables. 

The target variable was the winning team. For instance, each game is stored in tabular format, with one column titled ‘Win?’ with either a 1 or 0 indicating win or loss. 

I chose not to include playoff games, and instead to focus on regular season basketball. This is because I believe the variables that lead to playoff wins and losses to be sufficiently different than the variables that lead to regular season wins and losses. 

Other pieces of data from sources I do not have access to - such as second spectrum or other advanced nba analytics companies - would be very helpful in increasing the accuracy of the overall model, in my opinion.

### Data Preparation

All of the data was collected via scraping. I know this was not completely necessary, but I find scraping to be a fun challenge and good problem solving practice (aka, fun). The data is stored in a tabular format as CSVs. 

To add features to the dataset, I typically utilized the apply method. While this was accurate, it is not very fast, and preparing the entirety of the dataset from scrape to prepared would likely take a couple of days. If you were to skip the scrape and just do the data preparation and application of additional features, it would still likely take over a full day with a strong computer.


### Stakeholders: Bookkeepers, bettors, and speculators. 


This project's end result will be an application which can help identify descrepancies between the "Vegas" odds of a fight and the model-predicted (i.e., theoretically more accurate) odds of that same fight. This could be used by bookmakers to increase revenues by offering slightly "better" odds than competitor bookmakers, given the model indicates it is appropriate. Alternatively, it could simply be used by bookmakers to create more accurate odds than previously, or give individual speculators or bettors insights into more accurate game probabilities. 


### Target Variable

The target variable is if a fighter won an individual fight or not.

### Scoring Metric

Because our data is evenly split between wins and losses, and there is no relative advantage between false negatives and false positives due to having one copy of data for each team for each game; accuracy is my chosen scoring metric.


## Testing and Modeling
The initial model (decision tree) achieved an accuracy of 65%. 

After iterating on a variety of models, including decision tree, logistic regression, bagged trees, extrra trees, KNN, and random forest, I found the best performing model to test at 83% accuracy. 

### Modeling

- Accuracy was the chosen metric, as this was a completely 50/50 split dataset, with each game repeating twice, once from the viewpoint of each of the two teams. Thus, focusing on another metric would only decrease accuracy, which we are trying to optimize.


- The models ran included:
    - Logistic Regression
    - Decision Tree
    - Bagged Trees
    - Extra Trees
    - Random Forest
    - AdaBoost
    - XGBoost

- Cross Validation was included in both the regular testing and the grid parameter tetsing.

- The best models were the random forest and extra trees models. These models were then gridsearched to optimize.

## Project Conclusion
The final model achieved a 83% (rounded) accuracy. 
The model's most important features included:
- Opening Spread
- Closing Spread
- Moneyline
- Estimate of Points Difference (my metric)
- Estimate of Points Difference based on 40 games (my metric)
- Home or Away
- Estimate of Points Difference based on 80 games (my metric)
- Estimate of Points Difference based on 20 games (my metric)
- Team 1 delta (to league) minue team 2 delta (to league) of +-
- Top 5 predicted winner (my metric, sum of player metrics for 5 best players in game)
    
  ... among many others. 
  
  **Next Steps:**

- More features. I have a list for the next iteration (3.2) of this model that is around 100 features long, which include:
    - Metrics to better value missing players
    - Metrics to better value rookies
    - Metrics to include for team incentives
    - Player-based incentives
    - Distribution statistics
    - Use of harmonic means


