import streamlit as st
import warnings
warnings.filterwarnings("ignore")
# EDA Pkgs
import pandas as pd
import numpy as np
import pandas as pd
import tweepy
import json
from tweepy import OAuthHandler
import re
import openpyxl
import time
import tqdm
import pickle
import string
from string import digits

punctuations = '''`÷×؛<>_()*&^%][ـ،/:"؟.,'{}~¦+|!”…“–ـ''' + string.punctuation

import nltk
from nltk.corpus import stopwords
stop = stopwords.words('arabic')
#words = set(nltk.corpus.words.words())
arab_stopwords = set(nltk.corpus.stopwords.words("arabic"))

arab_stopwords = r'\b(?:{})\b'.format('|'.join(arab_stopwords))
arabic_diacritics = re.compile("""
                             ّ    | # Shadda
                             َ    | # Fatha
                             ً    | # Tanwin Fath
                             ُ    | # Damma
                             ٌ    | # Tanwin Damm
                             ِ    | # Kasra
                             ٍ    | # Tanwin Kasr
                             ْ    | # Sukun
                             ـ     # Tatwil/Kashida
                         """, re.VERBOSE)

model = pickle.load(open('model.pkl', 'rb'))
#To Hide Warnings
st.set_option('deprecation.showfileUploaderEncoding', False)
st.set_option('deprecation.showPyplotGlobalUse', False)
# Viz Pkgs
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
#sns.set_style('darkgrid')


STYLE = """
<style>
img {
    max-width: 100%;
}
</style> """

