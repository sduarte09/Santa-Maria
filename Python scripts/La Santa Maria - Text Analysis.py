"""
La Santa Maria
Text Analysis
Author: Santiago Duarte
"""
import os # Use OS functions
import pandas as pd # Woking with DataFrames
import warnings # Ignore Warnings in the calculations
import itertools
import re
import string
from wordcloud import WordCloud,ImageColorGenerator
import matplotlib.pyplot as plt
import numpy as np    
from PIL import Image  
import random
from sklearn.feature_extraction.text import CountVectorizer
from gensim import matutils, models
import scipy.sparse
# import nltk
# nltk.download('all')
from nltk.corpus import stopwords    
from classifier import SentimentClassifier
import math
from nltk import word_tokenize, pos_tag
clf = SentimentClassifier()
import csv

def clean_text_round1(text):
    '''Make text lowercase, remove text in square brackets, remove punctuation and remove words containing numbers.'''
    text = text.lower()
    text = re.sub('\[.*?¿\]\%', ' ', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), ' ', text)
    text = re.sub('\w*\d\w*', '', text)
    return text

# Apply a second round of cleaning
def clean_text_round2(text):
    '''Get rid of some additional punctuation and non-sensical text that was missed the first time around.'''
    text = re.sub('[‘’“”…«»]', '', text)
    text = re.sub('\n', ' ', text)
    return text

def clean_all(texto):
    texto.insert(2,'text clean','')
    for jj in texto.index:
        text2= clean_text_round1(texto['text'].loc[jj])
        text3= clean_text_round2(text2) ### ADD Space in all words
        texto['text clean'].loc[jj]=text3.replace('AdsDisplay("Nativead_Interes_Horizontal ")',
                ' ').replace('AdsDisplay("Banner_Mobile") ',' ').replace('adsdisplay ', ' ').replace('call ',
                ' ').replace('invoke ',' ').replace('function ',' ').replace('googletag ',' ').replace(' div ',
                ' ').replace('push ',' ').replace(' appnexus ',' ').replace(' CDATA ',' ').replace(' cX ',' ').replace(' cx ',
                ' ').replace(' cdata ',' ').replace(' display ',' ').replace(' queue ',' ').replace(' cmd ',
                ' ').replace(' gpt ',' ').replace(' ad ',' ').replace(' appnexus ',' ').replace(' appnexus ',
                ' ').replace(' window ',' ').replace(' Click ',' ').replace(' passback ',' ').replace(' breakpoints ',
                ' ').replace(' share ',' ').replace(' Opens ',' ').replace(' enableServices ',' ').replace(' pubads ',
                ' ').replace(' BannerUPDuplicadoMovil ',' ').replace(' Facebook ',' ').replace(' WhatsApp ',
                ' ').replace(' appnexus ',' ').replace(' Pinterest ',' ').replace(' Twitter ',' ').replace(' LinkedIn ',
                ' ').replace(' Telegram ',' ').replace(' Skype ',' ').replace(' print ',' ').replace(' themoneytizer ',
                ' ').replace(' COMPARTIR ',' ').replace(' RobaPagina ',' ').replace(' ValidateItemUltimaHora ',
                ' ').replace(' weather ',' ').replace(' widgets ',' ').replace(' sabagh ',' ').replace(' widget ',
                ' ').replace(' location ',' ').replace(' size ',' ').replace(' sizes ',' ').replace(' browser ',
                ' ').replace(' opens ',' ').replace(' in ',' ').replace(' new click ',' ').replace(' do ',
                ' ').replace(' día ',' ').replace(' top ',' ').replace(' sección ',' ').replace(' value ',
                ' ').replace(' target ',' ').replace(' node ',' ').replace(' text ',' ').replace(' lk ',
                ' ').replace(' out ',' ').replace(' of ',' ').replace(' banner ',' ').replace(' mega ',
                ' ').replace(' slug ',' ').replace(' año ',' ').replace(' tag ',' ').replace(' sense ',' ').replace(' page ',
                ' ').replace(' short ',' ').replace(' types ',' ').replace(' breakpots ',' ').replace(' nids ',
                ' ').replace(' second ',' ').replace(' channel ',' ').replace(' colors ',' ').replace(' background ',
                ' ').replace(' border ',' ').replace(' url ',' ').replace(' id ',' ').replace(' unit ',
                ' ').replace('lun ',' ').replace(' vie ',' ').replace('míe ',' ').replace(' mar ',
                ' ').replace('sab ',' ').replace(' dom ',' ').replace(' mobile ',' ').replace(' adsense ',
                ' ').replace(' table ',' ').replace(' dfp ',' ').replace(' seccion ',' ').replace(' slot ',
                ' ').replace(' type ',' ').replace(' ft ',' ').replace(' ee ',' ').replace(' export ', 
                ' ').replace(' section ',' ').replace(' block ',' ').replace(' settgs ',' ').replace(' tema ',  
                ' ').replace(' pattern ',' ').replace(' module ',' ').replace(' to ',' ').replace(' contenl ',                                                                           
                ' ').replace(' args ',' ').replace(' term ',' ').replace(' settgs ',' ').replace(' sobrescrito ', 
                ' ').replace(' section ',' ').replace(' block ',' ').replace(' settgs ',' ').replace(' link ', 
                ' ').replace('posicion',' ').replace('sobreescrito',' ').replace('adunit',' ').replace('field',  
                ' ').replace('machinename',' ').replace('adid',' ').replace(' ads ',' ').replace('pagina',
                ' ').replace('posicion',' ').replace('tag',' ').replace('adunit',' ').replace('blacklist',    
                ' ').replace('call',' ').replace('queue',' ').replace('settings',' ').replace('call',
                ' ').replace('targeting',' ').replace('contenido',' ').replace('foto',' ').replace('network',                                                                                     
                ' ').replace('linkedin',' ').replace('enableservices',' ').replace('twitter',' ').replace('facebook',                                                                                     
                ' ').replace('sitionuevo',' ').replace('wrapper',' ').replace('addservice',' ').replace(' com ',
                ' ').replace('cryptocanthon',' ').replace('uno',' ').replace('dos',' ').replace('tres',                                                                                     
                ' ').replace('linkedin',' ').replace('enableservices',' ').replace('twitter',' ').replace('facebook',                                                                                                         
                ' ').replace('skype',' ').replace('defineslot',' ').replace('click',' ').replace('maicolmedia',  
                ' ').replace(' slider ',' ').replace(' ss ',' ').replace(' parameter ',' ').replace(' thumbnail ', 
                ' ').replace('json',' ').replace('parse',' ').replace('apto',' ').replace('archivo',        
                ' ').replace(' prototype ',' ').replace(' style ',' ').replace(' width ',' ').replace(' allign ',                                                                                 
                ' ').replace(' border ',' ').replace(' pinterest ',' ').replace(' nid ',' ').replace(' ids ',' ')                                                                    
    return texto

