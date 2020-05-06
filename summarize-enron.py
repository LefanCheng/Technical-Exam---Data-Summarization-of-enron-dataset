# Import Modules
import sys
import numpy as np
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

class summarize_enron():
    
    def __init__(self):
        
        # Import csv file with column names specified
        self.column_names = ['time', 'message_id', 'sender', 'recipient', 'topic', 'mode']
        # self.df = pd.read_csv('enron-event-history-all.csv', names=self.column_names)
        self.df = pd.read_csv(sys.argv[1], names=self.column_names)
        
        # Data Cleaning and Preprocessing: 
        # Detected 32 and 38 missing values(NaN) in Senders and recipient.
        # Fill NaN with 'missing' which is easier to handle them if needed.
        # Assume 'blank' is a legit person name instead of missing value.
        self.df['recipient'].fillna('missing', inplace=True)
        
        # Convert Unix time in milliseconds into readable date time 
        self.df['time'] = pd.to_datetime(self.df['time'], unit='ms')
        
        # Discovered 2244 announcements and 3314 notes in sender
        # which are in the top 10 prolific senders. Assuming they were sent by system 
        # not person, same as 'schedule'(852), 'outlook'(1160), 'arsystem'(299), 
        # remove these senders as they might be much less informative. 
        self.df = self.df[~self.df.sender.isin(['announcements', 'notes', 'schedule', 'outlook', 'arsystem'])]
        # set time column as index
        self.df.set_index('time', inplace=True)
        
    def senders_count(self):
        # Use defaultdict to create a dictionary that has name as key and count as value. 
        # If a key doesn't exist in defaultdict(int), it'll return 0
        counter = defaultdict(int)
        for name in self.df['sender']:
            counter[name] += 1
        
        return counter
    
    def recipient_count(self):
        # Same as senders_count, but split mutiple recipients.
        counter = defaultdict(int)
        for names in self.df['recipient']:
            if '|' in names:
                for name in names.split('|'):
                    counter[name] += 1
            else:
                counter[names] += 1
        
        return counter
    
    def q1_ouput_csv(self):
        # Concatenate senders and recipients count into one by unique names 
        dic = {}
        senders = self.senders_count()
        recipients = self.recipient_count()
        unique_names = set(list(senders) + list(recipients))
        for name in unique_names:
            dic[name] = {'senders': senders[name], 'recipients': recipients[name]}
        # Contruct the dataframe using the dict    
        df = pd.DataFrame.from_dict(dic, orient='index').sort_values('senders', ascending=False).reset_index()
        # Reset column name
        df.rename(columns = {'index':'person'}, inplace = True)  
        # Refine the top 5 senders
        self.top_senders = list(df.person[:5])

        return df
    
    def q2_prolific_senders(self):
        sns.set(style="whitegrid")
        plt.figure(figsize=(12,8))
        for person in self.top_senders:
            sns.lineplot(data=self.df['sender'][self.df['sender'] == person].resample('M').count(), label=person, palette = 'pastel')
        plt.xticks(rotation=45)
        plt.legend(loc='upper left')
        plt.title("Most Prolific Senders - The Number of Emails Sent Over Time")
        plt.xlabel("Month")
        plt.ylabel("Number of Emails")

        return plt

    def q3_num_uniq_ppl_contacted(self):
        sns.set(style="whitegrid")
        plt.figure(figsize=(12,8))
        # plot based on the number of unique senders for each top prolific senders as recipient in each month
        for person in self.top_senders:
            sns.lineplot(data=self.df[self.df['recipient'].str.contains(person)].resample('M').nunique()['sender'], label=person)
        plt.xticks(rotation=45)
        plt.legend(loc='upper left')
        plt.title("Relative Number of Unique People who Contacted the Top 5 Prolific Senders")
        plt.xlabel("Month")
        plt.ylabel("Number of Unique Contacts")
        
        return plt

if __name__=='__main__':
    
    summarize_enron = summarize_enron()
    
    # Question 1: 
    summarize_enron.q1_ouput_csv().to_csv('question_1_output.csv')
    
    # Question 2:
    summarize_enron.q2_prolific_senders().savefig('question_2_output.png')
    
    # Question 3:
    summarize_enron.q3_num_uniq_ppl_contacted().savefig('question_3_output.png')