import { computed } from 'vue';
import type { GlobalThemeOverrides } from 'naive-ui';
import { themeMode } from '@/composables/useTheme';

// Brand palette
export const brand = {
  primary: '#4F46E5',       // 深靛蓝 — 主色
  primaryHover: '#4338CA',
  primaryPressed: '#3730A3',
  secondary: '#F472B6',     // soft pink — 甜蜜辅色
  accent: '#fbbf24',        // warm gold — 点缀
  success: '#86efac',
  warning: '#fcd34d',
  error: '#fca5a5',
  info: '#93c5fd',
  bg: '#0f0a1a',            // deep dark purple-black
  bgCard: 'rgba(139, 92, 246, 0.06)',
  bgCardHover: 'rgba(139, 92, 246, 0.12)',
  text: '#f1f5f9',
  textSecondary: '#a78bfa',
  textMuted: '#7c6f9b',
  border: 'rgba(167, 139, 250, 0.15)',
  borderHover: 'rgba(192, 132, 252, 0.35)',
};

// Dark mode colors
const darkColors = {
  textColorBase: '#f1f5f9',
  textColor1: '#f1f5f9',
  textColor2: '#e2e8f0',
  textColor3: '#a78bfa',
  textColorDisabled: '#4a4458',
  textColorQuaternary: '#7c6f9b',
  textColorHoverQuaternary: '#f5f3ff',
  textColorPressedQuaternary: '#f5f3ff',
  textColorDefault: '#f1f5f9',
  textColorHoverDefault: '#f5f3ff',
  textColorPressedDefault: '#f5f3ff',
  textColorTextDefault: '#f1f5f9',
  textColorTextHoverDefault: '#f5f3ff',
  textColorGhostDefault: '#f1f5f9',
  textColorGhostHoverDefault: '#f5f3ff',
  inputColor: 'rgba(15, 10, 26, 0.6)',
  inputTextColor: '#f1f5f9',
  inputPlaceholderColor: '#7c6f9b',
  inputBorder: '1px solid rgba(167, 139, 250, 0.2)',
  formLabelTextColor: '#c4b5fd',
  cardColor: 'rgba(139, 92, 246, 0.06)',
  cardBorderColor: 'rgba(167, 139, 250, 0.12)',
  modalColor: '#1a1028',
  drawerColor: '#1a1028',
};

// Light mode colors
const lightColors = {
  textColorBase: '#1a1a2e',
  textColor1: '#1a1a2e',
  textColor2: '#374151',
  textColor3: '#6c757d',
  textColorDisabled: '#adb5bd',
  textColorQuaternary: '#6c757d',
  textColorHoverQuaternary: '#1a1a2e',
  textColorPressedQuaternary: '#1a1a2e',
  textColorDefault: '#1a1a2e',
  textColorHoverDefault: '#1a1a2e',
  textColorPressedDefault: '#1a1a2e',
  textColorTextDefault: '#1a1a2e',
  textColorTextHoverDefault: '#1a1a2e',
  textColorGhostDefault: '#1a1a2e',
  textColorGhostHoverDefault: '#1a1a2e',
  inputColor: '#ffffff',
  inputTextColor: '#1a1a2e',
  inputPlaceholderColor: '#adb5bd',
  inputBorder: '1px solid rgba(0, 0, 0, 0.15)',
  formLabelTextColor: '#4B5563',
  cardColor: 'rgba(255, 255, 255, 0.95)',
  cardBorderColor: 'rgba(0, 0, 0, 0.08)',
  modalColor: '#ffffff',
  drawerColor: '#ffffff',
};

