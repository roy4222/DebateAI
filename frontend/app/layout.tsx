import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";
import { Providers } from "@/components/Providers";

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
    <html lang="zh-TW" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-slate-950`}
      >
        <Providers>
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
        </Providers>
      </body>
    </html>
  );
}
