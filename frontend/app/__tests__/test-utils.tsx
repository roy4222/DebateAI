/**
 * Test Utilities
 *
 * 提供測試用的 wrapper 和輔助函數
 */

import React from 'react'
import { render } from '@testing-library/react'
import { I18nProvider } from '@/lib/i18n'

/**
 * 自定義 render 函數，自動包裝必要的 Provider
 */
export function renderWithProviders(
  ui: React.ReactElement,
  options = {}
) {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <I18nProvider>
        {children}
      </I18nProvider>
    )
  }

  return render(ui, { wrapper: Wrapper, ...options })
}

// Re-export everything from testing library
export * from '@testing-library/react'
export { renderWithProviders as render }
