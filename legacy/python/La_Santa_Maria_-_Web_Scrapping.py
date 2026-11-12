"""
La Santa Maria
General News Web Scrapping
Author: Santiago Duarte
"""
import os # Use OS functions
from bs4 import BeautifulSoup # Translate Web Page Info 
import pandas as pd # Woking with DataFrames
from requests import get # Get a WebPage Info
from datetime import datetime,timedelta # Work with datetime format
import warnings # Ignore Warnings in the calculations
import time  # Use time functions as time.time()

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
temp_rivers=rivers.drop_duplicates(subset ='Element').reset_index()
temp_rivers['DPTO']=[''.join(rivers['DPTO'].loc[temp_rivers['Element'][ii]==rivers['Element']]) for ii in range(temp_rivers.shape[0])]
rivers=temp_rivers.reset_index()

temp_reservoris=reservoris.drop_duplicates(subset ='Element').reset_index()
temp_reservoris['DPTO']=[''.join(reservoris['DPTO'].loc[temp_reservoris['Element'][ii]==reservoris['Element']]) for ii in range(temp_reservoris.shape[0])]
reservoris=temp_reservoris.reset_index()

### Change for rivers, reservoirs or municipalities
elements=reservoris

###### DEFINE INICIAL VARIABLES ######
api_key = keys['API_KEY'][0]
cse_id = keys['CSE_ID'][0]
        
#### MAIN ####
print ('Searching News')
for ii in elements.index[80:]:
    ###### SEARCH NEWS (GOOGLE) ######
    rio=elements.loc[ii] 
    print('\nSearching: ... ' +str(ii)+' : ...'+rio['Element'])
    rio_folder=os.path.join(path,'NewsDB',rio['Element'])
    if not os.path.exists(rio_folder):
        os.mkdir(rio_folder)
    items=[sources.loc[j] for j in range(sources.shape[0]) if sources['Extension'][j] in rio['DPTO'] ]
    periodicos=pd.concat([sources[sources['Extension']=='ALL'],pd.DataFrame(items)]).reset_index(drop=True)
    
    ####################### DOWNLOAD NEWS ###### ############## 
    ###### DELETE REPEATED NEWS AND OBSOLETE WEB PAGES ######## 
    print ('    Deleting Repeated and Irrelevant News ...')
    if os.path.isfile(rio_folder+'/container_list.csv'):
        container_df=pd.read_csv(rio_folder+'/container_list.csv', engine ='python')
        if len(container_df)==0:
            continue
        container_df=container_df.sort_values('link', ascending=False)
        container_list=container_df.to_dict('records') 
    print('Total de Resultados '+rio['Element']+': '+str(len(container_list)))                  
    container_list_filter=[]
    for d in container_list:
        if 'htmlSnippet' in d.keys():
            del d['htmlSnippet'];
        if 'htmlTitle' in d.keys():
            del d['htmlTitle'];
        if d['displayLink'][:2]=='m.':
                d['displayLink']=d['displayLink'].replace('m.','')
        d['sourceLink']='https://'+d['displayLink']+'/' 
        try:
            if d['snippet'][0].isdigit():
                d['date']=pd.to_datetime(d['snippet'][:12].replace('.','').replace('Ene','Jan').replace('Abr','Apr').replace('Ago','Aug').replace('Dic','Dec'))
            else:
                now=datetime.today()
                delta=int(d['snippet'][5:7])
                if 'mes' in d['snippet'][:20]:   
                    d['date']=now-timedelta(months=delta)
                else:
                    d['date']=now-timedelta(days=delta)        
            if 'pdf' not in d['link']:
                container_list_filter.append(d)  
        except:
            print('Obsolete page: '+ d['link'])
    container_filter=[i for n, i in enumerate(container_list_filter) if i not in container_list_filter[n + 1:]]
    container_clean_df=pd.DataFrame(container_filter)
    container_clean_df=container_clean_df.groupby((container_clean_df["link"] != container_clean_df["link"].shift()).cumsum().values).first()
    container_clean=container_clean_df.to_dict('records')  
    print('Total de Resultados no duplicados '+rio['Element']+': '+str(len(container_clean)))     
          
    ###### DOWNLOAD NEWS (SOURCES) ###### 
    print ('    Downloading News ...')
    a=time.time()
    container_last=[]
    container_not=[]
    for k in container_clean[:]:
        print ('        Downloading '+str( [i for i,x in enumerate(container_clean) if x == k][0])+'-'+str(len(container_clean)-1))
        try:
            response = get(k['link'])
        except Exception as e:
            print(e)
            continue     
        if response.status_code==200:
            try:
                soup = BeautifulSoup(response.content, "lxml") 
                try:
                    div=periodicos['class'].loc[periodicos['URL']==k['displayLink'].replace('www.','').replace('sostenibilidad.','')].values[0]       
                    k['text']=soup.find_all('div', class_=div)[0].text.lstrip().rstrip()      
                    print(k['link']+'\n'+k['text'][:50])
                except:
                    try:
                        div2=periodicos['class2'].loc[periodicos['URL']==k['displayLink'].replace('www.','')].values[0]       
                        k['text']=soup.find_all('div', class_=div2)[0].text.lstrip().rstrip()         
                        print(k['link']+'\n'+k['text'][:50])           
                    except:
                        try:
                            div3=periodicos['class3'].loc[periodicos['URL']==k['displayLink'].replace('www.','')].values[0]       
                            k['text']=soup.find_all('div', class_=div3)[0].text.lstrip().rstrip()         
                            print(k['link']+'\n'+k['text'][:50])
                        except:   
                            div4=periodicos['class4'].loc[periodicos['URL']==k['displayLink'].replace('www.','')].values[0]       
                            k['text']=soup.find_all('div', class_=div4)[0].text.lstrip().rstrip()         
                            print(k['link']+'\n'+k['text'][:50])            
                container_last.append(k)  
            except:
                print('Incorrect page: '+ k['link'])
                container_not.append(k)
        else:
            print('Server Error:'+str(response.status_code))
        # time.sleep(0.1)
    b=(time.time()-a)/60.0
    print('elapsed time: ' + "{:.2f}".format(b) +' min')
    if len(container_not)!=0: 
        invalid_news='\n'.join(pd.DataFrame(container_not)['link'])
        print('\nNoticias Invalidas :\n'+invalid_news)
    print('Total de Noticias Validas '+rio['Element']+': '+str(len(container_last)))     
    ###### SAVE NEWS LINKS ######  
    print('Saving News')
    for i in range(len(container_last)):  
        news = pd.DataFrame.from_dict(container_last[i], orient="index")                
        news.to_csv(os.path.join(rio_folder,str(i+1)+".csv"), index_label='Parameters')    
    noticias=pd.DataFrame(container_last) 
    noticias.to_csv(os.path.join(rio_folder,rio['Element']+".csv"), index_label='News')