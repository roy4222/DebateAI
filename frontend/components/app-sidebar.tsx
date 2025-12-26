"use client";

import { useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Swords,
  Info,
  CreditCard,
  Settings,
  History,
  Clock,
  ArrowRight,
} from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarFooter,
} from "@/components/ui/sidebar";
import { getRecentDebates } from "@/app/lib/api";
import { useDebateHistory } from "@/contexts/DebateHistoryContext";

// 導航項目
const menuItems = [
  {
    title: "辯論",
    url: "/",
    icon: Swords,
  },
  {
    title: "歷史紀錄",
    url: "/history",
    icon: History,
  },
  {
    title: "關於我們",
    url: "/about",
    icon: Info,
  },
  {
    title: "價格方案",
    url: "/pricing",
    icon: CreditCard,
  },
  {
    title: "設定",
    url: "/settings",
    icon: Settings,
  },
];

// 格式化相對時間
function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMins < 1) return "剛剛";
  if (diffMins < 60) return `${diffMins} 分鐘前`;
  if (diffHours < 24) return `${diffHours} 小時前`;
  if (diffDays < 7) return `${diffDays} 天前`;
  return date.toLocaleDateString("zh-TW");
}

export function AppSidebar() {
  const pathname = usePathname();
  const { recentDebates, setRecentDebates } = useDebateHistory();

  // 初次載入時取得最近辯論
  useEffect(() => {
    const fetchRecent = async () => {
      try {
        const debates = await getRecentDebates(5);
        setRecentDebates(debates);
      } catch (error) {
        console.error("Failed to fetch recent debates:", error);
      }
    };

    fetchRecent();
  }, [setRecentDebates]);

  return (
    <Sidebar className="border-r border-slate-800/50">
      {/* Sidebar Header */}
      <SidebarHeader className="border-b border-slate-800/50 p-4">
        <Link
          href="/"
          className="flex items-center gap-3 hover:opacity-80 transition-opacity"
        >
          <div className="p-2 rounded-lg bg-gradient-to-br from-purple-600 to-blue-600">
            <Swords className="size-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold bg-gradient-to-r from-purple-400 via-pink-500 to-blue-400 bg-clip-text text-transparent">
              DebateAI
            </h1>
            <p className="text-xs text-slate-500">Multi-Agent 辯論平台</p>
          </div>
        </Link>
      </SidebarHeader>

      {/* Sidebar Content */}
      <SidebarContent>
        {/* 導覽區 */}
        <SidebarGroup>
          <SidebarGroupLabel className="text-slate-400">導覽</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname === item.url}
                    className="hover:bg-slate-800/50"
                  >
                    <Link href={item.url}>
                      <item.icon className="size-4" />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* 最近辯論區 (Google AI Studio 風格) */}
        <SidebarGroup className="mt-2">
          <SidebarGroupLabel className="text-slate-400 flex items-center gap-2">
            <Clock className="size-3" />
            最近辯論
          </SidebarGroupLabel>
          <SidebarGroupContent>
            {recentDebates.length === 0 ? (
              <p className="text-xs text-slate-500 px-3 py-2">尚無辯論記錄</p>
            ) : (
              <SidebarMenu>
                {recentDebates.map((debate) => (
                  <SidebarMenuItem key={debate.id}>
                    <SidebarMenuButton
                      asChild
                      isActive={
                        pathname === "/history" &&
                        (typeof window !== "undefined"
                          ? new URLSearchParams(window.location.search).get(
                              "id"
                            ) === debate.id
                          : false)
                      }
                      className="hover:bg-slate-800/50"
                    >
                      <Link href={`/history?id=${debate.id}`}>
                        <div className="flex flex-col items-start w-full min-w-0">
                          <span className="text-sm truncate w-full">
                            {debate.topic.length > 25
                              ? debate.topic.slice(0, 25) + "..."
                              : debate.topic}
                          </span>
                          <span className="text-xs text-slate-500">
                            {formatRelativeTime(debate.created_at)} •{" "}
                            {debate.rounds_completed} 輪
                          </span>
                        </div>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}

                {/* 查看所有紀錄連結 */}
                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    className="hover:bg-slate-800/50 text-purple-400 hover:text-purple-300"
                  >
                    <Link href="/history" className="flex items-center gap-1">
                      <span>查看所有紀錄</span>
                      <ArrowRight className="size-3" />
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              </SidebarMenu>
            )}
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      {/* Sidebar Footer */}
      <SidebarFooter className="border-t border-slate-800/50 p-4">
        <p className="text-xs text-slate-500 text-center">v0.4.0 • Phase 4</p>
      </SidebarFooter>
    </Sidebar>
  );
}