def cloud(texto, stop_words, img_folder, cloud_folder,name):
    # Generate a word cloud image
    mask_id=str(random.randint(1, 23))
    mask = np.array(Image.open(img_folder+mask_id+'.png'))
    wordcloud_spa = WordCloud(stopwords=stop_words, background_color="white", max_words=200, 
                              mask=mask).generate(nouns(' \n'.join(texto['text clean'])))
    image_colors = ImageColorGenerator(mask) # Create coloring from image
    plt.figure(figsize=[7,7])
    plt.imshow(wordcloud_spa.recolor(color_func=image_colors), interpolation="bilinear")
    plt.imshow(mask, alpha=0.2) # Backgroud Image
    plt.axis("off")
    plt.title(name, loc='center', y=-0.14, fontsize=36)
    plt.savefig(os.path.join(cloud_folder,name+'.png')) # Store to file

def format_topics_sentences(ldamodel, corpus, texts):
    # Init output
    sent_topics_df = pd.DataFrame()
    # Get main topic in each document
    for i, row_list in enumerate(ldamodel[corpus]):
        row = row_list[0] if ldamodel.per_word_topics else row_list            
        # print(row)
        row = sorted(row, key=lambda x: (x[1]), reverse=True)
        # Get the Dominant topic, Perc Contribution and Keywords for each document
        for j, (topic_num, prop_topic) in enumerate(row):
            if j == 0:  # => dominant topic
                wp = ldamodel.show_topic(topic_num)
                topic_keywords = ", ".join([word for word, prop in wp])
                sent_topics_df = sent_topics_df.append(pd.Series([int(topic_num), round(prop_topic,4), topic_keywords]), ignore_index=True)
            else:
                break
    sent_topics_df.columns = ['Dominant_Topic', 'Perc_Contribution', 'Topic_Keywords']   
    # Add original text to the end of the output
    contents = pd.Series(texts)
    sent_topics_df = pd.concat([sent_topics_df, contents], axis=1)
    return(sent_topics_df)

