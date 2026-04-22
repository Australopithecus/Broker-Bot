import SwiftUI

enum AppConfig {
    static let backendBaseURL = "http://127.0.0.1:8001"
    static let defaultLatitude = 35.9959
    static let defaultLongitude = -78.9021
}

enum AppTheme {
    static let accent = Color(red: 0.12, green: 0.46, blue: 0.95)
    static let accentSoft = Color(red: 0.39, green: 0.67, blue: 0.98)
    static let textPrimary = Color(red: 0.12, green: 0.14, blue: 0.18)
    static let textSecondary = Color(red: 0.42, green: 0.47, blue: 0.55)
    static let card = Color.white.opacity(0.94)
    static let chip = Color(red: 0.92, green: 0.95, blue: 0.99)
    static let border = Color.white.opacity(0.75)
    static let shadow = Color.black.opacity(0.08)
    static let badgeIndigo = Color(red: 0.33, green: 0.39, blue: 0.89)
    static let badgeTeal = Color(red: 0.0, green: 0.58, blue: 0.63)
    static let evidencePractice = Color(red: 0.11, green: 0.60, blue: 0.35)
    static let evidenceNeutral = Color(red: 0.45, green: 0.48, blue: 0.56)
    static let evidenceHarm = Color(red: 0.82, green: 0.24, blue: 0.24)

    static var pageGradient: LinearGradient {
        LinearGradient(
            colors: [
                Color(red: 0.98, green: 0.99, blue: 1.0),
                Color(red: 0.93, green: 0.96, blue: 1.0)
            ],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }
}
