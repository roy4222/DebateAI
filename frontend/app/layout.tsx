import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";
import { ThemeProvider } from "@/components/theme-provider";
import { I18nProvider } from "@/lib/i18n";
import { DebateHistoryProvider } from "@/contexts/DebateHistoryContext";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "DebateAI - Multi-Agent 即時辯論平台",
  description: "讓 AI 辯手針對各種議題進行深度辯論",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-TW" suppressHydrationWarning>
      <head>
        {/*
          立即執行腳本以避免 lang 屬性閃爍
          注意：靜態導出限制 - SSR HTML 永遠是 lang="zh-TW"
          此腳本僅在客戶端執行後生效，SEO/無 JS 環境會看到中文 lang
        */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var locale = localStorage.getItem('debateai-locale');
                  if (locale === 'en') {
                    document.documentElement.lang = 'en';
                  } else {
                    document.documentElement.lang = 'zh-TW';
                  }
                } catch (e) {}
              })();
            `,
          }}
        />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <I18nProvider>
          <ThemeProvider
            attribute="class"
            defaultTheme="dark"
            enableSystem
            disableTransitionOnChange
          >
            <DebateHistoryProvider>
              <SidebarProvider>
                <AppSidebar />
                <main className="flex-1 flex flex-col min-h-screen w-full">
                  {/* Sidebar Trigger for mobile */}
                  <div className="md:hidden p-2 border-b border-slate-800/50">
                    <SidebarTrigger />
                  </div>
                  {children}
                </main>
              </SidebarProvider>
            </DebateHistoryProvider>
          </ThemeProvider>
        </I18nProvider>
      </body>
    </html>
  );
}
