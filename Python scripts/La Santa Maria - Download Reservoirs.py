"""
La Santa Maria
Search and Help V9
Author: Santiago Duarte
"""
import os # Use OS functions
from bs4 import BeautifulSoup # Translate Web Page Info 
from googleapiclient.discovery import build   #Import the Google Search Library
import pandas as pd # Woking with DataFrames
from requests import get # Get a WebPage Info
import warnings # Ignore Warnings in the calculations
import itertools # Iteration Tools
import time  # Use time functions as time.time()
import sys # Import sys Functions

def google_query(query, api_key, cse_id, **kwargs):
    query_service = build("customsearch","v1", developerKey=api_key)  
    try:
        query_results = query_service.cse().list(q=query,cx=cse_id,**kwargs).execute()
        searc_result=query_results['items']
    except Exception as e:
        print(e)
        searc_result=0
    return searc_result

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

###### DELETE DUPLICATES ######
temp_reservoris=reservoris.drop_duplicates(subset ='Element').reset_index()
temp_reservoris['DPTO']=[''.join(reservoris['DPTO'].loc[temp_reservoris['Element'][ii]==reservoris['Element']]) for ii in range(temp_reservoris.shape[0])]
reservoris=temp_reservoris.reset_index()

###### DEFINE INICIAL VARIABLES ######
api_key = keys['API_KEY'][0]
cse_id = keys['CSE_ID'][0]
if os.path.isfile(path+'/NewsDB/counter_reservoirs.csv'):
    count_df=pd.read_csv(path+'/NewsDB/counter_reservoirs.csv',index_col='Index')    
else:
    count_df=pd.DataFrame(columns=['Count'],index=reservoris['Element'])
        
#### MAIN ####
print ('Searching News')
count_all=0
for ii in reservoris.index[:]:
    ###### SEARCH NEWS (GOOGLE) ######
    rio=reservoris.loc[ii] 
    print('\nSearching: ... ' + rio['Element'])
    rio_folder=os.path.join(path,'NewsDB',rio['Element'])
    if not os.path.exists(rio_folder):
        os.mkdir(rio_folder)
    items=[sources.loc[j] for j in range(sources.shape[0]) if sources['Extension'][j] in rio['DPTO'] ]
    periodicos=pd.concat([sources[sources['Extension']=='ALL'],pd.DataFrame(items)]).reset_index(drop=True)
    container=[]; count=0
    for fuente in periodicos.index:
        print('    Fuente: ... '+periodicos['Newspaper'].loc[fuente])
        search='"'+rio['Element'].replace(" ","+")+'"'+' site:'+periodicos['URL'].loc[fuente]+" after:2016-01-01 before:2020-12-31"
        lookfor = google_query(search, api_key, cse_id, num = 10, start=1)
        count=count+1
        if lookfor==0:
            continue
        for tema in topics['Water'].dropna():
            print ('            Topico: ... '+tema)
            tema=tema.replace(" ","+")
            search="'"+tema+"' site:"+periodicos['URL'].loc[fuente]+" after:2016-01-01 before:2020-12-31"
            lookfor=[None]*10; n=0; 
            while len(lookfor)==10:
                print('                Página: '+str(int(1+n/10)))
                time.sleep(1) # No superar el limite de 100 busquedas cada 100 segundos
                lookfor = google_query(search, api_key, cse_id, num = 10, start=1+n, sort='date', exactTerms=rio['Element'].replace(" ","+"))
                count=count+1
                if lookfor==0:
                    break
                container.append(lookfor)
                n=n+10
                if n>=100:
                    print('Mas de 10 páginas')  
                    break   
    container_list = list(itertools.chain(*container))  
    if not  os.path.isfile(rio_folder+'/container_list.csv'):
        container_df=pd.DataFrame(container_list)
        container_df.to_csv(rio_folder+'/container_list.csv',index_label='Index')
    else:
        container_df=pd.read_csv(rio_folder+'/container_list.csv',index_col='Index')
        container_list=container_df.to_dict('records')
    count_df['Count'].loc[rio['Element']]=count
    count_df.to_csv(path+'/NewsDB/counter_reservoirs.csv',index_label='Index')
    print('Total de Busquedas '+rio['Element']+': '+str(count))
    count_all=count_all+count
    if count_all>9500:
        sys.exit("Search limit found")
    
