import SwiftUI

struct ContentView: View {
    @EnvironmentObject var model: OverviewViewModel

    var body: some View {
        NavigationStack {
            ZStack {
                AppTheme.pageGradient
                    .ignoresSafeArea()

                List {
                    Section {
                        styledRow {
                            NavigationLink(value: model.trialOfDay) {
                                TrialOfDayCard(trial: model.trialOfDay)
                            }
                            .buttonStyle(.plain)
                        }
                    } header: {
                        sectionHeader("Trial of the Day")
                    } footer: {
                        Text("Updates each day for one quick, focused review.")
                            .font(.caption)
                            .foregroundStyle(AppTheme.textSecondary)
                    }

                    Section {
                        styledRow {
                            TopicFilterRow(
                                topics: model.topics,
                                selectedTopic: model.selectedTopic,
                                onSelect: model.selectTopic
                            )
                        }
                    } header: {
                        sectionHeader("Browse by Topic")
                    }

                    if !model.favoriteTrials.isEmpty {
                        Section {
                            ForEach(model.favoriteTrials) { trial in
                                styledRow {
                                    trialNavigationRow(for: trial)
                                }
                            }
                        } header: {
                            sectionHeader("Favorites")
                        }
                    }

                    if model.filteredTrials.isEmpty {
                        Section {
                            styledRow {
                                EmptyStateCard(
                                    title: "No matching trials",
                                    subtitle: "Try a broader term like ARDS, Sepsis, or Fluids."
                                )
                            }
                        }
                    }

                    if !model.landmarkTrials.isEmpty {
                        Section {
                            ForEach(model.landmarkTrials) { trial in
                                styledRow {
                                    trialNavigationRow(for: trial)
                                }
                            }
                        } header: {
                            sectionHeader("Landmark Trials")
                        }
                    }

                    if !model.recentTrials.isEmpty {
                        Section {
                            ForEach(model.recentTrials) { trial in
                                styledRow {
                                    trialNavigationRow(for: trial)
                                }
                            }
                        } header: {
                            sectionHeader("Recent Trials")
                        }
                    }
                }
                .listStyle(.insetGrouped)
                .scrollContentBackground(.hidden)
            }
            .navigationTitle("ICU Clinical Trials")
            .searchable(text: $model.searchText, prompt: "Search trial name or topic")
            .navigationDestination(for: ICUTrial.self) { trial in
                TrialDetailView(trial: trial)
            }
        }
    }

    private func sectionHeader(_ title: String) -> some View {
        Text(title)
            .font(.system(size: 14, weight: .semibold, design: .rounded))
            .foregroundStyle(AppTheme.textSecondary)
            .textCase(nil)
    }

    @ViewBuilder
    private func styledRow<Content: View>(@ViewBuilder _ content: () -> Content) -> some View {
        content()
            .listRowInsets(EdgeInsets(top: 6, leading: 16, bottom: 6, trailing: 16))
            .listRowBackground(Color.clear)
            .listRowSeparator(.hidden)
    }

    @ViewBuilder
    private func trialNavigationRow(for trial: ICUTrial) -> some View {
        NavigationLink(value: trial) {
            TrialRow(
                trial: trial,
                isFavorite: model.isFavorite(trial)
            )
        }
        .buttonStyle(.plain)
        .swipeActions(edge: .trailing, allowsFullSwipe: false) {
            Button {
                model.toggleFavorite(trial)
            } label: {
                Label(
                    model.isFavorite(trial) ? "Unfavorite" : "Favorite",
                    systemImage: model.isFavorite(trial) ? "star.slash" : "star"
                )
            }
            .tint(model.isFavorite(trial) ? .gray : .yellow)
        }
    }
}

private struct EmptyStateCard: View {
    let title: String
    let subtitle: String

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.system(.headline, design: .rounded))
                .foregroundStyle(AppTheme.textPrimary)
            Text(subtitle)
                .font(.subheadline)
                .foregroundStyle(AppTheme.textSecondary)
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .fill(AppTheme.card)
                .overlay(
                    RoundedRectangle(cornerRadius: 16, style: .continuous)
                        .stroke(AppTheme.border, lineWidth: 1)
                )
        )
        .shadow(color: AppTheme.shadow, radius: 12, x: 0, y: 6)
    }
}

private struct TrialOfDayCard: View {
    let trial: ICUTrial

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .center) {
                Label("Today", systemImage: "calendar.badge.clock")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(AppTheme.accent)
                Spacer()
                EvidenceBadge(strength: trial.evidenceStrength)
                TrialBadge(text: trial.topic.rawValue, tint: AppTheme.badgeTeal)
            }

            Text(trial.shortName)
                .font(.system(.title3, design: .rounded).weight(.semibold))
                .foregroundStyle(AppTheme.textPrimary)

            Text(trial.fullTitle)
                .font(.subheadline)
                .foregroundStyle(AppTheme.textSecondary)
                .lineLimit(3)

            Text(trial.bottomLine)
                .font(.body)
                .foregroundStyle(AppTheme.textPrimary)
                .lineLimit(4)
        }
        .padding(18)
        .background(
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .fill(
                    LinearGradient(
                        colors: [
                            Color.white.opacity(0.98),
                            Color(red: 0.89, green: 0.94, blue: 1.0)
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 20, style: .continuous)
                        .stroke(Color.white.opacity(0.9), lineWidth: 1)
                )
        )
        .shadow(color: AppTheme.shadow, radius: 14, x: 0, y: 8)
    }
}

