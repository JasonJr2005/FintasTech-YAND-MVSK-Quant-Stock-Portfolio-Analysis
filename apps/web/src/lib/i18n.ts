"use client";

import { useEffect, useState } from "react";

export type Language = "en" | "zh";

const STORAGE_KEY = "fintastech-language";

export function useLanguage() {
  const [language, setLanguageState] = useState<Language>("en");

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored === "zh" || stored === "en") {
      setLanguageState(stored);
    }
  }, []);

  function setLanguage(next: Language) {
    setLanguageState(next);
    window.localStorage.setItem(STORAGE_KEY, next);
  }

  return { language, setLanguage };
}

export function formatPercent(value: number, language: Language) {
  return new Intl.NumberFormat(language === "zh" ? "zh-CN" : "en-US", {
    style: "percent",
    maximumFractionDigits: 1
  }).format(value);
}