#    ###### DELETE REPEATED NEWS ######   
#    print ('    Deleting Repeated and Irrelevant News ...')
#    if not  os.path.isfile(rio_folder+'/container_list.csv'):
#        container_df=pd.DataFrame(container_list)
#        container_df.to_csv(rio_folder+'/container_list.csv',index_label='Index')
#    else:
#        container_df=pd.read_csv(rio_folder+'/container_list.csv',index_col='Index')
#        container_list=container_df.to_dict('records')                  
#    container_list_filter=[]
#    for d in container_list:
#        delete= periodicos['delete'].loc[periodicos['URL']==d['displayLink'].replace('www.','')].values[0]
#        if delete not in d['link']:
#            container_list_filter.append(d)       
#    for d in container_list_filter:
#        if 'htmlSnippet' in d.keys():
#            del d['htmlSnippet'];
#        if 'snippet' in d.keys():
#            del d['snippet'];
#        if 'htmlTitle' in d.keys():
#            del d['htmlTitle'];
#        d['sourceLink']='https://'+d['displayLink']+'/'   
##        d['date']=pd.to_datetime(d['pagemap']['metatags'][0]['article:published_time'])
#    container_clean=[i for n, i in enumerate(container_list_filter) if i not in container_list_filter[n + 1:]]
#    print('Total de Noticias '+rio['Element']+': '+str(len(container_clean)))     
#          
#    ###### DOWNLOAD NEWS (SOURCES) ###### 
#    print ('    Downloading News ...')
#    k_len=0
#    for k in container_clean:
#        print ('        Downloading '+str(k_len+1)+'-'+str(len(container_clean)))
#        div=periodicos['class'].loc[periodicos['URL']==k['displayLink'].replace('www.','')].values[0]       
#        response = get(k['link'])
#        print(response.status_code)
#        soup = BeautifulSoup(response.content, "lxml")        
#        container_clean[k_len]['text']=soup.find_all('div', class_=div)[0].text.lstrip().rstrip()      
#        k_len=k_len+1
#
#    ###### SAVE NEWS LINKS ######    
#    for i in range(len(container_clean)):  
#        news = pd.DataFrame.from_dict(container_clean[i], orient="index")                
#        news.to_csv(os.path.join(rio_folder,str(i+1)+".csv"), index_label='Parameters')    
#    noticias=pd.DataFrame(container_clean) 
#    noticias.to_csv(os.path.join(rio_folder,rio['Element']+".csv"), index_label='News') 
#
#    ###### TOPICS ######   
#    
#    
#    
#    
#    ###### SENTIMENT ANALYSIS ######  
#    
#    
#    
#    
#    
#    
#    ###### CLOUD OF WORLDS ######  
#
#
#
#
#
#
#
#     ###### CREATE DATA FOR GIS  ######  
#    noticias_elemento=pd.DataFrame(index=['elemento'])
#    noticias_elemento['Links']='\n'.join(noticias['link'])
#    if os.path.isfile(path+'/NewsDB/counter.csv'):
#        count_df=pd.read_csv(path+'/NewsDB/counter.csv',index_col='Index')    
#    else:
#        count_df=pd.DataFrame(columns=['Count'],index=rivers['Element'])
#    noticias_elemento['Total Search']=int(count_df['Count'].loc[rio['Element']])
#    noticias_elemento['Total Articles']=noticias.shape[0]
#    for i in range(1995,2021):
#        noticias_elemento['Topics '+str(i)]='Not Info'
#        noticias_elemento['Sentiment '+str(i)]='Not Info'
#    noticias_elemento['Topics All']='Not Info'    
#    noticias_elemento['Sentiment All']='Not Info'   
#    noticias_elemento=noticias_elemento.reindex(sorted(noticias_elemento.columns), axis=1)
#    noticias_elemento.to_csv(os.path.join(rio_folder,rio['Element']+"_GIS.csv")) 
    