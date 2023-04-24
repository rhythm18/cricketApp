import batting

highest_wickets = batting.bowlingData.sort_values(by='Wickets', ascending=False).iloc[0]
print(highest_wickets)
w = highest_wickets.iloc[4]
print(w)