private struct TopicFilterRow: View {
    let topics: [TrialTopic]
    let selectedTopic: TrialTopic?
    let onSelect: (TrialTopic?) -> Void

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                TopicChip(
                    title: "All",
                    isSelected: selectedTopic == nil,
                    action: { onSelect(nil) }
                )

                ForEach(topics) { topic in
                    TopicChip(
                        title: topic.rawValue,
                        isSelected: selectedTopic == topic,
                        action: { onSelect(topic) }
                    )
                }
            }
            .padding(.vertical, 4)
        }
    }
}

private struct TopicChip: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.caption.weight(.semibold))
                .padding(.vertical, 9)
                .padding(.horizontal, 14)
                .background(isSelected ? AppTheme.accent : AppTheme.chip)
                .foregroundStyle(isSelected ? Color.white : AppTheme.textPrimary)
                .clipShape(Capsule())
        }
        .buttonStyle(.plain)
    }
}

private struct TrialRow: View {
    let trial: ICUTrial
    let isFavorite: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .firstTextBaseline) {
                Text(trial.shortName)
                    .font(.system(.headline, design: .rounded))
                    .foregroundStyle(AppTheme.textPrimary)
                Spacer()
                if isFavorite {
                    Image(systemName: "star.fill")
                        .font(.footnote)
                        .foregroundStyle(.yellow)
                        .accessibilityLabel("Favorite")
                }
                Text(String(trial.year))
                    .font(.subheadline)
                    .foregroundStyle(AppTheme.textSecondary)
            }

            HStack(spacing: 6) {
                TrialBadge(text: trial.era.rawValue, tint: AppTheme.badgeIndigo)
                TrialBadge(text: trial.topic.rawValue, tint: AppTheme.badgeTeal)
                EvidenceBadge(strength: trial.evidenceStrength)
            }

            Text(trial.fullTitle)
                .font(.subheadline)
                .foregroundStyle(AppTheme.textSecondary)
                .lineLimit(2)

            Text(trial.bottomLine)
                .font(.footnote)
                .foregroundStyle(AppTheme.textPrimary)
                .lineLimit(3)
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .fill(AppTheme.card)
                .overlay(
                    RoundedRectangle(cornerRadius: 16, style: .continuous)
                        .stroke(AppTheme.border, lineWidth: 1)
                )
        )
        .shadow(color: AppTheme.shadow, radius: 10, x: 0, y: 6)
    }
}

private struct TrialBadge: View {
    let text: String
    let tint: Color

    var body: some View {
        Text(text)
            .font(.caption2.weight(.semibold))
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(tint.opacity(0.14))
            .foregroundStyle(tint)
            .clipShape(Capsule())
    }
}

private struct EvidenceBadge: View {
    let strength: EvidenceStrength

    private var tint: Color {
        switch strength {
        case .practiceChanging:
            return AppTheme.evidencePractice
        case .neutral:
            return AppTheme.evidenceNeutral
        case .harmSignal:
            return AppTheme.evidenceHarm
        }
    }

    private var icon: String {
        switch strength {
        case .practiceChanging:
            return "arrow.up.right.circle.fill"
        case .neutral:
            return "minus.circle.fill"
        case .harmSignal:
            return "exclamationmark.triangle.fill"
        }
    }

    var body: some View {
        Label(strength.rawValue, systemImage: icon)
            .font(.caption2.weight(.semibold))
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(tint.opacity(0.14))
            .foregroundStyle(tint)
            .clipShape(Capsule())
    }
}

private struct TrialDetailView: View {
    @EnvironmentObject var model: OverviewViewModel
    let trial: ICUTrial

