import CoreLocation
import Foundation

final class WeatherService {
    func fetchWeather(coordinate: CLLocationCoordinate2D?) async throws -> WeatherSummary {
        let lat = coordinate?.latitude ?? AppConfig.defaultLatitude
        let lon = coordinate?.longitude ?? AppConfig.defaultLongitude

        let urlString = "https://api.open-meteo.com/v1/forecast?latitude=\(lat)&longitude=\(lon)&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto"
        guard let url = URL(string: urlString) else {
            throw URLError(.badURL)
        }

        let (data, response) = try await URLSession.shared.data(from: url)
        if let http = response as? HTTPURLResponse, http.statusCode >= 400 {
            throw URLError(.badServerResponse)
        }

        let decoded = try JSONDecoder().decode(OpenMeteoResponse.self, from: data)
        guard let high = decoded.daily.temperature_2m_max.first,
              let low = decoded.daily.temperature_2m_min.first else {
            throw URLError(.cannotParseResponse)
        }

        let precip = decoded.daily.precipitation_probability_max?.first ?? 0
        let narrative = "High \(Int(high))°, low \(Int(low))°, precipitation chance \(Int(precip))%."

        return WeatherSummary(high: high, low: low, precipitationChance: precip, narrative: narrative)
    }
}

private struct OpenMeteoResponse: Decodable {
    struct Daily: Decodable {
        let temperature_2m_max: [Double]
        let temperature_2m_min: [Double]
        let precipitation_probability_max: [Double]?
    }

    let daily: Daily
}
