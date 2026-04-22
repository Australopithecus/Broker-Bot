import Foundation

struct NewsItem: Codable, Identifiable {
    let id: UUID = UUID()
    let headline: String
    let summary: String
    let source: String

    enum CodingKeys: String, CodingKey {
        case headline
        case summary
        case source
    }
}

struct DailyContent: Codable {
    let date: String
    let news: [NewsItem]
    let icuTrialSummary: String
    let historicalFact: String
    let generatedAt: String

    enum CodingKeys: String, CodingKey {
        case date
        case news
        case icuTrialSummary = "icu_trial_summary"
        case historicalFact = "historical_fact"
        case generatedAt = "generated_at"
    }
}

struct CalendarEvent: Identifiable {
    let id = UUID()
    let title: String
    let start: Date
    let end: Date
    let location: String?
}

struct WeatherSummary {
    let high: Double
    let low: Double
    let precipitationChance: Double
    let narrative: String
}

struct WorkoutRecommendation {
    let title: String
    let start: Date?
    let end: Date?
    let fallbackNote: String?
}

enum TrialEra: String, CaseIterable, Hashable {
    case landmark = "Landmark"
    case recent = "Recent"
}

enum EvidenceStrength: String, Hashable {
    case practiceChanging = "Practice-Changing"
    case neutral = "Neutral"
    case harmSignal = "Harm Signal"

    var interpretation: String {
        switch self {
        case .practiceChanging:
            return "Findings meaningfully shifted ICU standards or guideline-supported routine care."
        case .neutral:
            return "No clear superiority signal; treatment choice is typically individualized."
        case .harmSignal:
            return "Intervention showed potential harm or worsened important outcomes."
        }
    }
}

enum TrialTopic: String, CaseIterable, Identifiable, Hashable {
    case ards = "ARDS"
    case sepsis = "Sepsis"
    case septicShock = "Septic Shock"
    case fluids = "Fluids"
    case steroids = "Steroids"
    case transfusion = "Transfusion"
    case covid19 = "COVID-19"
    case generalICU = "General ICU"

    var id: String { rawValue }
}

struct TrialCitation: Identifiable, Hashable {
    let id: String
    let title: String
    let journal: String
    let year: Int
    let url: URL
}

struct TrialAppraisal: Hashable {
    let clinicalQuestion: String
    let background: String
    let design: String
    let keyResults: [String]
    let strengths: [String]
    let weaknesses: [String]
    let bottomLine: String

    var searchIndexTerms: [String] {
        [clinicalQuestion, background, design, bottomLine] + keyResults + strengths + weaknesses
    }
}

struct ICUTrial: Identifiable, Hashable {
    let id: String
    let shortName: String
    let fullTitle: String
    let year: Int
    let era: TrialEra
    let topic: TrialTopic
    let patientPopulation: String
    let intervention: String
    let comparator: String
    let primaryOutcome: String
    let bottomLine: String
    let practiceTakeaway: String
    let tags: [String]
    let citations: [TrialCitation]

    var appraisal: TrialAppraisal {
        let journalName = citations.first?.journal ?? "a peer-reviewed journal"
        let trialYear = citations.first?.year ?? year

        let design = "Comparative critical care trial published in \(journalName) (\(trialYear)). Appraisal here is based on summary-level trial data; full paper review is still essential for effect sizes, subgroup behavior, and protocol nuances."

        return TrialAppraisal(
            clinicalQuestion: "In \(patientPopulation), does \(intervention) compared with \(comparator) improve \(primaryOutcome)?",
            background: topicBackground,
            design: design,
            keyResults: [
                "Primary endpoint: \(primaryOutcome).",
                bottomLine,
                "Evidence signal in this app: \(evidenceStrength.rawValue)."
            ],
            strengths: [
                "Clinically relevant comparison: \(intervention) vs \(comparator).",
                "Patient population and endpoint are directly ICU-practice facing.",
                "Published in a high-impact, peer-reviewed source (\(journalName))."
            ],
            weaknesses: [
                "This summary does not include full effect-size granularity (absolute risk changes, confidence intervals, and all subgroup interactions).",
                "External validity may vary across ICU settings, staffing models, adjunct therapies, and local protocols.",
                "Practice interpretation should be integrated with current guidelines and your specific patient phenotype."
            ],
            bottomLine: "\(practiceTakeaway) \(evidenceStrength.interpretation)"
        )
    }

    var evidenceStrength: EvidenceStrength {
        switch id {
        case
            "TRICC",
            "ARMA",
            "PROSEVA",
            "SMART",
            "RECOVERY-DEX",
            "APROCCHSS",
            "STARRT-AKI",
            "REMAP-IL6",
            "BALANCE",
            "PREOXI",
            "TRAIN":
            return .practiceChanging

        case
            "NICE-SUGAR",
            "CHEST",
            "OSCILLATE",
            "LOVIT":
            return .harmSignal

        default:
            return .neutral
        }
    }

    var searchIndex: [String] {
        [
            shortName,
            fullTitle,
            topic.rawValue,
            era.rawValue,
            evidenceStrength.rawValue,
            patientPopulation,
            intervention,
            comparator,
            primaryOutcome,
            bottomLine,
            practiceTakeaway
        ] + appraisal.searchIndexTerms + tags
    }

    private var topicBackground: String {
        switch topic {
        case .ards:
            return "ARDS trials usually balance oxygenation gains against ventilator-associated lung injury and sedation burden."
        case .sepsis:
            return "Sepsis evidence often focuses on timing and intensity of antibiotics, source control, and organ support strategies."
        case .septicShock:
            return "Septic shock studies typically examine how hemodynamic targets and adjuncts affect perfusion, organ failure, and survival."
        case .fluids:
            return "Fluid trials evaluate the tradeoff between restoring perfusion and avoiding fluid overload, kidney injury, and downstream complications."
        case .steroids:
            return "Steroid studies in critical illness often assess faster shock reversal versus potential metabolic, infectious, or neuromuscular harms."
        case .transfusion:
            return "Transfusion research weighs oxygen-delivery benefits against transfusion-related complications and resource exposure."
        case .covid19:
            return "COVID-19 ICU trials must be interpreted in the context of evolving variants, baseline immunity, and co-treatments."
        case .generalICU:
            return "General ICU trials often involve heterogeneous populations, so bedside applicability depends on matching trial phenotype to patient context."
        }
    }
}

enum ICUTrialLibrary {
    private static func pubmed(_ pmid: String) -> URL {
        URL(string: "https://pubmed.ncbi.nlm.nih.gov/\(pmid)/")!
    }

