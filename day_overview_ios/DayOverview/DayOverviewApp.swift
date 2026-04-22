import SwiftUI

@main
struct DayOverviewApp: App {
    @StateObject private var model = OverviewViewModel()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(model)
                .tint(AppTheme.accent)
                .preferredColorScheme(.light)
        }
    }
}
