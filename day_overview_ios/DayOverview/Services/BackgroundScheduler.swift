import BackgroundTasks
import Foundation

final class BackgroundScheduler {
    static let taskID = "com.dayoverview.refresh"

    static func register() {
        BGTaskScheduler.shared.register(forTaskWithIdentifier: taskID, using: nil) { task in
            scheduleNextRefresh()
            task.setTaskCompleted(success: true)
        }
    }

    static func scheduleNextRefresh() {
        let calendar = Calendar.current
        var components = calendar.dateComponents([.year, .month, .day], from: Date())
        components.hour = 5
        components.minute = 0

        guard let todayAtFive = calendar.date(from: components) else { return }
        let nextRun = Date() < todayAtFive ? todayAtFive : calendar.date(byAdding: .day, value: 1, to: todayAtFive)

        let request = BGAppRefreshTaskRequest(identifier: taskID)
        request.earliestBeginDate = nextRun
        try? BGTaskScheduler.shared.submit(request)
    }
}
