// WRITTEN BY `python3 goals.py --write-js` FROM goals.json -- do not edit.
// The agency's goals and colour thresholds for the board page: see goals.py.
window.GOALS = {
 "thresholds": {
  "call_volume": {
   "green": 50,
   "yellow": 40
  },
  "avg_talk_min": {
   "green": 7,
   "yellow": 3
  },
  "contact_rate_pct": {
   "green": 13,
   "yellow": 10
  },
  "households_quoted": {
   "green": 5,
   "yellow": 2
  },
  "premium_quoted_per_hh": {
   "green": 900,
   "yellow": 501
  },
  "premium_sold_per_policy": {
   "green": 900,
   "yellow": 501
  },
  "policy_count": {
   "green": 4,
   "yellow": 1
  },
  "task_completion_pct": {
   "green": 100,
   "yellow": 90
  },
  "speed_to_dial_min": {
   "green": 2,
   "yellow": 5,
   "lower_better": true
  },
  "utilization_pct": {
   "green": 85,
   "yellow": 80
  },
  "roleplay_score": {
   "green": 80,
   "yellow": 0
  },
  "closing_ratio_pct": {
   "green": 25,
   "yellow": 15
  }
 },
 "team_scaled_metrics": [
  "call_volume",
  "households_quoted"
 ],
 "life_weekly_goal": 1,
 "reply_goal_minutes": {
  "green": 15,
  "red": 60
 },
 "week_premium_goal": 20000,
 "coach_bar_ranges": {
  "Avg Call Score": [
   38,
   251
  ],
  "Avg Sentiment": [
   11,
   43
  ],
  "Role Play": [
   58,
   87
  ]
 }
};