    var body: some View {
        ZStack {
            AppTheme.pageGradient
                .ignoresSafeArea()

            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    headerCard

                    TrialDetailSection(title: "Population", text: trial.patientPopulation)
                    TrialDetailSection(title: "Intervention", text: trial.intervention)
                    TrialDetailSection(title: "Comparator", text: trial.comparator)
                    TrialDetailSection(title: "Primary Outcome", text: trial.primaryOutcome)
                    TrialDetailSection(title: "Why It Matters", text: trial.bottomLine)
                    TrialDetailSection(title: "Clinical Takeaway", text: trial.practiceTakeaway)
                    TrialDetailSection(
                        title: "Evidence Strength",
                        text: "\(trial.evidenceStrength.rawValue): \(trial.evidenceStrength.interpretation)"
                    )

                    TrialAppraisalCard(appraisal: trial.appraisal)

                    citationCard
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
            }
        }
        .navigationTitle(trial.shortName)
        .navigationBarTitleDisplayMode(.inline)
    }

    private var headerCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .top, spacing: 12) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(trial.fullTitle)
                        .font(.system(.title3, design: .rounded).weight(.semibold))
                        .foregroundStyle(AppTheme.textPrimary)

                    HStack(spacing: 8) {
                        TrialBadge(text: trial.era.rawValue, tint: AppTheme.badgeIndigo)
                        TrialBadge(text: trial.topic.rawValue, tint: AppTheme.badgeTeal)
                        EvidenceBadge(strength: trial.evidenceStrength)
                        Text(String(trial.year))
                            .font(.subheadline)
                            .foregroundStyle(AppTheme.textSecondary)
                    }
                }

                Spacer(minLength: 0)

                Button {
                    model.toggleFavorite(trial)
                } label: {
                    Image(systemName: model.isFavorite(trial) ? "star.fill" : "star")
                        .font(.title3)
                        .foregroundStyle(model.isFavorite(trial) ? .yellow : AppTheme.textSecondary)
                }
                .buttonStyle(.plain)
                .accessibilityLabel(
                    model.isFavorite(trial)
                    ? "Remove from favorites"
                    : "Add to favorites"
                )
            }
        }
        .padding(16)
        .background(cardBackground(cornerRadius: 18))
    }

    private var citationCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Citations")
                .font(.system(.headline, design: .rounded))
                .foregroundStyle(AppTheme.textPrimary)

            ForEach(trial.citations) { citation in
                Link(destination: citation.url) {
                    HStack(alignment: .top, spacing: 10) {
                        Image(systemName: "doc.text")
                            .foregroundStyle(AppTheme.accent)
                        VStack(alignment: .leading, spacing: 4) {
                            Text(citation.title)
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(AppTheme.textPrimary)
                                .multilineTextAlignment(.leading)
                            Text("\(citation.journal), \(citation.year)")
                                .font(.footnote)
                                .foregroundStyle(AppTheme.textSecondary)
                        }
                        Spacer(minLength: 0)
                        Image(systemName: "arrow.up.right")
                            .font(.caption)
                            .foregroundStyle(AppTheme.textSecondary)
                    }
                    .padding(12)
                    .background(
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .fill(Color.white.opacity(0.82))
                    )
                }
                .buttonStyle(.plain)
            }
        }
        .padding(16)
        .background(cardBackground(cornerRadius: 18))
    }

    private func cardBackground(cornerRadius: CGFloat) -> some View {
        RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
            .fill(AppTheme.card)
            .overlay(
                RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                    .stroke(AppTheme.border, lineWidth: 1)
            )
            .shadow(color: AppTheme.shadow, radius: 10, x: 0, y: 6)
    }
}

private struct TrialAppraisalCard: View {
    let appraisal: TrialAppraisal

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Critical Appraisal")
                .font(.system(.headline, design: .rounded))
                .foregroundStyle(AppTheme.textPrimary)

            AppraisalTextBlock(title: "Clinical Question", text: appraisal.clinicalQuestion)
            AppraisalTextBlock(title: "Background", text: appraisal.background)
            AppraisalTextBlock(title: "Design", text: appraisal.design)
            AppraisalBulletBlock(title: "Key Results", points: appraisal.keyResults)
            AppraisalBulletBlock(title: "Strengths", points: appraisal.strengths)
            AppraisalBulletBlock(title: "Weaknesses / Caveats", points: appraisal.weaknesses)
            AppraisalTextBlock(title: "Bottom Line", text: appraisal.bottomLine)
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .fill(AppTheme.card)
                .overlay(
                    RoundedRectangle(cornerRadius: 18, style: .continuous)
                        .stroke(AppTheme.border, lineWidth: 1)
                )
        )
        .shadow(color: AppTheme.shadow, radius: 10, x: 0, y: 6)
    }
}

private struct AppraisalTextBlock: View {
    let title: String
    let text: String

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(AppTheme.textPrimary)
            Text(text)
                .font(.subheadline)
                .foregroundStyle(AppTheme.textPrimary)
        }
    }
}

private struct AppraisalBulletBlock: View {
    let title: String
    let points: [String]

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(AppTheme.textPrimary)

            ForEach(Array(points.enumerated()), id: \.offset) { _, point in
                HStack(alignment: .top, spacing: 8) {
                    Circle()
                        .fill(AppTheme.accentSoft)
                        .frame(width: 6, height: 6)
                        .padding(.top, 7)
                    Text(point)
                        .font(.subheadline)
                        .foregroundStyle(AppTheme.textPrimary)
                }
            }
        }
    }
}

private struct TrialDetailSection: View {
    let title: String
    let text: String

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.system(.headline, design: .rounded))
                .foregroundStyle(AppTheme.textPrimary)
            Text(text)
                .font(.body)
                .foregroundStyle(AppTheme.textPrimary)
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .fill(AppTheme.card)
                .overlay(
                    RoundedRectangle(cornerRadius: 16, style: .continuous)
                        .stroke(AppTheme.border, lineWidth: 1)
                )
        )
        .shadow(color: AppTheme.shadow, radius: 8, x: 0, y: 4)
    }
}
