
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
    -  Feature notebooks 2c and 2d are hidden for IP privacy, for a couple of algorithms I developed years ago. I would be happy to describe the metrics in general though. They are all trying to answer the question, 'for each posession, how much does a player add or take away from a team, considering offense and defense equally?' I will try to provide more clarity in the future.
    -  [Odds & Refs Features](https://github.com/tmcroyce/NBA_Prediction_Classification_Public/blob/master/Printed_PDF_Notebooks/2f_Odds_and_Refs_Features.pdf)
- [Modeling Notebook](https://github.com/tmcroyce/NBA_Prediction_Classification_Public/blob/master/Printed_PDF_Notebooks/3_Win_Classification.pdf)

# Data
- Data was scraped from NBA.com, basketball_reference.com, hoopshype.com, and a small amount from bigdataball.com. 
- 
# Project Overview
The purpose of this project is to create a model to predict the outcome of NBA (National Basketball Association) games. 

The final model tested at 83 percent (rounded). 


### Stakeholders: Bookkeepers, bettors, and speculators. 


This project's end result will be an application which can help identify descrepancies between the "Vegas" odds of a fight and the model-predicted (i.e., theoretically more accurate) odds of that same fight. This could be used by bookmakers to increase revenues by offering slightly "better" odds than competitor bookmakers, given the model indicates it is appropriate. Alternatively, it could simply be used by bookmakers to create more accurate odds than previously, or give individual speculators or bettors insights into more accurate game probabilities. 


### Target Variable

The target variable is if a fighter won an individual fight or not.

### Scoring Metric

Because our data is evenly split between wins and losses, and there is no relative advantage between false negatives and false positives due to having one copy of data for each team for each game; accuracy is my chosen scoring metric.


## Testing and Modeling
The initial model (decision tree) achieved an accuracy of 65%. 

After iterating on a variety of models, including decision tree, logistic regression, bagged trees, extrra trees, KNN, and random forest, I found the best performing model to test at 83% accuracy. 


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
  
  