    static let allTrials: [ICUTrial] = [
        ICUTrial(
            id: "TRICC",
            shortName: "TRICC",
            fullTitle: "A multicenter, randomized, controlled clinical trial of transfusion requirements in critical care",
            year: 1999,
            era: .landmark,
            topic: .transfusion,
            patientPopulation: "Hemodynamically stable, critically ill adults",
            intervention: "Restrictive transfusion strategy (Hgb target 7-9 g/dL)",
            comparator: "Liberal transfusion strategy (Hgb target 10-12 g/dL)",
            primaryOutcome: "30-day all-cause mortality",
            bottomLine: "A restrictive transfusion strategy was at least as safe as liberal transfusion and became foundational ICU practice.",
            practiceTakeaway: "For most stable ICU patients, transfuse conservatively unless there is specific ischemic risk or active bleeding.",
            tags: ["hemoglobin", "blood products", "critical care"],
            citations: [
                TrialCitation(
                    id: "TRICC-primary",
                    title: "A multicenter, randomized, controlled clinical trial of transfusion requirements in critical care",
                    journal: "N Engl J Med",
                    year: 1999,
                    url: pubmed("9971864")
                )
            ]
        ),
        ICUTrial(
            id: "ARMA",
            shortName: "ARMA (ARDSNet)",
            fullTitle: "Ventilation with lower tidal volumes as compared with traditional tidal volumes for acute lung injury and ARDS",
            year: 2000,
            era: .landmark,
            topic: .ards,
            patientPopulation: "Adults with acute lung injury/ARDS on mechanical ventilation",
            intervention: "Low tidal volume ventilation (6 mL/kg predicted body weight)",
            comparator: "Traditional tidal volume ventilation (12 mL/kg predicted body weight)",
            primaryOutcome: "Mortality before hospital discharge (up to day 180)",
            bottomLine: "Low tidal volume ventilation reduced mortality and established lung-protective ventilation as standard care.",
            practiceTakeaway: "Ventilator settings should prioritize lung protection, even if permissive hypercapnia is needed.",
            tags: ["mechanical ventilation", "lung protective", "ALI"],
            citations: [
                TrialCitation(
                    id: "ARMA-primary",
                    title: "Ventilation with lower tidal volumes as compared with traditional tidal volumes",
                    journal: "N Engl J Med",
                    year: 2000,
                    url: pubmed("10793162")
                )
            ]
        ),
        ICUTrial(
            id: "RIVERS",
            shortName: "Rivers EGDT",
            fullTitle: "Early goal-directed therapy in the treatment of severe sepsis and septic shock",
            year: 2001,
            era: .landmark,
            topic: .sepsis,
            patientPopulation: "Adults presenting with severe sepsis or septic shock",
            intervention: "Protocolized early goal-directed resuscitation in first 6 hours",
            comparator: "Usual care of the era",
            primaryOutcome: "In-hospital mortality",
            bottomLine: "The trial accelerated aggressive early sepsis resuscitation protocols and drove major systems-level change.",
            practiceTakeaway: "Even as protocols evolve, rapid recognition and early resuscitation remain central in septic shock care.",
            tags: ["EGDT", "resuscitation", "emergency department"],
            citations: [
                TrialCitation(
                    id: "RIVERS-primary",
                    title: "Early goal-directed therapy in the treatment of severe sepsis and septic shock",
                    journal: "N Engl J Med",
                    year: 2001,
                    url: pubmed("11794169")
                )
            ]
        ),
        ICUTrial(
            id: "SAFE",
            shortName: "SAFE",
            fullTitle: "A comparison of albumin and saline for fluid resuscitation in the intensive care unit",
            year: 2004,
            era: .landmark,
            topic: .fluids,
            patientPopulation: "Heterogeneous ICU patients requiring fluid resuscitation",
            intervention: "4% albumin",
            comparator: "0.9% saline",
            primaryOutcome: "28-day all-cause mortality",
            bottomLine: "No mortality difference overall between albumin and saline in general ICU resuscitation.",
            practiceTakeaway: "Choice of crystalloid vs albumin should be individualized by phenotype and local practice rather than routine default albumin.",
            tags: ["albumin", "saline", "resuscitation"],
            citations: [
                TrialCitation(
                    id: "SAFE-primary",
                    title: "A comparison of albumin and saline for fluid resuscitation in the intensive care unit",
                    journal: "N Engl J Med",
                    year: 2004,
                    url: pubmed("15163774")
                )
            ]
        ),
        ICUTrial(
            id: "CORTICUS",
            shortName: "CORTICUS",
            fullTitle: "Hydrocortisone therapy for patients with septic shock",
            year: 2008,
            era: .landmark,
            topic: .septicShock,
            patientPopulation: "Adults with septic shock",
            intervention: "Hydrocortisone",
            comparator: "Placebo",
            primaryOutcome: "28-day mortality in nonresponders to corticotropin",
            bottomLine: "Hydrocortisone accelerated shock reversal but did not improve survival in this trial.",
            practiceTakeaway: "Corticosteroids are often used for vasopressor-refractory shock to facilitate hemodynamic recovery, with survival effects interpreted in context of later trials.",
            tags: ["vasopressor refractory", "adrenal axis", "steroids"],
            citations: [
                TrialCitation(
                    id: "CORTICUS-primary",
                    title: "Hydrocortisone therapy for patients with septic shock",
                    journal: "N Engl J Med",
                    year: 2008,
                    url: pubmed("18184957")
                )
            ]
        ),
        ICUTrial(
            id: "NICE-SUGAR",
            shortName: "NICE-SUGAR",
            fullTitle: "Intensive versus conventional glucose control in critically ill patients",
            year: 2009,
            era: .landmark,
            topic: .generalICU,
            patientPopulation: "Mixed medical-surgical ICU adults",
            intervention: "Intensive glucose target (81-108 mg/dL)",
            comparator: "Conventional target (<180 mg/dL)",
            primaryOutcome: "90-day all-cause mortality",
            bottomLine: "Very tight glycemic control increased harm risk and shifted practice toward more moderate glucose targets.",
            practiceTakeaway: "Avoid aggressive glucose lowering that increases hypoglycemia risk in critically ill patients.",
            tags: ["insulin", "glycemic control", "hypoglycemia"],
            citations: [
                TrialCitation(
                    id: "NICE-SUGAR-primary",
                    title: "Intensive versus conventional glucose control in critically ill patients",
                    journal: "N Engl J Med",
                    year: 2009,
                    url: pubmed("19318384")
                )
            ]
        ),
        ICUTrial(
            id: "ACURASYS",
            shortName: "ACURASYS",
            fullTitle: "Neuromuscular blockers in early acute respiratory distress syndrome",
            year: 2010,
            era: .landmark,
            topic: .ards,
            patientPopulation: "Adults with early, severe ARDS",
            intervention: "48-hour cisatracurium infusion",
            comparator: "Placebo with deep sedation strategy",
            primaryOutcome: "90-day mortality",
            bottomLine: "Early paralysis showed improved outcomes in this pre-high-PEEP era ARDS trial.",
            practiceTakeaway: "Neuromuscular blockade can be useful in selected severe ARDS, but must be weighed against modern ventilation and sedation strategies.",
            tags: ["cisatracurium", "ventilation synchrony", "severe ARDS"],
            citations: [
                TrialCitation(
                    id: "ACURASYS-primary",
                    title: "Neuromuscular blockers in early acute respiratory distress syndrome",
                    journal: "N Engl J Med",
                    year: 2010,
                    url: pubmed("20843245")
                )
            ]
        ),
        ICUTrial(
            id: "PROSEVA",
            shortName: "PROSEVA",
            fullTitle: "Prone positioning in severe acute respiratory distress syndrome",
            year: 2013,
            era: .landmark,
            topic: .ards,
            patientPopulation: "Adults with severe ARDS",
            intervention: "Early prolonged prone positioning",
            comparator: "Supine positioning",
            primaryOutcome: "28-day all-cause mortality",
            bottomLine: "Proning significantly reduced mortality in severe ARDS when done early and for prolonged sessions.",
            practiceTakeaway: "Proning is a high-value intervention in severe ARDS when teams are trained and protocols are consistent.",
            tags: ["prone", "oxygenation", "mechanical ventilation"],
            citations: [
                TrialCitation(
                    id: "PROSEVA-primary",
                    title: "Prone positioning in severe acute respiratory distress syndrome",
                    journal: "N Engl J Med",
                    year: 2013,
                    url: pubmed("23688302")
                )
            ]
        ),
        ICUTrial(
            id: "PROCESS",
            shortName: "ProCESS",
            fullTitle: "A randomized trial of protocol-based care for early septic shock",
            year: 2014,
            era: .landmark,
            topic: .sepsis,
            patientPopulation: "Adults with early septic shock in emergency settings",
            intervention: "Protocolized EGDT or protocolized standard therapy",
            comparator: "Usual contemporary care",
            primaryOutcome: "60-day in-hospital mortality",
            bottomLine: "In modern systems with early antibiotics and fluids, protocolized EGDT was not superior to usual care.",
            practiceTakeaway: "Sepsis outcomes improve with reliable early care bundles, even without invasive EGDT targets.",
            tags: ["sepsis bundle", "resuscitation", "protocolized care"],
            citations: [
                TrialCitation(
                    id: "PROCESS-primary",
                    title: "A randomized trial of protocol-based care for early septic shock",
                    journal: "N Engl J Med",
                    year: 2014,
                    url: pubmed("24635773")
                )
            ]
        ),
        ICUTrial(
            id: "EOLIA",
            shortName: "EOLIA",
            fullTitle: "Extracorporeal membrane oxygenation for severe acute respiratory distress syndrome",
            year: 2018,
            era: .recent,
            topic: .ards,
            patientPopulation: "Adults with very severe ARDS",
            intervention: "Early venovenous ECMO",
            comparator: "Conventional mechanical ventilation strategy",
            primaryOutcome: "60-day mortality",
            bottomLine: "The primary endpoint was not statistically significant, but crossover and secondary analyses support ECMO consideration in selected refractory severe ARDS.",
            practiceTakeaway: "ECMO is best considered in experienced centers for carefully selected patients with severe refractory hypoxemia or hypercapnia.",
            tags: ["VV-ECMO", "refractory hypoxemia", "advanced support"],
            citations: [
                TrialCitation(
                    id: "EOLIA-primary",
                    title: "Extracorporeal membrane oxygenation for severe acute respiratory distress syndrome",
                    journal: "N Engl J Med",
                    year: 2018,
                    url: pubmed("29791822")
                )
            ]
        ),
        ICUTrial(
            id: "SMART",
            shortName: "SMART",
            fullTitle: "Balanced crystalloids versus saline in critically ill adults",
            year: 2018,
            era: .recent,
            topic: .fluids,
            patientPopulation: "Adults admitted to ICU requiring crystalloid therapy",
            intervention: "Balanced crystalloids (LR or Plasma-Lyte)",
            comparator: "0.9% saline",
            primaryOutcome: "Major adverse kidney events within 30 days (MAKE30)",
            bottomLine: "Balanced crystalloids modestly reduced major adverse kidney events compared with saline.",
            practiceTakeaway: "Balanced solutions are commonly preferred for many ICU patients, especially when chloride load is a concern.",
            tags: ["LR", "Plasma-Lyte", "kidney outcomes"],
            citations: [
                TrialCitation(
                    id: "SMART-primary",
                    title: "Balanced crystalloids versus saline in critically ill adults",
                    journal: "N Engl J Med",
                    year: 2018,
                    url: pubmed("29485925")
                )
            ]
        ),
        ICUTrial(
            id: "ADRENAL",
            shortName: "ADRENAL",
            fullTitle: "Adjunctive glucocorticoid therapy in patients with septic shock",
            year: 2018,
            era: .recent,
            topic: .steroids,
            patientPopulation: "Mechanically ventilated adults with septic shock",
            intervention: "Hydrocortisone infusion",
            comparator: "Placebo",
            primaryOutcome: "90-day all-cause mortality",
            bottomLine: "Hydrocortisone did not reduce 90-day mortality but improved several secondary recovery outcomes.",
            practiceTakeaway: "Steroids can shorten vasopressor duration in septic shock, with mortality impact interpreted alongside other corticosteroid trials.",
            tags: ["hydrocortisone", "vasopressors", "shock reversal"],
            citations: [
                TrialCitation(
                    id: "ADRENAL-primary",
                    title: "Adjunctive glucocorticoid therapy in patients with septic shock",
                    journal: "N Engl J Med",
                    year: 2018,
                    url: pubmed("29347874")
                )
            ]
        ),
        ICUTrial(
            id: "APROCCHSS",
            shortName: "APROCCHSS",
            fullTitle: "Hydrocortisone plus fludrocortisone for adults with septic shock",
            year: 2018,
            era: .recent,
            topic: .steroids,
            patientPopulation: "Adults with septic shock",
            intervention: "Hydrocortisone plus fludrocortisone",
            comparator: "Placebo",
            primaryOutcome: "90-day all-cause mortality",
            bottomLine: "Combined hydrocortisone/fludrocortisone improved survival in septic shock in this multicenter trial.",
            practiceTakeaway: "Some ICUs consider dual-steroid therapy in septic shock protocols based on local interpretation and guideline alignment.",
            tags: ["fludrocortisone", "corticosteroids", "septic shock"],
            citations: [
                TrialCitation(
                    id: "APROCCHSS-primary",
                    title: "Hydrocortisone plus fludrocortisone for adults with septic shock",
                    journal: "N Engl J Med",
                    year: 2018,
                    url: pubmed("29490185")
                )
            ]
        ),
        ICUTrial(
            id: "ROSE",
            shortName: "ROSE",
            fullTitle: "Early neuromuscular blockade in the acute respiratory distress syndrome",
            year: 2019,
            era: .recent,
            topic: .ards,
            patientPopulation: "Adults with moderate-to-severe ARDS",
            intervention: "Early continuous cisatracurium with deep sedation",
            comparator: "Usual-care strategy with lighter sedation targets",
            primaryOutcome: "90-day in-hospital mortality",
            bottomLine: "Unlike ACURASYS, routine early neuromuscular blockade did not improve mortality in this modern ARDS strategy trial.",
            practiceTakeaway: "Paralysis is generally reserved for selected severe cases rather than automatic early routine use.",
            tags: ["neuromuscular blockade", "sedation strategy", "ARDS management"],
            citations: [
                TrialCitation(
                    id: "ROSE-primary",
                    title: "Early neuromuscular blockade in the acute respiratory distress syndrome",
                    journal: "N Engl J Med",
                    year: 2019,
                    url: pubmed("31112383")
                )
            ]
        ),
        ICUTrial(
            id: "RECOVERY-DEX",
            shortName: "RECOVERY Dexamethasone",
            fullTitle: "Dexamethasone in hospitalized patients with Covid-19",
            year: 2021,
            era: .recent,
            topic: .covid19,
            patientPopulation: "Hospitalized adults with COVID-19 requiring respiratory support",
            intervention: "Dexamethasone 6 mg daily up to 10 days",
            comparator: "Usual care",
            primaryOutcome: "28-day mortality",
            bottomLine: "Dexamethasone reduced mortality in patients needing oxygen or mechanical ventilation.",
            practiceTakeaway: "This trial rapidly changed critical care treatment standards for severe COVID-19 respiratory failure.",
            tags: ["SARS-CoV-2", "steroids", "respiratory failure"],
            citations: [
                TrialCitation(
                    id: "RECOVERY-DEX-primary",
                    title: "Dexamethasone in hospitalized patients with Covid-19",
                    journal: "N Engl J Med",
                    year: 2021,
                    url: pubmed("32678530")
                )
            ]
        ),
        ICUTrial(
            id: "PLUS",
            shortName: "PLUS",
            fullTitle: "Balanced multielectrolyte solution versus saline in critically ill adults",
            year: 2022,
            era: .recent,
            topic: .fluids,
            patientPopulation: "Adults admitted to ICU needing crystalloid therapy",
            intervention: "Plasma-Lyte 148",
            comparator: "0.9% saline",
            primaryOutcome: "90-day mortality",
            bottomLine: "PLUS did not show a mortality difference between balanced fluid and saline in a broad ICU population.",
            practiceTakeaway: "Fluid selection should be individualized by phenotype and context; balanced fluids are reasonable but not universally superior.",
            tags: ["balanced crystalloid", "Plasma-Lyte", "mortality"],
            citations: [
                TrialCitation(
                    id: "PLUS-primary",
                    title: "Balanced multielectrolyte solution versus saline in critically ill adults",
                    journal: "N Engl J Med",
                    year: 2022,
                    url: pubmed("35041780")
                )
            ]
        ),
        ICUTrial(
            id: "CLASSIC",
            shortName: "CLASSIC",
            fullTitle: "Restriction of intravenous fluid in ICU patients with septic shock",
            year: 2022,
            era: .recent,
            topic: .septicShock,
            patientPopulation: "Adults with septic shock in ICU after initial fluids",
            intervention: "Restrictive intravenous fluid strategy",
            comparator: "Standard intravenous fluid strategy",
            primaryOutcome: "90-day mortality",
            bottomLine: "Restrictive fluid strategy did not reduce mortality compared with standard care in established ICU septic shock.",
            practiceTakeaway: "After initial resuscitation, fluid strategy should remain dynamic and guided by perfusion and congestion, not one-size-fits-all.",
            tags: ["resuscitation", "fluid restriction", "vasopressor"],
            citations: [
                TrialCitation(
                    id: "CLASSIC-primary",
                    title: "Restriction of intravenous fluid in ICU patients with septic shock",
                    journal: "N Engl J Med",
                    year: 2022,
                    url: pubmed("35709019")
                )
            ]
        ),
        ICUTrial(
            id: "LOVIT",
            shortName: "LOVIT",
            fullTitle: "Intravenous vitamin C in adults with sepsis in the intensive care unit",
            year: 2022,
            era: .recent,
            topic: .sepsis,
            patientPopulation: "Adults with sepsis on vasopressors in ICU",
            intervention: "High-dose intravenous vitamin C",
            comparator: "Placebo",
            primaryOutcome: "Composite of death or persistent organ dysfunction at day 28",
            bottomLine: "Vitamin C was associated with higher risk of death or persistent organ dysfunction.",
            practiceTakeaway: "Routine high-dose vitamin C is not supported for vasopressor-dependent sepsis based on current randomized evidence.",
            tags: ["adjunctive therapy", "organ dysfunction", "vasopressors"],
            citations: [
                TrialCitation(
                    id: "LOVIT-primary",
                    title: "Intravenous vitamin C in adults with sepsis in the intensive care unit",
                    journal: "N Engl J Med",
                    year: 2022,
                    url: pubmed("35704292")
                )
            ]
        ),
        ICUTrial(
            id: "CLOVERS",
            shortName: "CLOVERS",
            fullTitle: "Early restrictive or liberal fluid management for sepsis-induced hypotension",
            year: 2023,
            era: .recent,
            topic: .sepsis,
            patientPopulation: "Adults with sepsis-induced hypotension refractory to initial fluid",
            intervention: "Restrictive strategy prioritizing earlier vasopressors",
            comparator: "Liberal strategy prioritizing additional fluids",
            primaryOutcome: "Death before discharge home by day 90",
            bottomLine: "Restrictive versus liberal early fluid strategy did not significantly change 90-day mortality.",
            practiceTakeaway: "Early hemodynamic strategy can be tailored; close bedside reassessment may matter more than rigid protocol volume targets.",
            tags: ["early sepsis", "vasopressor-first", "fluid-first"],
            citations: [
                TrialCitation(
                    id: "CLOVERS-primary",
                    title: "Early restrictive or liberal fluid management for sepsis-induced hypotension",
                    journal: "N Engl J Med",
                    year: 2023,
                    url: pubmed("36688507")
                )
            ]
        ),
        ICUTrial(
            id: "ALVEOLI",
            shortName: "ALVEOLI",
            fullTitle: "Higher versus lower positive end-expiratory pressures in patients with acute respiratory distress syndrome",
            year: 2004,
            era: .landmark,
            topic: .ards,
            patientPopulation: "Adults with acute lung injury/ARDS receiving low tidal volume ventilation",
            intervention: "Higher PEEP strategy",
            comparator: "Lower PEEP strategy",
            primaryOutcome: "In-hospital mortality before discharge home",
            bottomLine: "Higher PEEP did not significantly improve mortality overall in this ARDSNet trial.",
            practiceTakeaway: "PEEP should be individualized to recruit lung while limiting overdistention and hemodynamic compromise.",
            tags: ["PEEP", "mechanical ventilation", "ARDSNet"],
            citations: [
                TrialCitation(
                    id: "ALVEOLI-primary",
                    title: "Higher versus lower positive end-expiratory pressures in patients with the acute respiratory distress syndrome",
                    journal: "N Engl J Med",
                    year: 2004,
                    url: pubmed("15269312")
                )
            ]
        ),
        ICUTrial(
            id: "FACTT",
            shortName: "FACTT",
            fullTitle: "Comparison of two fluid-management strategies in acute lung injury",
            year: 2006,
            era: .landmark,
            topic: .ards,
            patientPopulation: "Adults with acute lung injury requiring mechanical ventilation",
            intervention: "Conservative fluid strategy",
            comparator: "Liberal fluid strategy",
            primaryOutcome: "60-day mortality",
            bottomLine: "Mortality was similar, but conservative fluid management improved ventilator-free and ICU-free days.",
            practiceTakeaway: "After initial resuscitation in ARDS, conservative fluid balance can improve respiratory recovery.",
            tags: ["fluid balance", "ventilator-free days", "ARDSNet"],
            citations: [
                TrialCitation(
                    id: "FACTT-primary",
                    title: "Comparison of two fluid-management strategies in acute lung injury",
                    journal: "N Engl J Med",
                    year: 2006,
                    url: pubmed("16714767")
                )
            ]
        ),
        ICUTrial(
            id: "VASST",
            shortName: "VASST",
            fullTitle: "Vasopressin versus norepinephrine infusion in patients with septic shock",
            year: 2008,
            era: .landmark,
            topic: .septicShock,
            patientPopulation: "Adults with vasopressor-dependent septic shock",
            intervention: "Low-dose vasopressin infusion",
            comparator: "Norepinephrine infusion",
            primaryOutcome: "28-day mortality",
            bottomLine: "Vasopressin did not improve mortality overall compared with norepinephrine.",
            practiceTakeaway: "Vasopressin is often used as an adjunct vasopressor rather than a mortality-improving replacement for norepinephrine.",
            tags: ["vasopressors", "norepinephrine", "hemodynamics"],
            citations: [
                TrialCitation(
                    id: "VASST-primary",
                    title: "Vasopressin versus norepinephrine infusion in patients with septic shock",
                    journal: "N Engl J Med",
                    year: 2008,
                    url: pubmed("18305265")
                )
            ]
        ),
        ICUTrial(
            id: "CHEST",
            shortName: "CHEST",
            fullTitle: "Hydroxyethyl starch or saline for fluid resuscitation in intensive care",
            year: 2012,
            era: .landmark,
            topic: .fluids,
            patientPopulation: "Heterogeneous ICU adults requiring fluid resuscitation",
            intervention: "6% hydroxyethyl starch (130/0.4)",
            comparator: "0.9% saline",
            primaryOutcome: "90-day mortality",
            bottomLine: "Hydroxyethyl starch increased renal replacement therapy use without survival benefit.",
            practiceTakeaway: "Modern ICU resuscitation generally avoids HES because of kidney and safety concerns.",
            tags: ["HES", "renal injury", "resuscitation fluids"],
            citations: [
                TrialCitation(
                    id: "CHEST-primary",
                    title: "Hydroxyethyl starch or saline for fluid resuscitation in intensive care",
                    journal: "N Engl J Med",
                    year: 2012,
                    url: pubmed("23075127")
                )
            ]
        ),
        ICUTrial(
            id: "OSCILLATE",
            shortName: "OSCILLATE",
            fullTitle: "High-frequency oscillation in early acute respiratory distress syndrome",
            year: 2013,
            era: .landmark,
            topic: .ards,
            patientPopulation: "Adults with early moderate-to-severe ARDS",
            intervention: "High-frequency oscillatory ventilation",
            comparator: "Conventional lung-protective ventilation",
            primaryOutcome: "In-hospital mortality",
            bottomLine: "HFOV increased mortality in this trial and is not routine ARDS practice.",
            practiceTakeaway: "Conventional lung-protective ventilation remains first-line for most ARDS patients.",
            tags: ["HFOV", "ventilation strategy", "mortality"],
            citations: [
                TrialCitation(
                    id: "OSCILLATE-primary",
                    title: "High-frequency oscillation in early acute respiratory distress syndrome",
                    journal: "N Engl J Med",
                    year: 2013,
                    url: pubmed("23339639")
                )
            ]
        ),
        ICUTrial(
            id: "OSCAR",
            shortName: "OSCAR",
            fullTitle: "High-frequency oscillation for acute respiratory distress syndrome",
            year: 2013,
            era: .landmark,
            topic: .ards,
            patientPopulation: "Adults with ARDS receiving mechanical ventilation",
            intervention: "High-frequency oscillatory ventilation",
            comparator: "Usual conventional ventilation",
            primaryOutcome: "30-day mortality",
            bottomLine: "HFOV did not improve survival compared with conventional ventilation.",
            practiceTakeaway: "Together with OSCILLATE, this trial discouraged routine HFOV use in adult ARDS.",
            tags: ["HFOV", "ARDS ventilation", "critical care trial"],
            citations: [
                TrialCitation(
                    id: "OSCAR-primary",
                    title: "High-frequency oscillation for acute respiratory distress syndrome",
                    journal: "N Engl J Med",
                    year: 2013,
                    url: pubmed("23339638")
                )
            ]
        ),
        ICUTrial(
            id: "ALBIOS",
            shortName: "ALBIOS",
            fullTitle: "Albumin replacement in patients with severe sepsis or septic shock",
            year: 2014,
            era: .landmark,
            topic: .fluids,
            patientPopulation: "Adults with severe sepsis or septic shock",
            intervention: "20% albumin plus crystalloid",
            comparator: "Crystalloid alone",
            primaryOutcome: "28-day mortality",
            bottomLine: "Albumin replacement did not significantly reduce mortality in the overall cohort.",
            practiceTakeaway: "Albumin may be selectively used, but broad routine use for all sepsis patients is not strongly supported.",
            tags: ["albumin", "sepsis", "resuscitation"],
            citations: [
                TrialCitation(
                    id: "ALBIOS-primary",
                    title: "Albumin replacement in patients with severe sepsis or septic shock",
                    journal: "N Engl J Med",
                    year: 2014,
                    url: pubmed("24635772")
                )
            ]
        ),
        ICUTrial(
            id: "SEPSISPAM",
            shortName: "SEPSISPAM",
            fullTitle: "High versus low blood-pressure target in patients with septic shock",
            year: 2014,
            era: .landmark,
            topic: .septicShock,
            patientPopulation: "Adults with septic shock on vasopressor support",
            intervention: "Higher MAP target (80-85 mm Hg)",
            comparator: "Lower MAP target (65-70 mm Hg)",
            primaryOutcome: "28-day and 90-day mortality",
            bottomLine: "Higher MAP targets did not reduce mortality overall but reduced need for renal replacement in chronic hypertension subgroup.",
            practiceTakeaway: "MAP goals are usually individualized, especially in patients with chronic hypertension or kidney vulnerability.",
            tags: ["MAP target", "vasopressors", "hemodynamics"],
            citations: [
                TrialCitation(
                    id: "SEPSISPAM-primary",
                    title: "High versus low blood-pressure target in patients with septic shock",
                    journal: "N Engl J Med",
                    year: 2014,
                    url: pubmed("24635770")
                )
            ]
        ),
        ICUTrial(
            id: "TRISS",
            shortName: "TRISS",
            fullTitle: "Lower versus higher hemoglobin threshold for transfusion in septic shock",
            year: 2014,
            era: .landmark,
            topic: .transfusion,
            patientPopulation: "Adults with septic shock in ICU",
            intervention: "Restrictive transfusion threshold (hemoglobin 7 g/dL)",
            comparator: "Liberal transfusion threshold (hemoglobin 9 g/dL)",
            primaryOutcome: "90-day mortality",
            bottomLine: "A lower transfusion threshold was noninferior and reduced blood product use.",
            practiceTakeaway: "Restrictive transfusion approaches are generally appropriate in septic shock unless specific contraindications exist.",
            tags: ["hemoglobin threshold", "blood products", "septic shock"],
            citations: [
                TrialCitation(
                    id: "TRISS-primary",
                    title: "Lower versus higher hemoglobin threshold for transfusion in septic shock",
                    journal: "N Engl J Med",
                    year: 2014,
                    url: pubmed("25270275")
                )
            ]
        ),
        ICUTrial(
            id: "ARISE",
            shortName: "ARISE",
            fullTitle: "Goal-directed resuscitation for patients with early septic shock",
            year: 2014,
            era: .landmark,
            topic: .sepsis,
            patientPopulation: "Adults with early septic shock",
            intervention: "Protocolized early goal-directed therapy",
            comparator: "Usual contemporary care",
            primaryOutcome: "90-day mortality",
            bottomLine: "EGDT did not improve mortality over modern usual care.",
            practiceTakeaway: "High-quality, early sepsis care is key even without invasive EGDT targets.",
            tags: ["EGDT", "early sepsis", "resuscitation protocol"],
            citations: [
                TrialCitation(
                    id: "ARISE-primary",
                    title: "Goal-directed resuscitation for patients with early septic shock",
                    journal: "N Engl J Med",
                    year: 2014,
                    url: pubmed("25272316")
                )
            ]
        ),
        ICUTrial(
            id: "PROMISE",
            shortName: "ProMISe",
            fullTitle: "Trial of early, goal-directed resuscitation for septic shock",
            year: 2015,
            era: .landmark,
            topic: .sepsis,
            patientPopulation: "Adults with septic shock in emergency care pathways",
            intervention: "Protocolized EGDT",
            comparator: "Usual resuscitation",
            primaryOutcome: "90-day mortality",
            bottomLine: "Like ProCESS and ARISE, ProMISe found no mortality benefit from protocolized EGDT in modern practice.",
            practiceTakeaway: "The sepsis bundle era shifted from rigid invasive targets toward timely antibiotics, fluids, and reassessment.",
            tags: ["EGDT", "sepsis bundle", "emergency care"],
            citations: [
                TrialCitation(
                    id: "PROMISE-primary",
                    title: "Trial of early, goal-directed resuscitation for septic shock",
                    journal: "N Engl J Med",
                    year: 2015,
                    url: pubmed("25776532")
                )
            ]
        ),
        ICUTrial(
            id: "SPLIT",
            shortName: "SPLIT",
            fullTitle: "Effect of a buffered crystalloid solution versus saline on acute kidney injury among patients in the intensive care unit",
            year: 2015,
            era: .recent,
            topic: .fluids,
            patientPopulation: "Predominantly lower-risk ICU adults receiving crystalloid",
            intervention: "Buffered crystalloid",
            comparator: "0.9% saline",
            primaryOutcome: "Acute kidney injury",
            bottomLine: "No significant difference in AKI was seen in this relatively low-risk ICU population.",
            practiceTakeaway: "Fluid strategy evidence depends on illness severity and exposure volume; later larger trials provided additional context.",
            tags: ["buffered crystalloid", "saline", "AKI"],
            citations: [
                TrialCitation(
                    id: "SPLIT-primary",
                    title: "Effect of a buffered crystalloid solution vs saline on acute kidney injury among patients in the intensive care unit",
                    journal: "JAMA",
                    year: 2015,
                    url: pubmed("26444692")
                )
            ]
        ),
        ICUTrial(
            id: "AKIKI",
            shortName: "AKIKI",
            fullTitle: "Initiation strategies for renal-replacement therapy in the intensive care unit",
            year: 2016,
            era: .recent,
            topic: .generalICU,
            patientPopulation: "Adults with severe acute kidney injury in ICU",
            intervention: "Early initiation of renal replacement therapy",
            comparator: "Delayed initiation strategy",
            primaryOutcome: "60-day mortality",
            bottomLine: "Early routine RRT initiation did not improve mortality compared with a delayed strategy.",
            practiceTakeaway: "RRT timing should be individualized using metabolic, volume, and clinical trajectory triggers.",
            tags: ["acute kidney injury", "dialysis timing", "RRT"],
            citations: [
                TrialCitation(
                    id: "AKIKI-primary",
                    title: "Initiation strategies for renal-replacement therapy in the intensive care unit",
                    journal: "N Engl J Med",
                    year: 2016,
                    url: pubmed("27181456")
                )
            ]
        ),
        ICUTrial(
            id: "SUP-ICU",
            shortName: "SUP-ICU",
            fullTitle: "Pantoprazole in patients at risk for gastrointestinal bleeding in the ICU",
            year: 2018,
            era: .recent,
            topic: .generalICU,
            patientPopulation: "Adults in ICU at risk for stress-related GI bleeding",
            intervention: "Pantoprazole prophylaxis",
            comparator: "Placebo",
            primaryOutcome: "90-day mortality",
            bottomLine: "Pantoprazole did not reduce mortality, though clinically important GI bleeding was less frequent.",
            practiceTakeaway: "Stress-ulcer prophylaxis is typically targeted to higher-risk ICU patients rather than universal use.",
            tags: ["stress ulcer prophylaxis", "PPI", "ICU bleeding risk"],
            citations: [
                TrialCitation(
                    id: "SUP-ICU-primary",
                    title: "Pantoprazole in patients at risk for gastrointestinal bleeding in the ICU",
                    journal: "N Engl J Med",
                    year: 2018,
                    url: pubmed("30354950")
                )
            ]
        ),
        ICUTrial(
            id: "STARRT-AKI",
            shortName: "STARRT-AKI",
            fullTitle: "Timing of initiation of renal-replacement therapy in acute kidney injury",
            year: 2020,
            era: .recent,
            topic: .generalICU,
            patientPopulation: "Critically ill adults with severe acute kidney injury",
            intervention: "Accelerated initiation of RRT",
            comparator: "Standard initiation strategy",
            primaryOutcome: "90-day mortality",
            bottomLine: "Accelerated RRT did not improve survival and increased dialysis dependence at 90 days.",
            practiceTakeaway: "A watchful, criteria-driven strategy is often preferred over automatic early dialysis.",
            tags: ["AKI", "dialysis", "RRT timing"],
            citations: [
                TrialCitation(
                    id: "STARRT-AKI-primary",
                    title: "Timing of initiation of renal-replacement therapy in acute kidney injury",
                    journal: "N Engl J Med",
                    year: 2020,
                    url: pubmed("32668114")
                )
            ]
        ),
        ICUTrial(
            id: "REMAP-IL6",
            shortName: "REMAP-CAP IL-6",
            fullTitle: "Interleukin-6 receptor antagonists in critically ill patients with Covid-19",
            year: 2021,
            era: .recent,
            topic: .covid19,
            patientPopulation: "Critically ill adults with COVID-19 receiving organ support",
            intervention: "Tocilizumab or sarilumab",
            comparator: "Standard care",
            primaryOutcome: "Organ support-free days and in-hospital mortality (Bayesian platform outcome)",
            bottomLine: "IL-6 receptor antagonists improved outcomes in critically ill COVID-19 patients in this adaptive platform trial.",
            practiceTakeaway: "This evidence supported immunomodulation for selected ICU COVID-19 phenotypes.",
            tags: ["tocilizumab", "sarilumab", "platform trial"],
            citations: [
                TrialCitation(
                    id: "REMAP-IL6-primary",
                    title: "Interleukin-6 receptor antagonists in critically ill patients with Covid-19",
                    journal: "N Engl J Med",
                    year: 2021,
                    url: pubmed("33631065")
                )
            ]
        ),
        ICUTrial(
            id: "ATTACC-CRIT",
            shortName: "ATTACC/REMAP/ACTIV-4a (ICU)",
            fullTitle: "Therapeutic anticoagulation with heparin in critically ill patients with Covid-19",
            year: 2021,
            era: .recent,
            topic: .covid19,
            patientPopulation: "Critically ill adults with COVID-19",
            intervention: "Therapeutic-dose anticoagulation",
            comparator: "Usual-care pharmacologic thromboprophylaxis",
            primaryOutcome: "Organ support-free days",
            bottomLine: "Therapeutic anticoagulation did not improve organ support-free days in critically ill COVID-19 patients.",
            practiceTakeaway: "In ICU-level COVID-19 illness, routine full-dose anticoagulation is not favored without another indication.",
            tags: ["heparin", "thrombosis", "multiplatform trial"],
            citations: [
                TrialCitation(
                    id: "ATTACC-CRIT-primary",
                    title: "Therapeutic anticoagulation with heparin in critically ill patients with Covid-19",
                    journal: "N Engl J Med",
                    year: 2021,
                    url: pubmed("34351722")
                )
            ]
        ),
        ICUTrial(
            id: "BLING-III",
            shortName: "BLING III",
            fullTitle: "Continuous versus intermittent beta-lactam antibiotic infusions in critically ill patients with sepsis",
            year: 2024,
            era: .recent,
            topic: .sepsis,
            patientPopulation: "Critically ill adults with sepsis receiving beta-lactam therapy",
            intervention: "Continuous beta-lactam infusion",
            comparator: "Intermittent beta-lactam infusion",
            primaryOutcome: "90-day all-cause mortality",
            bottomLine: "Continuous infusion did not significantly reduce 90-day mortality versus intermittent infusion.",
            practiceTakeaway: "Either strategy is acceptable; local protocols and pharmacokinetic goals should guide dosing approach.",
            tags: ["beta-lactam", "antibiotic infusion", "sepsis treatment"],
            citations: [
                TrialCitation(
                    id: "BLING-III-primary",
                    title: "Continuous vs Intermittent beta-Lactam Antibiotic Infusions in Critically Ill Patients With Sepsis",
                    journal: "JAMA",
                    year: 2024,
                    url: pubmed("38864155")
                )
            ]
        ),
        ICUTrial(
            id: "BALANCE",
            shortName: "BALANCE",
            fullTitle: "Antibiotic treatment for 7 versus 14 days in patients with bloodstream infections",
            year: 2024,
            era: .recent,
            topic: .sepsis,
            patientPopulation: "Hospitalized adults, including ICU patients, with bloodstream infection",
            intervention: "7-day antibiotic course",
            comparator: "14-day antibiotic course",
            primaryOutcome: "90-day all-cause mortality",
            bottomLine: "A 7-day strategy was noninferior to 14 days for mortality and reduced antibiotic exposure.",
            practiceTakeaway: "For many bloodstream infections with adequate source control, shorter treatment duration is appropriate.",
            tags: ["bloodstream infection", "antibiotic duration", "short course"],
            citations: [
                TrialCitation(
                    id: "BALANCE-primary",
                    title: "Antibiotic Treatment for 7 versus 14 Days in Patients with Bloodstream Infections",
                    journal: "N Engl J Med",
                    year: 2024,
                    url: pubmed("39021332")
                )
            ]
        ),
        ICUTrial(
            id: "PREOXI",
            shortName: "PREOXI",
            fullTitle: "Noninvasive ventilation for preoxygenation during emergency intubation",
            year: 2024,
            era: .recent,
            topic: .generalICU,
            patientPopulation: "Critically ill adults undergoing emergency tracheal intubation",
            intervention: "Preoxygenation with noninvasive ventilation",
            comparator: "Preoxygenation with an oxygen mask",
            primaryOutcome: "Hypoxemia during intubation (oxygen saturation <85%)",
            bottomLine: "Noninvasive ventilation reduced severe hypoxemia during emergency intubation.",
            practiceTakeaway: "Noninvasive ventilation is a strong default preoxygenation strategy for many high-risk ICU intubations.",
            tags: ["airway management", "intubation", "preoxygenation"],
            citations: [
                TrialCitation(
                    id: "PREOXI-primary",
                    title: "Noninvasive Ventilation for Preoxygenation during Emergency Intubation",
                    journal: "N Engl J Med",
                    year: 2024,
                    url: pubmed("38048190")
                )
            ]
        ),
        ICUTrial(
            id: "REVISE",
            shortName: "REVISE",
            fullTitle: "Stress ulcer prophylaxis in critically ill patients receiving invasive mechanical ventilation",
            year: 2024,
            era: .recent,
            topic: .generalICU,
            patientPopulation: "Mechanically ventilated critically ill adults",
            intervention: "Pantoprazole stress-ulcer prophylaxis",
            comparator: "Placebo",
            primaryOutcome: "90-day in-hospital mortality",
            bottomLine: "Pantoprazole did not improve mortality, while clinically important GI bleeding was less frequent.",
            practiceTakeaway: "Stress-ulcer prophylaxis remains a selective risk-based intervention rather than universal default therapy.",
            tags: ["stress ulcer prophylaxis", "pantoprazole", "mechanical ventilation"],
            citations: [
                TrialCitation(
                    id: "REVISE-primary",
                    title: "Stress Ulcer Prophylaxis in Critically Ill Patients Receiving Invasive Mechanical Ventilation",
                    journal: "N Engl J Med",
                    year: 2024,
                    url: pubmed("38875111")
                )
            ]
        ),
        ICUTrial(
            id: "REVIVAL",
            shortName: "REVIVAL",
            fullTitle: "Recombinant alkaline phosphatase for sepsis-associated acute kidney injury",
            year: 2024,
            era: .recent,
            topic: .sepsis,
            patientPopulation: "Critically ill adults with sepsis-associated acute kidney injury",
            intervention: "Recombinant human alkaline phosphatase",
            comparator: "Placebo",
            primaryOutcome: "Major adverse kidney events at day 90",
            bottomLine: "No statistically significant improvement in the primary kidney outcome was demonstrated.",
            practiceTakeaway: "Routine use of recombinant alkaline phosphatase for sepsis-associated AKI is not yet supported.",
            tags: ["AKI", "sepsis-associated AKI", "renal outcomes"],
            citations: [
                TrialCitation(
                    id: "REVIVAL-primary",
                    title: "Recombinant alkaline phosphatase for sepsis-associated acute kidney injury",
                    journal: "Intensive Care Med",
                    year: 2024,
                    url: pubmed("38204212")
                )
            ]
        ),
        ICUTrial(
            id: "TRAIN",
            shortName: "TRAIN",
            fullTitle: "Restrictive versus liberal transfusion strategy in patients with acute brain injury",
            year: 2024,
            era: .recent,
            topic: .transfusion,
            patientPopulation: "Critically ill adults with acute brain injury and anemia",
            intervention: "Liberal transfusion strategy",
            comparator: "Restrictive transfusion strategy",
            primaryOutcome: "Unfavorable neurologic outcome at 180 days",
            bottomLine: "A liberal strategy lowered the probability of unfavorable neurologic outcome versus restrictive transfusion.",
            practiceTakeaway: "Neurocritical care transfusion thresholds may differ from general ICU restrictive strategies.",
            tags: ["acute brain injury", "hemoglobin threshold", "neurocritical care"],
            citations: [
                TrialCitation(
                    id: "TRAIN-primary",
                    title: "Restrictive vs Liberal Transfusion Strategy in Patients With Acute Brain Injury",
                    journal: "JAMA",
                    year: 2024,
                    url: pubmed("39461563")
                )
            ]
        ),
        ICUTrial(
            id: "ADAPT-SEPSIS",
            shortName: "ADAPT-Sepsis",
            fullTitle: "Biomarker-guided duration of antibiotic treatment in critically ill patients with suspected sepsis",
            year: 2024,
            era: .recent,
            topic: .sepsis,
            patientPopulation: "Critically ill adults with suspected sepsis receiving broad-spectrum antibiotics",
            intervention: "Procalcitonin- or CRP-guided antibiotic discontinuation strategy",
            comparator: "Usual care",
            primaryOutcome: "Antibiotic duration and 28-day mortality",
            bottomLine: "Biomarker guidance modestly reduced antibiotic exposure with similar short-term mortality.",
            practiceTakeaway: "Biomarker-guided stewardship can help shorten antibiotic courses in selected ICU sepsis pathways.",
            tags: ["antibiotic stewardship", "procalcitonin", "CRP"],
            citations: [
                TrialCitation(
                    id: "ADAPT-SEPSIS-primary",
                    title: "Biomarker-Guided Duration of Antibiotic Treatment in Critically Ill Patients With Suspected Sepsis",
                    journal: "JAMA",
                    year: 2024,
                    url: pubmed("39080151")
                )
            ]
        ),
        ICUTrial(
            id: "UK-ROX",
            shortName: "UK-ROX",
            fullTitle: "Conservative oxygen therapy during mechanical ventilation in the intensive care unit",
            year: 2025,
            era: .recent,
            topic: .generalICU,
            patientPopulation: "Adults receiving invasive mechanical ventilation in ICU",
            intervention: "Conservative oxygen therapy",
            comparator: "Usual oxygen therapy",
            primaryOutcome: "Ventilator-free days and mortality outcomes",
            bottomLine: "Conservative oxygen targets did not significantly improve ventilator-free days or mortality.",
            practiceTakeaway: "Avoiding extreme hyperoxia remains sensible, but strict conservative oxygen targets are not clearly superior.",
            tags: ["oxygen therapy", "mechanical ventilation", "critical care"],
            citations: [
                TrialCitation(
                    id: "UK-ROX-primary",
                    title: "Conservative Oxygen Therapy During Mechanical Ventilation in the Intensive Care Unit",
                    journal: "JAMA",
                    year: 2025,
                    url: pubmed("40305744")
                )
            ]
        ),
        ICUTrial(
            id: "ANDROMEDA-SHOCK-2",
            shortName: "ANDROMEDA-SHOCK-2",
            fullTitle: "Personalized blood pressure and perfusion targets in patients with septic shock",
            year: 2025,
            era: .recent,
            topic: .septicShock,
            patientPopulation: "Adults with early septic shock",
            intervention: "Personalized hemodynamic strategy with capillary refill and restrictive fluids",
            comparator: "Usual guideline-based resuscitation",
            primaryOutcome: "Hierarchical composite (mortality, organ support, and length-of-stay domains)",
            bottomLine: "The personalized strategy improved win-ratio outcomes without a clear standalone mortality difference.",
            practiceTakeaway: "Bedside perfusion-guided and individualized shock targets are increasingly supported in septic shock care.",
            tags: ["capillary refill time", "septic shock resuscitation", "hemodynamics"],
            citations: [
                TrialCitation(
                    id: "ANDROMEDA-SHOCK-2-primary",
                    title: "Personalized Blood Pressure and Perfusion Targets in Patients with Septic Shock",
                    journal: "JAMA",
                    year: 2025,
                    url: pubmed("40679120")
                )
            ]
        ),
        ICUTrial(
            id: "LIBERATE-D",
            shortName: "LIBERATE-D",
            fullTitle: "Conservative vs liberal kidney replacement therapy strategy among critically ill adults with dialysis-requiring acute kidney injury",
            year: 2025,
            era: .recent,
            topic: .generalICU,
            patientPopulation: "Critically ill adults with dialysis-requiring acute kidney injury",
            intervention: "Conservative kidney replacement strategy",
            comparator: "Liberal kidney replacement strategy",
            primaryOutcome: "90-day all-cause mortality",
            bottomLine: "A conservative strategy did not significantly reduce 90-day mortality compared with a liberal approach.",
            practiceTakeaway: "Dialysis strategy should remain individualized; mortality benefit from conservative-first approaches is unproven.",
            tags: ["AKI", "dialysis-requiring AKI", "kidney replacement therapy"],
            citations: [
                TrialCitation(
                    id: "LIBERATE-D-primary",
                    title: "Conservative vs Liberal Kidney Replacement Therapy Strategy Among Critically Ill Adults With Dialysis-Requiring Acute Kidney Injury",
                    journal: "JAMA",
                    year: 2025,
                    url: pubmed("40734001")
                )
            ]
        ),
        ICUTrial(
            id: "BICARICU-2",
            shortName: "BICARICU-2",
            fullTitle: "Sodium bicarbonate for severe metabolic acidemia and acute kidney injury in critically ill patients",
            year: 2025,
            era: .recent,
            topic: .generalICU,
            patientPopulation: "Critically ill adults with severe metabolic acidemia and acute kidney injury",
            intervention: "Sodium bicarbonate infusion strategy",
            comparator: "Usual care without systematic bicarbonate infusion",
            primaryOutcome: "90-day all-cause mortality",
            bottomLine: "Sodium bicarbonate did not significantly reduce 90-day mortality in the overall trial population.",
            practiceTakeaway: "Bicarbonate may be considered selectively, but routine use for all severe acidemia with AKI is not clearly beneficial.",
            tags: ["metabolic acidosis", "AKI", "bicarbonate therapy"],
            citations: [
                TrialCitation(
                    id: "BICARICU-2-primary",
                    title: "Sodium Bicarbonate for Severe Metabolic Acidemia and Acute Kidney Injury in Critically Ill Patients",
                    journal: "JAMA",
                    year: 2025,
                    url: pubmed("40656748")
                )
            ]
        )
    ]
}
