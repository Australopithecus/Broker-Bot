import Foundation

@MainActor
final class OverviewViewModel: ObservableObject {
    @Published var searchText: String = ""
    @Published var selectedTopic: TrialTopic? = nil
    @Published private(set) var favoriteTrialIDs: Set<String>

    let trials: [ICUTrial]
    private let defaults: UserDefaults
    private static let favoriteIDsStorageKey = "icuClinicalTrials.favoriteTrialIDs"

    init(
        trials: [ICUTrial] = ICUTrialLibrary.allTrials,
        defaults: UserDefaults = .standard
    ) {
        self.defaults = defaults
        self.favoriteTrialIDs = Set(
            defaults.stringArray(forKey: Self.favoriteIDsStorageKey) ?? []
        )
        self.trials = trials.sorted { lhs, rhs in
            if lhs.year == rhs.year {
                return lhs.shortName < rhs.shortName
            }
            return lhs.year > rhs.year
        }
    }

    var topics: [TrialTopic] {
        TrialTopic.allCases
    }

    var trialOfDay: ICUTrial {
        guard !trials.isEmpty else {
            fatalError("ICU trial catalog is empty.")
        }

        let dayIndex = (Calendar.current.ordinality(of: .day, in: .year, for: Date()) ?? 1) - 1
        return trials[dayIndex % trials.count]
    }

    var filteredTrials: [ICUTrial] {
        trials.filter { trial in
            matchesSelectedTopic(trial) && matchesSearch(trial)
        }
    }

    var favoriteTrials: [ICUTrial] {
        filteredTrials.filter { isFavorite($0) }
    }

    var landmarkTrials: [ICUTrial] {
        filteredTrials.filter { $0.era == .landmark && !isFavorite($0) }
    }

    var recentTrials: [ICUTrial] {
        filteredTrials.filter { $0.era == .recent && !isFavorite($0) }
    }

    func selectTopic(_ topic: TrialTopic?) {
        selectedTopic = topic
    }

    func isFavorite(_ trial: ICUTrial) -> Bool {
        favoriteTrialIDs.contains(trial.id)
    }

    func toggleFavorite(_ trial: ICUTrial) {
        if favoriteTrialIDs.contains(trial.id) {
            favoriteTrialIDs.remove(trial.id)
        } else {
            favoriteTrialIDs.insert(trial.id)
        }
        persistFavorites()
    }

    private func matchesSelectedTopic(_ trial: ICUTrial) -> Bool {
        guard let selectedTopic else { return true }
        return trial.topic == selectedTopic
    }

    private func matchesSearch(_ trial: ICUTrial) -> Bool {
        let query = searchText
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased()

        guard !query.isEmpty else { return true }

        return trial.searchIndex.contains { item in
            item.lowercased().contains(query)
        }
    }

    private func persistFavorites() {
        defaults.set(favoriteTrialIDs.sorted(), forKey: Self.favoriteIDsStorageKey)
    }
}