def main():

    from PIL import Image
    im = Image.open('t.png')
    st.image(im, caption='',use_column_width='auto', width = 350)
    #st.title("Sentiment Analysis Tool for Arabic Tweets")

    ################# Twitter API Connection #######################
    consumer_key = 'qJMwGaoSTmGaAQCiqECHBacSR'
    consumer_secret = '63GDaykQ0sF2JCFSniJtgUo2qqnddJqVbkShvCn36Ci4ptf5vd'
    access_token = '1400486892-o6f21Eo5v4fshZwrAjeUJmelhQBxW0P53yyRxt9'
    access_token_secret = 'JlivSWZ5dw8KY9YIk5oQuzgiZYwkfINBikGZCIRnwzNCm'



    # Use the above credentials to authenticate the API.

    auth = tweepy.OAuthHandler( consumer_key , consumer_secret )
    auth.set_access_token( access_token , access_token_secret )
    api = tweepy.API(auth)
    ################################################################
    
    df = pd.DataFrame(columns=["Date","User","IsVerified","Tweet","Likes","RT",'User_location'])
    
    # Write a Function to extract tweets:
    def get_tweets(Topic,Count):
        i=0
        for tweet in tweepy.Cursor(api.search, q=Topic,count=100, lang="ar",exclude='retweets').items():
            
            df.loc[i,"Date"] = tweet.created_at
            df.loc[i,"User"] = tweet.user.name
            df.loc[i,"IsVerified"] = tweet.user.verified
            df.loc[i,"Tweet"] = tweet.text
            df.loc[i,"Likes"] = tweet.favorite_count
            df.loc[i,"RT"] = tweet.retweet_count
            df.loc[i,"User_location"] = tweet.user.location

            i=i+1
            if i>Count:
                break
            else:
                pass
    # Function to Clean the Tweet.
    def clean_tweet(tweet):
        remove_digits = str.maketrans('', '', digits)
        tweet =tweet.translate(remove_digits)

        tweet=tweet.translate(str.maketrans('', '', punctuations))#removing all ponctuations
        # remove Tashkeel
        tweet = re.sub(arabic_diacritics, '', str(tweet))
        tweet = re.sub(arab_stopwords, '', tweet)
        tweet = re.sub("@[_A-Za-z0-9]+","",tweet) #Removing mention
        tweet=re.sub("[^\w\s#@/:%.,_-]", "", tweet, flags=re.UNICODE)#REmove emoji
        tweet=re.sub(r'\s*[A-Za-z]+\b', '' , tweet)#remove no arabic word
        tweet=re.sub(r'#','',tweet)# removing hachtag
        tweet=re.sub(r'https?:\/\/\s+','',tweet)#remove the hyper link
        tweet = re.sub("\n","",tweet)
        tweet=re.sub(r'^[A-Za-z0-9.!?:؟]+'," ",tweet) ##Removing digits and punctuations
        tweet = re.sub("\n","",tweet)
        tweet = re.sub(u'\xa0','',tweet)
        tweet = re.sub(r'[\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652]','',tweet)
        tweet = re.sub("[إأٱآا]", "ا", tweet)
        tweet = re.sub("[ااا]+","ا",tweet)
        tweet = re.sub("[a-zA-Z]+","",tweet)
        tweet = re.sub("²", "", tweet)
        tweet = re.sub("[0-9]+","",tweet)
        tweet = re.sub("گ", "ك", tweet)
        tweet = re.sub("[ﷺöüçāīṣııšḥāḫםבםבḥāā]", "",tweet)
        tweet = re.sub("[헨리생일축하해요왕자어린]", "",tweet)
        tweet = re.sub(r'http', '',tweet)
        tweet=re.sub('[٠١٢٣٤٥٦٧٨٩]',"",tweet)
        tweet = re.sub('öü','',tweet)
        return tweet
    
        
    # Funciton to analyze Sentiment
    def analyze_sentiment(tweet):
        data = [tweet]
        df = pd.DataFrame([str(data)], columns=['content'])
        p = model.predict(data)
        if p[0] == 'positive':
            return 'Positive'
        elif p[0] == 'negative':
            return 'Negative'
        else:
            return 'Neutral'
    

    from PIL import Image
    image = Image.open('logo.png')
    st.image(image, caption='',use_column_width='auto', width = 350)


    # Collect Input from user :
    Topic = str()
    Topic = str(st.text_input("    (اضغط Enter)  ادخل عنوان باللغة العربيه انت مهتم بمعرفة تحليله "))
    
    if len(Topic) > 0 :
        
        # Call the function to extract the data. pass the topic and filename you want the data to be stored in.
        with st.spinner("الرجاء الانتظار ، التغريدات في طور الاستخراج"):
            get_tweets(Topic , Count=500)
        st.success('!! تم استخراج التغريدات')
           
    
        # Call function to get Clean tweets
        df['clean_tweet'] = df['Tweet'].apply(lambda x : clean_tweet(x))
    
        # Call function to get the Sentiments
        df["Sentiment"] = df["clean_tweet"].apply(lambda x : analyze_sentiment(x))
        
        
        # Write Summary of the Tweets
        st.write("مجموع التغريدات المستخرجة للموضوع  '{}' هي : {}".format(Topic,len(df.Tweet)))
        st.write("مجموع التغريدات الايجابية هي : {}".format(len(df[df["Sentiment"]=="Positive"])))
        st.write("مجموع التغريدات السلبية هي : {}".format(len(df[df["Sentiment"]=="Negative"])))
        st.write("مجموع التغريدات المحايدة هي : {}".format(len(df[df["Sentiment"]=="Neutral"])))
        
        # See the Extracted Data : 
        if st.button("اطلع على البيانات المستخرجة "):
            st.success("  البيانات المستخرجة في الاسفل")
            st.write(df.head(50))
        
        
        # get the countPlot
        if st.button("(Count Plot) اطّلع على الرسم البياني للمشاعر "):
            st.success("يتم العمل على الرسم البياني")
            st.subheader(" الرسم البياني لمختلف المشاعر")
            st.write(sns.countplot(df["Sentiment"]))
            st.pyplot()
        
        # Piechart 
        if st.button(" (Pie Chart) اطّلع على المخطط الدائري للمشاعر"):
            st.success("يتم العمل على المخطط الدائري")
            a=len(df[df["Sentiment"]=="Positive"])
            b=len(df[df["Sentiment"]=="Negative"])
            c=len(df[df["Sentiment"]=="Neutral"])
            d=np.array([a,b,c])
            explode = (0.1, 0.0, 0.1)
            st.write(plt.pie(d,shadow=True,explode=explode,labels=["Positive","Negative","Neutral"],autopct='%1.2f%%'))
            st.pyplot()




    st.sidebar.header("عن الأداة:")
    st.sidebar.info("الهدف من موقعنا هو تحليل مجموعة من التغريدات حول مجموعة متنوعة من الموضوعات باستخدام أساليب التعلم الآلي الفعالة, جمع التغريدات المتعلقة بأي موضوع عربي ثم تنفيذ تقنية تحليل المشاعر المناسبة للحصول على أعلى نتيجة ممكنة. ")

    st.sidebar.header("للاستفسارات او الإقتراحات الرجاء التواصل على :")
    st.sidebar.info("naifalharbi321@gmail.com\n"
                    "mf.almadi@gmail.com   \n"
                    "talal-ov@hotmail.com\n"
                    "abdullah.ababutain@gmail.com")






if __name__ == '__main__':
    main()

