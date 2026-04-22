import Foundation

final class OverviewStorage {
    private let key = "day_overview.latest"

    func load() -> StoredOverview? {
        guard let data = UserDefaults.standard.data(forKey: key) else { return nil }
        return try? JSONDecoder().decode(StoredOverview.self, from: data)
    }

    func save(_ overview: StoredOverview) {
        if let data = try? JSONEncoder().encode(overview) {
            UserDefaults.standard.set(data, forKey: key)
        }
    }
}

struct StoredOverview: Codable {
    let date: String
    let script: String
    let generatedAt: String
}
