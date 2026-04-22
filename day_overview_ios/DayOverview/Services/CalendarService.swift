import EventKit
import Foundation

final class CalendarService {
    private let store = EKEventStore()

    func requestAccess() async -> Bool {
        await withCheckedContinuation { continuation in
            store.requestAccess(to: .event) { granted, _ in
                continuation.resume(returning: granted)
            }
        }
    }

    func events(for day: Date) -> [CalendarEvent] {
        let calendar = Calendar.current
        let start = calendar.startOfDay(for: day)
        guard let end = calendar.date(byAdding: .day, value: 1, to: start) else {
            return []
        }

        let predicate = store.predicateForEvents(withStart: start, end: end, calendars: nil)
        let events = store.events(matching: predicate)

        return events.map {
            CalendarEvent(
                title: $0.title ?? "(No Title)",
                start: $0.startDate,
                end: $0.endDate,
                location: $0.location
            )
        }
    }
}