function buildOverrides(isDark: boolean): GlobalThemeOverrides {
  const c = isDark ? darkColors : lightColors;

  return {
    common: {
      primaryColor: brand.primary,
      primaryColorHover: brand.primaryHover,
      primaryColorPressed: brand.primaryPressed,
      primaryColorSuppl: brand.primaryHover,
      infoColor: brand.info,
      successColor: brand.success,
      warningColor: brand.warning,
      errorColor: brand.error,
      textColorBase: c.textColorBase,
      textColor1: c.textColor1,
      textColor2: c.textColor2,
      textColor3: c.textColor3,
      textColorDisabled: c.textColorDisabled,
      fontFamily: '"Noto Serif SC", "Source Han Serif SC", "Playfair Display", Georgia, serif',
      fontFamilyMono: '"JetBrains Mono", "Fira Code", monospace',
      borderRadius: '12px',
      borderRadiusSmall: '8px',
      heightMedium: '40px',
      heightLarge: '48px',
    },
    Button: {
      borderRadiusMedium: '24px',
      borderRadiusSmall: '16px',
      borderRadiusLarge: '28px',
      fontWeight: '600',
      colorSecondary: isDark ? 'transparent' : 'rgba(0,0,0,0.04)',
      colorHoverSecondary: isDark ? 'rgba(167,139,250,0.08)' : 'rgba(79,70,229,0.06)',
      colorPressedSecondary: isDark ? 'rgba(167,139,250,0.12)' : 'rgba(79,70,229,0.1)',
      borderSecondary: isDark ? 'rgba(167,139,250,0.2)' : 'rgba(0,0,0,0.15)',
      borderHoverSecondary: isDark ? 'rgba(192,132,252,0.35)' : '#4F46E5',
      textColorSecondary: isDark ? '#f1f5f9' : '#374151',
      textColorHoverSecondary: isDark ? '#f5f3ff' : '#1a1a2e',
      textColorPressedSecondary: isDark ? '#f5f3ff' : '#1a1a2e',
      colorPrimary: '#4F46E5',
      colorHoverPrimary: '#4338CA',
      colorPressedPrimary: '#3730A3',
      borderPrimary: 'transparent',
      borderHoverPrimary: 'transparent',
      borderPressedPrimary: 'transparent',
      textColorPrimary: isDark ? '#ffffff' : '#000000',
      textColorHoverPrimary: isDark ? '#ffffff' : '#000000',
      textColorPressedPrimary: isDark ? '#ffffff' : '#000000',
      textColorDisabledPrimary: isDark ? '#ffffff' : '#000000',
      // Quaternary button: text visible on hover in both modes
      textColorQuaternary: c.textColorQuaternary,
      textColorHoverQuaternary: c.textColorHoverQuaternary,
      textColorPressedQuaternary: c.textColorPressedQuaternary,
      colorHoverQuaternary: 'rgba(167, 139, 250, 0.08)',
      colorPressedQuaternary: 'rgba(167, 139, 250, 0.12)',
      // Default button
      textColorDefault: c.textColorDefault,
      textColorHoverDefault: c.textColorHoverDefault,
      textColorPressedDefault: c.textColorPressedDefault,
      // Text button
      textColorTextDefault: c.textColorTextDefault,
      textColorTextHoverDefault: c.textColorTextHoverDefault,
      // Ghost button
      textColorGhostDefault: c.textColorGhostDefault,
      textColorGhostHoverDefault: c.textColorGhostHoverDefault,
    },
    Card: {
      borderRadius: '16px',
      color: c.cardColor,
      borderColor: c.cardBorderColor,
      titleFontSizeMedium: '16px',
      titleFontWeight: '600',
    },
    Input: {
      borderRadius: '12px',
      heightMedium: '44px',
      color: c.inputColor,
      colorFocus: c.inputColor,
      colorDisabled: isDark ? 'rgba(15, 10, 26, 0.3)' : 'rgba(255, 255, 255, 0.5)',
      border: c.inputBorder,
      borderHover: `1px solid ${brand.primary}`,
      borderFocus: `1px solid ${brand.primary}`,
      boxShadowFocus: '0 0 0 3px rgba(79, 70, 229, 0.15)',
      textColor: c.inputTextColor,
      placeholderColor: c.inputPlaceholderColor,
      caretColor: brand.primary,
    },
    Tag: {
      borderRadius: '16px',
      fontSizeSmall: '11px',
    },
    Progress: {
      railHeight: '8px',
    },
    Modal: {
      borderRadius: '20px',
      color: c.modalColor,
    },
    Drawer: {
      color: c.drawerColor,
    },
    Steps: {
      indicatorColorProcess: '#4F46E5',
      indicatorColorFinish: '#86efac',
    },
    Timeline: {
      titleFontSizeMedium: '14px',
    },
    Checkbox: {
      colorChecked: brand.primary,
      borderChecked: brand.primary,
    },
    Divider: {
      color: isDark ? 'rgba(167, 139, 250, 0.15)' : 'rgba(0, 0, 0, 0.08)',
    },
    Form: {
      labelTextColor: c.formLabelTextColor,
    },
  };
}

/**
 * Reactive theme overrides that switch between dark and light color sets.
 * Usage: `:theme-overrides="themeOverrides"` (as a computed)
 */
export const themeOverrides = computed<GlobalThemeOverrides>(() =>
  buildOverrides(themeMode.value === 'dark'),
);

// Legacy static export for backward compat (defaults to dark)
export const themeOverridesStatic: GlobalThemeOverrides = buildOverrides(true);
