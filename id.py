url = "https://www.espncricinfo.com/series/indian-premier-league-2023-1345038/royal-challengers-bangalore-vs-rajasthan-royals-32nd-match-1359506/full-scorecard"

# split the url on "/"
url_parts = url.split("/")

# extract series ID and match ID from the url
full_series_id = url_parts[4]
full_match_id = url_parts[5]

# extract lastID for both IDs
series_id = full_series_id.split('-')[-1]
match_id = full_match_id.split('-')[-1]