def nouns(text):
    '''Given a string of text, tokenize the text and pull out only the nouns.'''
    is_noun = lambda pos: pos[:2] == 'NN'
    tokenized = word_tokenize(text,language='spanish')
    all_nouns = [word for (word, pos) in pos_tag(tokenized) if is_noun(pos)] 
    return ' '.join(all_nouns)

def split_text(text, n=12):
    '''Takes in a string of text and splits into n equal parts, with a default of 12 equal parts.'''
    # Calculate length of text, the size of each chunk of text and the starting points of each chunk of text
    length = len(text)
    size = math.floor(length / n)
    start = np.arange(0, length, size)
    # Pull out equally sized pieces of text and put it into a list
    split_list = []
    for piece in range(n):
        split_list.append(text[start[piece]:start[piece]+size])
    return split_list

def topicos(news,stop_words):
        if len(news['text clean'].values)!=0:
            texto_clean=' \n'.join(news['text clean'])
            index_clean=news['date'][0:1]
            data_clean  = pd.DataFrame(columns=['transcript'],index=pd.to_datetime(index_clean),
                                   data=texto_clean) 
            data_clean = data_clean.sort_index()    # Recreate document-term matrix
            cv = CountVectorizer(stop_words=stop_words)
            data_nouns= pd.DataFrame(columns=['transcript'],index=pd.to_datetime(index_clean),
                                   data=nouns(texto_clean)) 
            data_cv = cv.fit_transform(data_nouns['transcript'])
            data_stop = pd.DataFrame(data_cv.toarray(), columns=cv.get_feature_names())
            data_stop.index = data_nouns.index
            tdm = data_stop.transpose() # Term-document matrix
            sparse_counts = scipy.sparse.csr_matrix(tdm) # term-document matrix into a new gensim format
            corpus = matutils.Sparse2Corpus(sparse_counts)
            id2word = dict((v, k) for k, v in cv.vocabulary_.items())     # Gensim also requires dictionary of the all terms and their respective location in the term-document matrix
            lda = models.LdaModel(corpus=corpus, id2word=id2word, num_topics=2, passes=10)
            df_topic_sents_keywords = format_topics_sentences(ldamodel=lda, corpus=corpus, texts=texto_clean)
            key_topics=df_topic_sents_keywords['Topic_Keywords'][0] 
        else:
            key_topics=''
        return key_topics
    
## DEFINE MAIN FOLDER ##
print('La Santa Maria\n')
print('Welcome ... User ... \n')
warnings.filterwarnings('ignore')   
path='C:/Users/Alejandra/Desktop/La Santa Maria/'

###### LOAD DATA BASES ######
rivers=pd.read_csv(path+'Search/Parameters/Rivers.csv')
places=pd.read_csv(path+'Search/Parameters/Municipalities.csv')
reservoris=pd.read_csv(path+'Search/Parameters/Reservoirs.csv')

topics=pd.read_csv(path+'Search/Parameters/Key Words.csv')
sources=pd.read_csv(path+'Search/Parameters/Newspapers.csv')
keys=pd.read_csv(path+'Search/Scripts/API_KEY.csv')
bag_file=path+'WebPage/Bag of Words.csv'

###### DELETE DUPLICATES ######
temp_rivers=rivers.drop_duplicates(subset ='Element').reset_index()
temp_rivers['DPTO']=[''.join(rivers['DPTO'].loc[temp_rivers['Element'][ii]==rivers['Element']]) for ii in range(temp_rivers.shape[0])]
rivers=temp_rivers.reset_index()

temp_reservoris=reservoris.drop_duplicates(subset ='Element').reset_index()
temp_reservoris['DPTO']=[''.join(reservoris['DPTO'].loc[temp_reservoris['Element'][ii]==reservoris['Element']]) for ii in range(temp_reservoris.shape[0])]
reservoris=temp_reservoris.reset_index()

