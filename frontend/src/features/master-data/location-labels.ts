/** Location field labels — bilingual when locale is Telugu (no i18n message catalogs yet). */

export type LocationLocale = "en" | "te" | string;

export function locationLabels(locale: LocationLocale = "en") {
  if (locale === "te") {
    return {
      district: "జిల్లా (District)",
      mandal: "మండలం (Mandal)",
      village: "గ్రామం (Village)",
      selectDistrict: "జిల్లా ఎంచుకోండి…",
      selectMandal: "మండలం ఎంచుకోండి…",
      selectVillage: "గ్రామం ఎంచుకోండి…",
    };
  }
  return {
    district: "District",
    mandal: "Mandal",
    village: "Village",
    selectDistrict: "Search district…",
    selectMandal: "Search mandal…",
    selectVillage: "Search village…",
  };
}
