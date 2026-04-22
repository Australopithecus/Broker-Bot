import Foundation

final class WorkoutScheduler {
    private let durationMinutes = 30

    func recommendation(for events: [CalendarEvent], day: Date) -> WorkoutRecommendation {
        let calendar = Calendar.current
        let isRunningDay = calendar.ordinality(of: .day, in: .year, for: day).map { $0 % 2 == 0 } ?? true
        let title = isRunningDay ? "Run" : "Weight training"

        let windows: [(start: (Int, Int), end: (Int, Int))] = [
            ((5, 30), (9, 0)),
            ((11, 30), (14, 0)),
            ((17, 0), (20, 0))
        ]

        for window in windows {
            guard let windowStart = calendar.date(bySettingHour: window.start.0, minute: window.start.1, second: 0, of: day),
                  let windowEnd = calendar.date(bySettingHour: window.end.0, minute: window.end.1, second: 0, of: day) else {
                continue
            }

            if let slot = firstAvailableSlot(events: events, windowStart: windowStart, windowEnd: windowEnd) {
                return WorkoutRecommendation(title: title, start: slot.start, end: slot.end, fallbackNote: nil)
            }
        }

        return WorkoutRecommendation(
            title: title,
            start: nil,
            end: nil,
            fallbackNote: "No 30-minute window found. Consider a short walk today."
        )
    }

    private func firstAvailableSlot(events: [CalendarEvent], windowStart: Date, windowEnd: Date) -> (start: Date, end: Date)? {
        let duration = TimeInterval(durationMinutes * 60)
        let overlapping = events
            .filter { $0.end > windowStart && $0.start < windowEnd }
            .sorted { $0.start < $1.start }

        var cursor = windowStart
        for event in overlapping {
            if event.start.timeIntervalSince(cursor) >= duration {
                return (cursor, cursor.addingTimeInterval(duration))
            }
            if event.end > cursor {
                cursor = event.end
            }
        }

        if windowEnd.timeIntervalSince(cursor) >= duration {
            return (cursor, cursor.addingTimeInterval(duration))
        }

        return nil
    }
}
