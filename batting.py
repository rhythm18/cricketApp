import main
import id
battingData = main.extract_batting_data(series_id = id.series_id, match_id = id.match_id)
#print(battingData)
print("\n\n")
bowlingData = main.extract_bowling_data(series_id = id.series_id, match_id = id.match_id)
#print(bowlingData)

battingPoints = main.calculate_batting_points(battingData)
battingPoints.to_excel("batting_data.xlsx", index=False)

bowlingPoints = main.calculate_bowling_points(bowlingData)
bowlingPoints.to_excel("bowling_data.xlsx", index=False)