"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";

export type Locale = "zh" | "en";

// 翻譯內容定義
const translations = {
  zh: {
    // Settings page
    settings: "⚙️ 設定",
    settingsDescription: "在此調整您的",
    preferenceSuffix: "偏好設定。",
    
    // Theme
    themeTitle: "🎨 外觀主題",
    themeDescription: "選擇您偏好的顯示模式",
    themeLight: "淺色",
    themeDark: "深色",
    themeSystem: "系統",
    currentTheme: "目前主題：",
    themeUnknown: "未知",
    
    // Language
    languageTitle: "🌐 語言設定",
    languageDescription: "選擇介面顯示語言",
    languageChinese: "中文",
    languageEnglish: "English",
    currentLanguage: "目前語言：",
    
    // Common
    moreSettingsComingSoon: "更多設定功能開發中...",
    pageInDevelopment: "此頁面正在開發中...",
    
    // Sidebar
    sidebarNav: "導覽",
    sidebarSubtitle: "Multi-Agent 辯論平台",
    navDebate: "辯論",
    navAbout: "關於我們",
    navPricing: "價格方案",
    navSettings: "設定",
    
    // About page
    aboutTitle: "ℹ️ 關於我們",
    aboutDescription: "是一個 Multi-Agent 即時辯論平台，讓 AI 辯手針對各種議題進行深度辯論。",
    
    // Pricing page
    pricingTitle: "💰 價格方案",
    pricingDescription: "提供免費使用！",
    pricingCurrently: "目前",
    
    // Debate UI
    debateWelcomeTitle: "準備好開始一場精彩的辯論了嗎？",
    debateWelcomeDescription: "輸入一個主題，觀看 AI 樂觀者與懷疑者展開激烈交鋒。每個論點都會即時串流顯示。",
    debateTopic: "🎯 辯論主題：",
    debateDefaultTopic: "AI 會取代大部分人類工作嗎？",
    debateConnecting: "⚡ 正在連接 AI 辯論引擎...",
    debateTimeout: "❌ 連接超時，引擎可能正在冷啟動，請重試",
    debateConnectionFailed: "❌ 連接失敗：",
    debateStopped: "🛑 辯論已停止",
    debateError: "❌ 錯誤：",
    debateConnectionTime: "連線耗時：",
    debateSearching: "🔍 正在搜尋資料...",
    debateSearchComplete: "✅ 搜尋完成，繼續辯論...",
    debateOptimistSearching: "樂觀者",
    debateSkepticSearching: "懷疑者",
    debateSearchFor: "正在搜尋：",
    
    // Topic Form
    topicPlaceholder: "輸入辯論主題，例如：AI 會取代人類工作嗎？",
    topicStop: "停止",
    topicStart: "開始辯論",
    topicPoweredBy: "Powered by",
    topicTestVersion: "• Phase 1 測試版",
    
    // Message Bubble
    roleOptimist: "樂觀者",
    roleSkeptic: "懷疑者",
    roleModerator: "主持人",
    roleSystem: "系統",
    isTyping: "正在輸入...",
  },
  en: {
    // Settings page
    settings: "⚙️ Settings",
    settingsDescription: "Adjust your",
    preferenceSuffix: "preferences here.",
    
    // Theme
    themeTitle: "🎨 Appearance",
    themeDescription: "Choose your preferred display mode",
    themeLight: "Light",
    themeDark: "Dark",
    themeSystem: "System",
    currentTheme: "Current theme: ",
    themeUnknown: "Unknown",
    
    // Language
    languageTitle: "🌐 Language",
    languageDescription: "Choose interface language",
    languageChinese: "中文",
    languageEnglish: "English",
    currentLanguage: "Current language: ",
    
    // Common
    moreSettingsComingSoon: "More settings coming soon...",
    pageInDevelopment: "This page is under development...",
    
    // Sidebar
    sidebarNav: "Navigation",
    sidebarSubtitle: "Multi-Agent Debate Platform",
    navDebate: "Debate",
    navAbout: "About",
    navPricing: "Pricing",
    navSettings: "Settings",
    
    // About page
    aboutTitle: "ℹ️ About Us",
    aboutDescription: "is a Multi-Agent real-time debate platform where AI debaters engage in in-depth debates on various topics.",
    
    // Pricing page
    pricingTitle: "💰 Pricing",
    pricingDescription: "is free to use!",
    pricingCurrently: "Currently,",
    
    // Debate UI
    debateWelcomeTitle: "Ready to start an exciting debate?",
    debateWelcomeDescription: "Enter a topic and watch AI optimist and skeptic engage in a heated debate. Each argument will be streamed in real-time.",
    debateTopic: "🎯 Debate Topic: ",
    debateDefaultTopic: "Will AI replace most human jobs?",
    debateConnecting: "⚡ Connecting to AI Debate Engine...",
    debateTimeout: "❌ Connection timed out. Engine may be cold-starting, please retry.",
    debateConnectionFailed: "❌ Connection failed: ",
    debateStopped: "🛑 Debate stopped",
    debateError: "❌ Error: ",
    debateConnectionTime: "Connection time: ",
    debateSearching: "🔍 Searching for data...",
    debateSearchComplete: "✅ Search complete, continuing debate...",
    debateOptimistSearching: "Optimist",
    debateSkepticSearching: "Skeptic",
    debateSearchFor: "is searching: ",
    
    // Topic Form
    topicPlaceholder: "Enter debate topic, e.g.: Will AI replace human jobs?",
    topicStop: "Stop",
    topicStart: "Start Debate",
    topicPoweredBy: "Powered by",
    topicTestVersion: "• Phase 1 Test Version",
    
    // Message Bubble
    roleOptimist: "Optimist",
    roleSkeptic: "Skeptic",
    roleModerator: "Moderator",
    roleSystem: "System",
    isTyping: "Typing...",
  },
} as const;

type TranslationKey = keyof typeof translations.zh;

interface I18nContextType {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: TranslationKey) => string;
}

const I18nContext = createContext<I18nContextType | undefined>(undefined);

const STORAGE_KEY = "debateai-locale";

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("zh");

  useEffect(() => {
    // 從 localStorage 讀取儲存的語言設定
    const savedLocale = localStorage.getItem(STORAGE_KEY) as Locale | null;
    if (savedLocale && (savedLocale === "zh" || savedLocale === "en")) {
      setLocaleState(savedLocale);
    }
  }, []);

  const setLocale = (newLocale: Locale) => {
    setLocaleState(newLocale);
    localStorage.setItem(STORAGE_KEY, newLocale);
    // 更新 html lang 屬性
    document.documentElement.lang = newLocale === "zh" ? "zh-TW" : "en";
  };

  const t = (key: TranslationKey): string => {
    return translations[locale][key] || key;
  };

  return (
    <I18nContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (context === undefined) {
    throw new Error("useI18n must be used within an I18nProvider");
  }
  return context;
}
