import { fetchApi } from "@/lib/api/client";

export async function suggestTeluguName(text: string): Promise<string> {
  const q = encodeURIComponent(text.trim());
  if (q.length < 2) return "";
  const data = await fetchApi<{ text: string; locale: string }>(
    `/utils/transliterate?text=${q}&target=te`,
    { method: "GET", clientHeaders: false },
  );
  return data.text ?? "";
}
