import Foundation

final class OverviewService {
    func fetchDailyContent() async throws -> DailyContent {
        guard let url = URL(string: "\(AppConfig.backendBaseURL)/daily-content") else {
            throw URLError(.badURL)
        }

        let (data, response) = try await URLSession.shared.data(from: url)
        if let http = response as? HTTPURLResponse, http.statusCode >= 400 {
            throw URLError(.badServerResponse)
        }

        return try JSONDecoder().decode(DailyContent.self, from: data)
    }
}
