"use client";

import { useEffect, useRef } from "react";
import { suggestTeluguName } from "@/features/master-data/transliterate-api";

/**
 * Suggest Telugu name from English when the Telugu field is still empty.
 * Does not overwrite after the user edits Telugu manually.
 */
export function useAutoTeluguName(
  english: string,
  telugu: string,
  setTelugu: (value: string) => void,
) {
  const userEditedTe = useRef(false);

  useEffect(() => {
    if (userEditedTe.current) return;
    const trimmed = english.trim();
    if (trimmed.length < 2) {
      if (!telugu) setTelugu("");
      return;
    }

    const handle = window.setTimeout(() => {
      void suggestTeluguName(trimmed)
        .then((suggested) => {
          if (!userEditedTe.current && suggested) setTelugu(suggested);
        })
        .catch(() => {
          /* optional API — ignore failures */
        });
    }, 450);

    return () => window.clearTimeout(handle);
  }, [english, telugu, setTelugu]);

  const onTeluguChange = (value: string) => {
    if (value.trim()) userEditedTe.current = true;
    setTelugu(value);
  };

  const resetTeluguEditFlag = () => {
    userEditedTe.current = false;
  };

  return { onTeluguChange, resetTeluguEditFlag };
}
