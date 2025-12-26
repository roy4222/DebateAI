import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const response = NextResponse.next();

  // 從 cookie 讀取語言設定（如果有的話）
  const savedLocale = request.cookies.get('debate-language')?.value;

  // 設定 response header，讓 layout 可以讀取
  if (savedLocale === 'en' || savedLocale === 'zh') {
    response.headers.set('x-user-locale', savedLocale);
  }

  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