### Change for rivers, reservoirs or municipalities
elements=rivers

###### DEFINE INICIAL VARIABLES ######
api_key = keys['API_KEY'][0]
cse_id = keys['CSE_ID'][0]
dates_main=[2016,2017,2018,2019,2020]
dates_sec=pd.to_datetime([str(r[0]) +'-'+ str(r[1]) for r in itertools.product(dates_main, list(range(1,13)))])[:-6]
img_folder=path+'\\Search\\Scripts\\cloud_pictures\\'
cloud_folder=path+'WebPage/Cloud_web'
if not os.path.exists(cloud_folder):
    os.mkdir(cloud_folder)
        
###### DEFINE OUTPUT RESULT ######
noticias_gis=elements.copy()

# Monthly Results
for i in dates_sec:
    noticias_gis['Topics '+str(i.year)+'-'+str(i.month)]='Not Info'
    noticias_gis['Sentiment '+str(i.year)+'-'+str(i.month)]='Not Info'
    noticias_gis['Links '+str(i.year)+'-'+str(i.month)]='Not Info'
    # noticias_gis['Text '+str(i.year)+'-'+str(i.month)]='Not Info'
    noticias_gis['Total Articles '+str(i.year)+'-'+str(i.month)]='Not Info'
# Anually Results
for i in dates_main:
    noticias_gis['Topics '+str(i)]='Not Info'
    noticias_gis['Sentiment '+str(i)]='Not Info'
    noticias_gis['Links '+str(i)]='Not Info'
    # noticias_gis['Text '+str(i)]='Not Info'
    noticias_gis['Total Articles '+str(i)]='Not Info'
# Overall
noticias_gis['Topics Overall']='Not Info'
noticias_gis['Sentiment Overall']='Not Info'
noticias_gis['Links Overall']='Not Info' 
# noticias_gis['Text Overall']='Not Info'   
noticias_gis['Total Articles']='Not Info'
# Sort
noticias_gis=noticias_gis.reindex(sorted(noticias_gis.columns), axis=1)

###### STOP WORDS ######
# Add Stop Words From NTLK
add_stop_words = set(stopwords.words('spanish')) 
# Add Stop Words From TXT File
with open('spanish.txt') as f:
    stop_words = f.read().splitlines()
# Add More Stop Words    
more_stop_words=['kilometro','qué','call']
for pal in add_stop_words:
        stop_words.append(pal)
for pal in more_stop_words:
    stop_words.append(pal)
    
