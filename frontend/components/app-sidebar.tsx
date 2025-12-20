"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Swords, Info, CreditCard, Settings, Home } from "lucide-react";
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

// 導航項目
const menuItems = [
  {
    title: "辯論",
    url: "/",
    icon: Swords,
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

export function AppSidebar() {
  const pathname = usePathname();

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
      </SidebarContent>

      {/* Sidebar Footer */}
      <SidebarFooter className="border-t border-slate-800/50 p-4">
        <p className="text-xs text-slate-500 text-center">v0.3.4 • Phase 3d</p>
      </SidebarFooter>
    </Sidebar>
  );
}
