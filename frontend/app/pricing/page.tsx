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

export default function PricingPage() {
  return (
    <div className="flex-1 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-3">💰 價格方案</h1>
        <p className="text-slate-400 mb-6">
          DebateAI 提供靈活的方案，從免費試用到企業級整合。選擇最符合您團隊需求的方案，或聯絡我們定制。
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          {/* Free */}
          <Card className="flex flex-col h-full">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>免費</CardTitle>
                <Badge variant="outline">入門</Badge>
              </div>
              <CardDescription>快速上手、無需信用卡</CardDescription>
            </CardHeader>
            <CardContent className="flex-1">
              <div className="text-3xl font-bold text-white mb-4">$0 <span className="text-sm text-slate-400">/ 永久</span></div>
              <ul className="text-sm text-slate-300 space-y-2">
                <li>每月 5 次公開辯論</li>
                <li>基本多代理人設定模板</li>
                <li>社群支援</li>
              </ul>
            </CardContent>
            <CardFooter>
              <Button asChild className="w-full">
                <Link href="/">開始使用（免費）</Link>
              </Button>
            </CardFooter>
          </Card>

          {/* Pro */}
          <Card className="flex flex-col h-full">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Pro</CardTitle>
                <Badge variant="outline">熱門</Badge>
              </div>
              <CardDescription className="text-center">適合進階使用者與小型團隊</CardDescription>
            </CardHeader>
            <CardContent className="flex-1">
              <div className="text-3xl font-bold text-white mb-4">$19 <span className="text-sm text-slate-400">/ 月</span></div>
              <ul className="text-sm text-slate-300 space-y-2">
                <li>每月 200 次辯論</li>
                <li>自訂代理人與角色設定</li>
                <li>API 優先配額</li>
                <li>電郵支援</li>
              </ul>
            </CardContent>
            <CardFooter>
              <Button className="w-full">立即升級</Button>
            </CardFooter>
          </Card>

          {/* Enterprise */}
          <Card className="flex flex-col h-full">
            <CardHeader>
              <CardTitle>企業</CardTitle>
              <CardDescription>彈性計價與企業整合</CardDescription>
            </CardHeader>
            <CardContent className="flex-1">
              <div className="text-3xl font-bold text-white mb-4">$100 USD/month</div>
              <ul className="text-sm text-slate-300 space-y-2">
                <li>無上限的使用與佈署選項</li>
                <li>SAML / SSO 與企業級安全性</li>
                <li>專屬客戶經理與 SLA 支援</li>
              </ul>
            </CardContent>
            <CardFooter>
              <Button variant="outline" className="w-full" asChild>
                <Link href="mailto:sales@example.com">聯絡我們</Link>
              </Button>
            </CardFooter>
          </Card>
        </div>

        <div className="mt-6 text-sm text-slate-400">
          <p>💡 所有價格為範例；實際計價與功能以正式公告為準。</p>
          <p className="mt-2">需要團隊折扣或預算內整合？請透過 sales@example.com 聯絡我們。</p>
        </div>
      </div>
    </div>
  );
}
