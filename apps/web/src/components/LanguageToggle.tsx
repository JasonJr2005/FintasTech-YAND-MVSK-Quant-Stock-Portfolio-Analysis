"use client";

import type { Language } from "@/lib/i18n";

type LanguageToggleProps = {
  language: Language;
  onChange: (language: Language) => void;
};

export function LanguageToggle({ language, onChange }: LanguageToggleProps) {
  return (
    <div className="flex rounded-full border border-white/15 bg-white/[0.04] p-1 text-sm">
      <button
        className={language === "en" ? activeClass : inactiveClass}
        type="button"
        onClick={() => onChange("en")}
      >
        EN
      </button>
      <button
        className={language === "zh" ? activeClass : inactiveClass}
        type="button"
        onClick={() => onChange("zh")}
      >
        中文
      </button>
    </div>
  );
}

const activeClass = "rounded-full bg-mint px-3 py-1.5 font-semibold text-ink transition";
const inactiveClass = "rounded-full px-3 py-1.5 text-white/60 transition hover:text-white";
