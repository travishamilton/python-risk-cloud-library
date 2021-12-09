from riskcloudpy import Session
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate

base_url = ''
username = ""
password = ""

####################################################
############----Send Requests to API----############
####################################################

session = Session(username,password,base_url)
assert(session.authentication_status==200)

r = session.account_endpoint()
assert(r.status_code==200)

r = session.applications_endpoint()
assert(r.status_code==200)

####################################################
####----Convert Json Response into Dataframe----####
####################################################

df = pd.DataFrame(r.json())

####################################################
####----Convert Time Series Data to CST Time----####
####################################################

#created and updated are in Unix ms time. Convert to date time
df['created'] = pd.to_datetime(df['created'], unit='ms')
df['updated'] = pd.to_datetime(df['updated'], unit='ms')

#set time zone to UTC and convert to US/Central
df.created = df.created.dt.tz_localize('UTC').dt.tz_convert('US/Central')
df.updated = df.updated.dt.tz_localize('UTC').dt.tz_convert('US/Central')
df['active']= (df.updated-df.created).dt.days

today = pd.to_datetime('today').normalize()
today = today.tz_localize('US/Central')

df['best active']= (today-df.created).dt.days

cutoff = pd.to_datetime('2019-01-01')
cutoff = cutoff.tz_localize('US/Central')

####################################################
###############----Plot Dataframe ---###############
####################################################

fig, axs = plt.subplots(figsize=(12,4))
df.groupby(df['created'].dt.hour).size().plot(kind='bar',rot=0,ax=axs)
plt.xlabel("Hour of the Day Application is Created")
plt.ylabel("Number of Applications")
plt.title("Number of Applications vs. Hour of the Day of Creation (CST)")

fig, axs = plt.subplots(figsize=(12,4))
df[df.active>0.0].plot(x='created',y='active',kind='scatter',ax=axs,logy=True, c='color')
df[df.active>0.0].plot(x='created',y='best active',kind='line',ax=axs,logy=True)
plt.title("Application Active Time (Days) vs. Creation Date with App Color")
plt.ylabel("active (days)")

fig, axs = plt.subplots(figsize=(12,4))
df.plot(x='created',y='updated',kind='scatter',ax=axs,c='color')
plt.title("Application Update Date vs. Creation Date with App Color")

####################################################
#############----Tabulate Dataframe ---#############
####################################################

print(tabulate(df[df['updated']<cutoff].sort_values(by='updated',ascending=True)[['name','updated','color','id']],headers='keys',tablefmt='psql'))

print(tabulate(df.sort_values(by=['active'],ascending=[False])[['name','active','created','color','id']].head(10),headers='keys',tablefmt='psql'))


plt.show()




