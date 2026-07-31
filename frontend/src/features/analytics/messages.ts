/** Bilingual chrome keys for Analytics Hub (inline; no next-intl yet). */

export const analyticsMessages = {
  en: {
    hubTitle: "Analytics Hub",
    hubDescription: "Executive command center for live ops and finance — honest empty states where data is missing.",
    filters: "Filters",
    preset: "Date range",
    today: "Today",
    yesterday: "Yesterday",
    thisWeek: "This week",
    thisMonth: "This month",
    pickDay: "Pick a day",
    d7: "7 days",
    d30: "30 days",
    season: "Season",
    custom: "Custom",
    exportCsv: "Export CSV",
    saveView: "Save view",
    savedViews: "Saved views",
    live: "Live",
    scaffold: "Coming soon",
    dataAvailability: "Data availability",
    healthScore: "Health score",
    cacheHit: "Cached",
    topTables: "Rankings",
    noData: "No data in this range",
    reportsRedirect: "Reports have moved into Analytics Hub.",
  },
  te: {
    hubTitle: "విశ్లేషణ కేంద్రం",
    hubDescription: "ప్రత్యక్ష కార్యకలాపాలు మరియు ఫైనాన్స్ కోసం ఎగ్జిక్యూటివ్ కమాండ్ — డేటా లేనిచోట నిజాయితీగా ఖాళీ స్థితులు.",
    filters: "ఫిల్టర్లు",
    preset: "తేదీ పరిధి",
    today: "ఈరోజు",
    yesterday: "నిన్న",
    thisWeek: "ఈ వారం",
    thisMonth: "ఈ నెల",
    pickDay: "రోజు ఎంచుకోండి",
    d7: "7 రోజులు",
    d30: "30 రోజులు",
    season: "సీజన్",
    custom: "కస్టమ్",
    exportCsv: "CSV ఎగుమతి",
    saveView: "వీక్షణ సేవ్",
    savedViews: "సేవ్ చేసిన వీక్షణలు",
    live: "లైవ్",
    scaffold: "త్వరలో",
    dataAvailability: "డేటా లభ్యత",
    healthScore: "ఆరోగ్య స్కోరు",
    cacheHit: "కాష్",
    topTables: "ర్యాంకింగ్స్",
    noData: "ఈ పరిధిలో డేటా లేదు",
    reportsRedirect: "రిపోర్టులు ఇప్పుడు విశ్లేషణ కేంద్రంలో ఉన్నాయి.",
  },
} as const;

export type AnalyticsLocale = keyof typeof analyticsMessages;

export function tAnalytics(locale: AnalyticsLocale, key: keyof (typeof analyticsMessages)["en"]): string {
  return analyticsMessages[locale][key] ?? analyticsMessages.en[key];
}
