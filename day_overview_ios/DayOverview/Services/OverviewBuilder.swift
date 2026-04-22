import Foundation

final class OverviewBuilder {
    func build(
        daily: DailyContent,
        events: [CalendarEvent],
        weather: WeatherSummary,
        workout: WorkoutRecommendation,
        day: Date
    ) -> String {
        let dateFormatter = DateFormatter()
        dateFormatter.dateStyle = .full

        let timeFormatter = DateFormatter()
        timeFormatter.timeStyle = .short

        var lines: [String] = []
        lines.append("Good morning. Here is your Day Overview for \(dateFormatter.string(from: day)).")

        if events.isEmpty {
            lines.append("You have no scheduled events today.")
        } else {
            lines.append("Here is your calendar:")
            for event in events.sorted(by: { $0.start < $1.start }) {
                let start = timeFormatter.string(from: event.start)
                let title = event.title
                if let location = event.location, !location.isEmpty {
                    lines.append("At \(start), \(title) in \(location).")
                } else {
                    lines.append("At \(start), \(title).")
                }
            }
        }

        lines.append("Weather: \(weather.narrative)")

        if daily.news.isEmpty {
            lines.append("No news items available.")
        } else {
            lines.append("Top news:")
            for item in daily.news.prefix(5) {
                if item.summary.isEmpty {
                    lines.append("\(item.headline).")
                } else {
                    lines.append("\(item.headline). \(item.summary)")
                }
            }
        }

        if let start = workout.start, let end = workout.end {
            lines.append("Workout suggestion: \(workout.title) from \(timeFormatter.string(from: start)) to \(timeFormatter.string(from: end)).")
        } else if let note = workout.fallbackNote {
            lines.append("Workout suggestion: \(workout.title). \(note)")
        } else {
            lines.append("Workout suggestion: \(workout.title).")
        }

        lines.append("ICU trial summary: \(daily.icuTrialSummary)")
        lines.append("Historical fact: \(daily.historicalFact)")

        return lines.joined(separator: " ")
    }
}
