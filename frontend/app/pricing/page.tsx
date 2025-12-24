"use client";

import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useI18n } from "@/lib/i18n";

export default function PricingPage() {
  const { t, locale } = useI18n();

  return (
    <div className="flex-1 bg-gradient-to-br from-slate-100 via-slate-50 to-white dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-3">
          💰 {locale === "en" ? "Pricing Plans" : "價格方案"}
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mb-6">
          {locale === "en"
            ? "DebateAI offers flexible plans from free trial to enterprise integration. Choose the plan that fits your team's needs."
            : "DebateAI 提供靈活的方案，從免費試用到企業級整合。選擇最符合您團隊需求的方案，或聯絡我們定制。"}
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          {/* Free */}
          <Card className="flex flex-col h-full bg-white/60 dark:bg-slate-800/40 border-slate-200 dark:border-slate-700/50">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-slate-900 dark:text-white">
                  {locale === "en" ? "Free" : "免費"}
                </CardTitle>
                <Badge variant="outline">
                  {locale === "en" ? "Starter" : "入門"}
                </Badge>
              </div>
              <CardDescription>
                {locale === "en"
                  ? "Quick start, no credit card needed"
                  : "快速上手、無需信用卡"}
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1">
              <div className="text-3xl font-bold text-slate-900 dark:text-white mb-4">
                $0{" "}
                <span className="text-sm text-slate-500 dark:text-slate-400">
                  / {locale === "en" ? "forever" : "永久"}
                </span>
              </div>
              <ul className="text-sm text-slate-600 dark:text-slate-300 space-y-2">
                <li>
                  {locale === "en"
                    ? "5 public debates per month"
                    : "每月 5 次公開辯論"}
                </li>
                <li>
                  {locale === "en"
                    ? "Basic multi-agent templates"
                    : "基本多代理人設定模板"}
                </li>
                <li>{locale === "en" ? "Community support" : "社群支援"}</li>
              </ul>
            </CardContent>
            <CardFooter>
              <Button asChild className="w-full">
                <Link href="/">
                  {locale === "en" ? "Start Free" : "開始使用（免費）"}
                </Link>
              </Button>
            </CardFooter>
          </Card>

          {/* Pro */}
          <Card className="flex flex-col h-full bg-white/60 dark:bg-slate-800/40 border-slate-200 dark:border-slate-700/50">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-slate-900 dark:text-white">
                  Pro
                </CardTitle>
                <Badge variant="outline">
                  {locale === "en" ? "Popular" : "熱門"}
                </Badge>
              </div>
              <CardDescription className="text-center">
                {locale === "en"
                  ? "For advanced users & small teams"
                  : "適合進階使用者與小型團隊"}
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1">
              <div className="text-3xl font-bold text-slate-900 dark:text-white mb-4">
                $19{" "}
                <span className="text-sm text-slate-500 dark:text-slate-400">
                  / {locale === "en" ? "month" : "月"}
                </span>
              </div>
              <ul className="text-sm text-slate-600 dark:text-slate-300 space-y-2">
                <li>
                  {locale === "en"
                    ? "200 debates per month"
                    : "每月 200 次辯論"}
                </li>
                <li>
                  {locale === "en"
                    ? "Custom agent & role settings"
                    : "自訂代理人與角色設定"}
                </li>
                <li>
                  {locale === "en" ? "API priority quota" : "API 優先配額"}
                </li>
                <li>{locale === "en" ? "Email support" : "電郵支援"}</li>
              </ul>
            </CardContent>
            <CardFooter>
              <Button className="w-full">
                {locale === "en" ? "Upgrade Now" : "立即升級"}
              </Button>
            </CardFooter>
          </Card>

          {/* Enterprise */}
          <Card className="flex flex-col h-full bg-white/60 dark:bg-slate-800/40 border-slate-200 dark:border-slate-700/50">
            <CardHeader>
              <CardTitle className="text-slate-900 dark:text-white">
                {locale === "en" ? "Enterprise" : "企業"}
              </CardTitle>
              <CardDescription>
                {locale === "en"
                  ? "Flexible pricing & enterprise integration"
                  : "彈性計價與企業整合"}
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1">
              <div className="text-3xl font-bold text-slate-900 dark:text-white mb-4">
                $100{" "}
                <span className="text-sm text-slate-500 dark:text-slate-400">
                  USD/{locale === "en" ? "month" : "月"}
                </span>
              </div>
              <ul className="text-sm text-slate-600 dark:text-slate-300 space-y-2">
                <li>
                  {locale === "en"
                    ? "Unlimited usage & deployment options"
                    : "無上限的使用與佈署選項"}
                </li>
                <li>
                  {locale === "en"
                    ? "SAML / SSO & enterprise security"
                    : "SAML / SSO 與企業級安全性"}
                </li>
                <li>
                  {locale === "en"
                    ? "Dedicated account manager & SLA"
                    : "專屬客戶經理與 SLA 支援"}
                </li>
              </ul>
            </CardContent>
            <CardFooter>
              <Button variant="outline" className="w-full" asChild>
                <Link href="mailto:sales@example.com">
                  {locale === "en" ? "Contact Us" : "聯絡我們"}
                </Link>
              </Button>
            </CardFooter>
          </Card>
        </div>

        <div className="mt-6 text-sm text-slate-500 dark:text-slate-400">
          <p>
            💡{" "}
            {locale === "en"
              ? "All prices are examples; actual pricing and features subject to official announcement."
              : "所有價格為範例；實際計價與功能以正式公告為準。"}
          </p>
          <p className="mt-2">
            {locale === "en"
              ? "Need team discounts or budget integration? Contact us at sales@example.com"
              : "需要團隊折扣或預算內整合？請透過 sales@example.com 聯絡我們。"}
          </p>
        </div>
      </div>
    </div>
  );
}
