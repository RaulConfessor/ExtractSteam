#!/usr/bin/env python
# coding: utf-8

# In[942]:


from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome import options
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup 
import pandas as pd
from datetime import datetime, timedelta


# In[ ]:





# In[943]:


driver = webdriver.Chrome()
driver.get('https://steamdb.info/sales/')


# In[944]:


select_element = driver.find_element(By.ID, 'dt-length-0')

select = Select(select_element)

select.select_by_visible_text('All (slow)')


# In[945]:


tableGames = driver.find_element(By.ID, 'DataTables_Table_0')


# In[946]:


htmlContent = tableGames.get_attribute("outerHtml")


# In[947]:


try:
    table_games = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="DataTables_Table_0"]'))
    )

    html_content = table_games.get_attribute("outerHTML")

    soup = BeautifulSoup(html_content, 'html.parser')

except Exception as e:
    print("Ocorreu um erro:", str(e))
finally:
     driver.quit()


# In[948]:


rows = soup.find_all('tr', class_='app')


# In[949]:


def extract_data(row):
        appid = row.get('data-appid', 'N/A')
        name = row.find('a', class_='b').text if row.find('a', class_='b') else 'N/A'
        discount = row.find('td', class_='price-discount-major dt-type-numeric') or row.find('td', class_='price-discount dt-type-numeric')
        price_elements = row.find_all('td', class_='dt-type-numeric')
        price = price_elements[2].text.strip() if len(price_elements) > 2 else 'N/A'
        rating = price_elements[3].text.strip() if len(price_elements) > 3 else 'N/A'
        release = price_elements[4].text.strip() if len(price_elements) > 4 else 'N/A'

        td_elements = row.find_all('td', class_='timeago dt-type-numeric')
        
        def convert_timestamp(data_sort):
            if data_sort and data_sort.isdigit():
                return datetime.utcfromtimestamp(int(data_sort)).strftime('%Y-%m-%d')
            return 'N/A'

        ends = convert_timestamp(td_elements[0].get('data-sort', '')) if len(td_elements) > 0 else 'N/A'
        started = convert_timestamp(td_elements[1].get('data-sort', '')) if len(td_elements) > 1 else 'N/A'
        
        return {
            'AppID': appid,
            'Name': name,
            'Discount': discount,
            'Price': price,
            'Rating': rating,
            'Release': release,
            'Ends': ends,
            'Started': started
        }


# In[950]:


print('oi')


# In[951]:


data = [extract_data(row) for row in rows]


# In[952]:


df = pd.DataFrame(data)


# In[953]:


df


# In[954]:


df['Release'] = df['Release'].replace('—', '')
df['Release'] = pd.to_datetime(df['Release'], errors='coerce')
df['Release'] = df['Release'].dt.strftime('%Y-%m')

df['Ends'] = pd.to_datetime(df['Ends'], errors='coerce')
df['Started'] = pd.to_datetime(df['Started'],errors='coerce')

today = (datetime.today())

df['Ends'] = (df['Ends'] - today + (timedelta(days=1))).dt.days
df['Started'] = (df['Started'] - today + (timedelta(days=1))).dt.days


# In[955]:


df.head(10)


# In[956]:


print(df.dtypes)


# In[957]:


def removerCaracteres(df,col, caract):
    for char in caract:
        df[col] = df[col].str.replace(char,"")
        
    return df


# In[958]:


df = removerCaracteres(df,'Price',['R',"$"])
df = removerCaracteres(df,'Rating',["%"])


# In[959]:


df.head()


# In[ ]:





# In[960]:


df['Discount'] = df['Discount'].apply(lambda x: re.sub('<.*?>', '', str(x)))
df = removerCaracteres(df,'Discount',["%"])


# In[961]:


df.head()


# In[962]:


df['Started'] = pd.to_numeric(df['Started'], errors='coerce')
df['Started'] = df['Started'].fillna(0).astype(int)


# In[965]:


print(df.dtypes)


# In[966]:


df['Discount'] = pd.to_numeric(df['Discount'], errors='coerce')
df['Discount'] = df['Discount'].astype(float)
df['Discount'] = df['Discount'].apply(lambda x: x / (-100) if pd.notnull(x) else x)


df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
df['Rating'] = df['Rating'].astype(float)

df['Price'] = df['Price'].str.replace(',', '.')
df['Price'] = df['Price'].astype(float)

df['Release'] = df['Release'].replace('—', '')
df['Release'] = pd.to_datetime(df['Release'], errors='coerce')
df['Release'] = df['Release'].dt.strftime('%Y-%m')

df['AppID'] = df['AppID'].astype(int)


# In[967]:


print(df.dtypes)


# In[968]:


df.head(50)


# In[969]:


df["Discount"] = df["Discount"].fillna(0)


# In[970]:


df.head(5)


# In[971]:


df.to_json(r'C:\Users\Raul\Desktop\Programação\Dados\Pandas\SteamSales.json', orient='records',lines=True)


# In[972]:


df.to_csv(r'C:\Users\Raul\Desktop\Programação\Dados\Pandas\SteamSales.csv', index=False)


# In[ ]:




