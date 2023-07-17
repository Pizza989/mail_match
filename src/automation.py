import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


class DataSet:
    feature_extraction = TfidfVectorizer(min_df=1, stop_words="english", lowercase=True)