#### MAIN ####
for ii in elements.index[:]:
    rio=elements.loc[ii] 
    print('\n Analizing Text... ' + rio['Element'])    
    rio_folder=os.path.join(path,'NewsDB',rio['Element'])
    if not os.path.exists(rio_folder):
        os.mkdir(rio_folder)  
    local_GIS=os.path.join(rio_folder,rio['Element']+"_GIS.csv")
    if os.path.isfile(local_GIS):
        noticias_gis.loc[noticias_gis['Element']==rio['Element']]=local_GIS
        continue
    ###### LOAD DATA ######
    if os.path.isfile(os.path.join(rio_folder,rio['Element']+".csv")):
        noticias=pd.read_csv(os.path.join(rio_folder,rio['Element']+".csv"),index_col='News')
        noticias = noticias.drop_duplicates(subset='cacheId', keep='first')
        if len(noticias)!=0:
            noticias = noticias[noticias['text'].notna()].reset_index()   
            noticias['real date']=pd.to_datetime(noticias['date'])
        else:
         continue   
    else:
        continue
    ####################### TEXT ANALYSIS #######################
    #############################################################
    bag_words=[]
    noticias=clean_all(noticias) 
    ###### CLOUD OF WORDS  ######      
    cloud(noticias, stop_words, img_folder,cloud_folder,rio['Element'])
    ###### SENTYMENT ANALYSIS  ######        
    noticias['Sentiment']=[clf.predict(noticias['text clean'].loc[j]) for j in range(noticias.shape[0])]
    ###### OVERALL ######
    print('\n Overall')
    news=noticias.copy()
    noticias_gis['Links Overall'][ii]=' \n'.join(news['link'])
    # noticias_gis['Text Overall'][ii]=' \n'.join(news['text'])   
    noticias_gis['Total Articles'][ii]=news.shape[0]
    
    ###### Topics Modelling  ###### 
    noticias_gis['Topics Overall'][ii]=topicos(news,stop_words)
    bag_words.append([x.strip() for x in noticias_gis['Topics Overall'][ii].split(',')])
    ###### Sentment Analysis  ######           
    noticias_gis['Sentiment Overall'][ii]=news['Sentiment'].mean()
    
    ###### ANUALLY ######
    print('\n Anually ...')
    for fecha_main in dates_main:
        news=noticias.copy()
        news.index=news['real date']
        news=news.loc[(news.index.year==fecha_main)]
        noticias_gis['Links '+str(fecha_main)][ii]=' \n'.join(news['link'])
        # noticias_gis['Text '+str(fecha_main)][ii]=' \n'.join(news['text'])
        noticias_gis['Total Articles '+str(fecha_main)][ii]=news.shape[0]
        ###### Topics Modelling  ###### 
        noticias_gis['Topics '+str(fecha_main)][ii]=topicos(news,stop_words)
        bag_words.append([x.strip() for x in noticias_gis['Topics '+str(i)][ii].split(',')])
        ###### Sentment Analysis  ######
        noticias_gis['Sentiment '+str(fecha_main)][ii]=news['Sentiment'].mean()

    ###### MONTHLY ######
    print('\n Monthly ...')
    for fecha_sec in dates_sec:
        news=noticias.copy()
        news.index=news['real date']
        news=news.loc[(news.index.year==fecha_sec.year) & (news.index.month==fecha_sec.month)]
        noticias_gis['Links '+str(fecha_sec.year)+'-'+str(fecha_sec.month)][ii]=' \n'.join(news['link'])
        # noticias_gis['Text '+str(fecha_sec.year)+'-'+str(fecha_sec.month)][ii]=' \n'.join(news['text'])
        noticias_gis['Total Articles '+str(fecha_sec.year)+'-'+str(fecha_sec.month)][ii]=news.shape[0]
        ###### Topics Modelling  ###### 
        noticias_gis['Topics '+str(fecha_sec.year)+'-'+str(fecha_sec.month)][ii]=topicos(news,stop_words)
        bag_words.append([x.strip() for x in noticias_gis['Topics '+str(fecha_sec.year)+'-'+str(fecha_sec.month)][ii].split(',')])
        ###### Sentment Analysis  ######
        noticias_gis['Sentiment '+str(fecha_sec.year)+'-'+str(fecha_sec.month)][ii]=news['Sentiment'].mean()
            
    ###### BAG OF KEY WORDS ######
    if os.path.isfile(bag_file):
        big_bag_words=list(pd.read_csv(bag_file)['0'].values)
        bag_words = [item for sublist in bag_words for item in sublist]
        big_bag_words=big_bag_words+bag_words
        big_bag_words_df =pd.DataFrame(list( dict.fromkeys(big_bag_words)))
        big_bag_words_df.to_csv(bag_file) 
    else:
        bag_words = [item for sublist in bag_words for item in sublist]
        bag_words_df =pd.DataFrame(list( dict.fromkeys(bag_words)))
        bag_words_df.to_csv(bag_file) 
    
    #####  SAVE LOCAL RESULTS #####    
    print('\n Saving Results ... ')
    noticias_gis_element=noticias_gis.loc[noticias_gis['Element']==rio['Element']]
    noticias_gis_element.to_csv(local_GIS) 
    noticias_gis_element.to_excel(local_GIS[:-4]+'.xlsx', engine='openpyxl')
    noticias.to_csv(os.path.join(rio_folder,rio['Element']+"_analized.csv"), sep = ',', index = False, quoting=csv.QUOTE_ALL)
    ##### SAVE GLOBAL RESULTS ##### 
    noticias_gis.to_csv(os.path.join(path,'NewsDB\GIS.csv'), sep = ',', index = False, quoting=csv.QUOTE_ALL) 
    noticias_gis.to_excel(os.path.join(path,'NewsDB\GIS.xlsx'), engine='openpyxl') 