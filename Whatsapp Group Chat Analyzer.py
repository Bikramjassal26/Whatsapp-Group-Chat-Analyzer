#!/usr/bin/env python
# coding: utf-8

# In[101]:


import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
import emoji


# In[2]:


f = open ("F:\Resume Projects\Whatsapp Group Chat Analyzer\_chat.txt", 'r', encoding='utf-8')


# In[3]:


data = f.read()


# In[4]:


data


# In[5]:


pattern = '\[(\d{4}-\d{2}-\d{2},\s\d{1,2}:\d{2}:\d{2}\s[APMapm]{2})\]'


# In[6]:


messages = re.split(pattern, data)
len(messages)


# In[7]:


len(messages)


# In[8]:


dates = re.findall(pattern, data)
len(dates)


# In[9]:


messages = messages[:len(dates)]


# In[10]:


df = pd.DataFrame({'user_message': messages, 'message_date': dates})


# In[11]:


df


# In[12]:


# convert message_date type
df['message_date'] = pd.to_datetime(df['message_date'], format= '%Y-%m-%d, %I:%M:%S %p')


# In[13]:


df.rename(columns={'message_date': 'date'}, inplace=True)


# In[14]:


df


# In[15]:


users = []
messages = []
for message in df['user_message']:
    entry = re.split('([\w\W]+?):\s', message)
    if entry[1:]:  # user name
        users.append(entry[1])
        messages.append(" ".join(entry[2:]))
    else:
        users.append('group_notification')
        messages.append(entry[0])


# In[16]:


df['user'] = users
df['message'] = messages
df.drop(columns=['user_message'], inplace=True)


# In[17]:


df


# In[18]:


df['only_date'] = df['date'].dt.date
df['year'] = df['date'].dt.year
df['month_num'] = df['date'].dt.month
df['month'] = df['date'].dt.month_name()
df['day'] = df['date'].dt.day
df['day_name'] = df['date'].dt.day_name()
df['hour'] = df['date'].dt.hour
df['minute'] = df['date'].dt.minute


# In[19]:


period = []
for hour in df[['day_name', 'hour']]['hour']:
    if hour == 23:
        period.append(str(hour) + "-" + str('00'))
    elif hour == 0:
        period.append(str('00') + "-" + str(hour + 1))
    else:
        period.append(str(hour) + "-" + str(hour + 1))

df['period'] = period


# In[20]:


df


# In[21]:


df = df.drop(df[df['user'] == 'group_notification'].index)


# In[22]:


df


# In[23]:


#total number of messages

num_messages = df.shape[0]
num_messages


# In[24]:


#total number of words
words = []
for message in df['message']:
    words.extend(message.split())

len(words)


# In[33]:


# Most_busy_users(df), Messages per user
most_busy_users = df['user'].value_counts().reset_index()
most_busy_users


# In[45]:


# Top 10 Most_busy_users(df), 
most_busy_users = df['user'].value_counts().head(10)
most_busy_users


# In[46]:


name = most_busy_users.index
count = most_busy_users.values


# In[192]:


plt.figure(figsize=(10, 6))
plt.bar(name, count, color = 'crimson')
plt.xticks(rotation = 'vertical')
plt.show


# In[62]:


# Percentage of contribution in the group chat
user_percentage = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(columns={'index': 'name', 'user': 'percent'})
user_percentage = user_percentage.head(15)
user_percentage


# In[83]:


fig, ax = plt.subplots(figsize=(20, 10))
colors = plt.cm.Paired.colors
wedges, texts, autotexts = ax.pie(user_percentage['percent'], labels=user_percentage['name'], autopct='%1.1f%%', startangle=90, colors=colors)

legend_labels = [f'{name} ({percent}%)' for name, percent in zip(user_percentage['name'], user_percentage['percent'])]
ax.legend(wedges, legend_labels, title='User Contribution', loc='best', bbox_to_anchor=(1, 0, 0.5, 1))

ax.set_title('Percentage of User Contribution')


# In[125]:


words = []

for message in df['message']:
    for word in message.lower().split():
        words.append(word)

most_common_df = pd.DataFrame(Counter(words).most_common(20), columns=['word', 'count'])
most_common_df


# In[126]:


# Top 20 Most commonly Used words

plt.figure(figsize=(10, 8))
plt.barh(most_common_df['word'], most_common_df['count'], color='seagreen')
plt.xlabel('Count')
plt.ylabel('Word')
plt.title('Top 20 Most Commonly Used Words')
plt.show()


# In[113]:


# Wordcloud

wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(dict(zip(most_common_df['word'], most_common_df['count'])))

plt.figure(figsize=(10, 10))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Word Cloud of Most Common Words')
plt.show()


# In[117]:


#monthly timeline
timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
timeline


# In[127]:


time = []
for i in range(timeline.shape[0]):
    time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

timeline['time'] = time


# In[128]:


timeline


# In[164]:


plt.figure(figsize=(12, 6))
plt.plot(timeline['time'], timeline['message'], marker = '+')
plt.xlabel('Month-Year')
plt.ylabel('Message Count')
plt.title('Monthly Timeline')
plt.grid(True, linestyle='--', alpha=0.3)
plt.legend()
plt.xticks(rotation = 'vertical')
plt.show()


# In[149]:


#daily timeline
daily_timeline = df.groupby('only_date').count()['message'].reset_index()
daily_timeline.drop(index=daily_timeline.index[0], inplace=True)
daily_timeline


# In[156]:


plt.figure(figsize=(18, 10))
plt.plot(daily_timeline['only_date'], daily_timeline['message'], marker = '+')
plt.xlabel('Date')
plt.ylabel('Message Count')
plt.title('Message Count Over Time')
plt.grid(True, linestyle='--', alpha=0.3)
plt.legend()
plt.xticks(rotation = 'vertical')
plt.show()


# In[147]:


#week activity map
weekly_activity = df['day_name'].value_counts()
weekly_activity


# In[191]:


days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weekly_activity = weekly_activity.reindex(days_order)
heatmap_data = weekly_activity.values.reshape(1, -1)
plt.figure(figsize=(10, 6))
sns.heatmap(heatmap_data, annot=True, fmt='d', cmap='coolwarm', xticklabels=days_order, yticklabels=False, cbar=True)
plt.xlabel('Day of the Week')
plt.title('Weekly Activity Heatmap')
plt.show()


# In[165]:


#monthly activity map
monthly_activity = df['month'].value_counts()
monthly_activity


# In[190]:


months_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
monthly_activity = monthly_activity.reindex(months_order)

heatmap_data = monthly_activity.values.reshape(1, -1)
plt.figure(figsize=(10, 6))
sns.set(style="whitegrid", palette="viridis")
sns.heatmap(heatmap_data, annot=True, fmt='d', cmap='coolwarm', xticklabels=months_order, yticklabels=False, cbar=True)
plt.xlabel('Month')
plt.title('Monthly Activity Heatmap')
plt.show()


# In[166]:


#user_heatmap
user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
user_heatmap


# In[175]:


plt.figure(figsize = (16,8))
sns.heatmap(user_heatmap, annot=True, fmt='.2f', cmap='coolwarm', linewidths=.5, cbar_kws={'label': 'Message Legend'})
plt.xlabel('Period of the Day')
plt.ylabel('Day_Name')
plt.title('User Activity Heatmap')

