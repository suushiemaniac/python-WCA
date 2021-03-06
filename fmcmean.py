#!/usr/bin/python

# This code is based on Stefan Pochmann's FMC-Mean script
# see here for original code: https://www.speedsolving.com/forum/threads/odd-wca-stats-stats-request-thread.26121/page-108#post-925988
# I used many parts from it and only modified it where necessary, so credits to him

import pymysql
import sys

N = 5              # average/mean-of-N
T = 1               # throw out T best/worst

def average(personId):
    # average-of-n, throwing out t best/worst attempts
    # returns triple (avg, sorted, values) for easy sorting
    res = results[personId]
    if len(res) == N - 1:
        res.append(-2)
    best = None
    for i in range(len(res) - N + 1):
        values = res[i:i+N]
        sorted_ = sorted(values, key=lambda v: (v<0, v))
        counting = sorted_[T:N-T]
        if min(counting) > 0:
            avg = float(sum(counting)) / len(counting)
            this = (avg, sorted_, values)
            if not best or this < best:
                best = this
    return best

# Print table
def table(rank):
    sys.stdout=open("fmcmean.txt","w")
    print('[spoiler=Average of', N, ']')
    print('[table]')
    print('[tr][td][td]Name[/td][td]Mean[/td][td]Solves[/td][/tr]')
    # If more than 100 people have an average, just take top 100
    for k in range(0, len(rank)):
        i = k+1
        for l in range(0,k):
            if round(rank[k][1][0][0],2) == round(rank[k-l][1][0][0],2):
                i = k-l+1
        print('[tr][td]', i, '[/td][td]', rank[k][0],'[/td][td]', round(rank[k][1][0][0],2),'[/td][td]', rank[k][1][0][2], '[/td][/tr]')
        if k > 100:
            break
    print('[/table]')
    print('[/spoiler]')
    sys.stdout.close()


# Just setup and connection to my DB
conn = pymysql.connect(host='127.0.0.1',
                       unix_socket='/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock',
                       user='root',
                       passwd=None,
                       db='wca')

cur = conn.cursor(pymysql.cursors.DictCursor)
cur.execute("SELECT eventId, personName, value1, value2, value3 FROM Results WHERE eventId = '333fm'")

names, results, list = {}, {}, {}

rows = cur.fetchall()

# Get everyone's results
for row in rows:
    for i in ('value1', 'value2', 'value3'):
        if row[i] > 0 or row[i] == -1:
            results.setdefault(row['personName'], []).append(row[i])

# Put everyones average in a dictionary
for p in results.keys():
    a = average(p)
    if a is not None:
        list.setdefault(p, []).append(a)

# Compute everybody's best average
ranking = [(k, list[k]) for k in sorted(list, key=lambda k:list[k])]

# Change -1, -2 to DNF, DNS if necessary
for key in ranking:
    for k in range(0,len(key[1][0][2])):
        if key[1][0][2][k] == -1:
            key[1][0][2][k] = 'DNF'
        if key[1][0][2][k] == -2:
            key[1][0][2][k] = 'DNS'

# Build table with results
table(ranking)

cur.close()
conn.close()



