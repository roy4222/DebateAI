"use client";

import { useTheme } from "next-themes";
import { Sun, Moon, Monitor, Globe } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";
import { useI18n } from "@/lib/i18n";

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const { locale, setLocale, t } = useI18n();
  const [mounted, setMounted] = useState(false);

  // 避免 hydration 不匹配
  useEffect(() => {
    setMounted(true);
  }, []);

  const themeOptions = [
    { value: "light", labelKey: "themeLight" as const, icon: Sun },
    { value: "dark", labelKey: "themeDark" as const, icon: Moon },
    { value: "system", labelKey: "themeSystem" as const, icon: Monitor },
  ];

  const languageOptions = [
    { value: "zh" as const, labelKey: "languageChinese" as const },
    { value: "en" as const, labelKey: "languageEnglish" as const },
  ];

  return (
    <div className="flex-1 bg-gradient-to-br from-slate-100 via-slate-50 to-white dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 p-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-6">{t("settings")}</h1>
        <div className="bg-white/60 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700/50 rounded-lg p-6 space-y-6 shadow-sm">
          <p className="text-slate-700 dark:text-slate-300">
            {t("settingsDescription")} <strong className="text-slate-900 dark:text-white">DebateAI</strong>{" "}
            {t("preferenceSuffix")}
          </p>

          {/* 主題設定區塊 */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
              {t("themeTitle")}
            </h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {t("themeDescription")}
            </p>

            <div className="flex flex-wrap gap-3">
              {themeOptions.map((option) => {
                const Icon = option.icon;
                const isActive = mounted && theme === option.value;

                return (
                  <Button
                    key={option.value}
                    variant={isActive ? "default" : "outline"}
                    onClick={() => setTheme(option.value)}
                    className={`flex items-center gap-2 min-w-[100px] transition-all ${
                      isActive
                        ? "bg-purple-600 hover:bg-purple-700 text-white border-purple-500"
                        : "hover:bg-slate-100 dark:hover:bg-slate-700/50"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {t(option.labelKey)}
                  </Button>
                );
              })}
            </div>

            {mounted && (
              <p className="text-xs text-slate-500 dark:text-slate-500 mt-2">
                {t("currentTheme")}{themeOptions.find((o) => o.value === theme)?.labelKey ? t(themeOptions.find((o) => o.value === theme)!.labelKey) : t("themeUnknown")}
              </p>
            )}
          </div>

          <hr className="border-slate-200 dark:border-slate-700/50" />

          {/* 語言設定區塊 */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
              {t("languageTitle")}
            </h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {t("languageDescription")}
            </p>

            <div className="flex flex-wrap gap-3">
              {languageOptions.map((option) => {
                const isActive = mounted && locale === option.value;

                return (
                  <Button
                    key={option.value}
                    variant={isActive ? "default" : "outline"}
                    onClick={() => setLocale(option.value)}
                    className={`flex items-center gap-2 min-w-[100px] transition-all ${
                      isActive
                        ? "bg-blue-600 hover:bg-blue-700 text-white border-blue-500"
                        : "hover:bg-slate-100 dark:hover:bg-slate-700/50"
                    }`}
                  >
                    <Globe className="w-4 h-4" />
                    {t(option.labelKey)}
                  </Button>
                );
              })}
            </div>

            {mounted && (
              <p className="text-xs text-slate-500 dark:text-slate-500 mt-2">
                {t("currentLanguage")}{t(languageOptions.find((o) => o.value === locale)?.labelKey || "languageChinese")}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
