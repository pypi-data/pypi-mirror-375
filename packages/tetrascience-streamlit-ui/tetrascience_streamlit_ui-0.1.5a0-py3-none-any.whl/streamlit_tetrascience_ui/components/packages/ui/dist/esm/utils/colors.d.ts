/**
 * Centralized color system for TetraScience UI
 * This utility provides access to CSS variables defined in colors.css
 * while maintaining TypeScript support and IntelliSense
 */
/**
 * Centralized color tokens that map to CSS variables
 * This provides TypeScript support while leveraging CSS custom properties
 */
export declare const COLORS: {
    readonly BLACK_50: string;
    readonly BLACK_100: string;
    readonly BLACK_200: string;
    readonly BLACK_300: string;
    readonly BLACK_400: string;
    readonly BLACK_500: string;
    readonly BLACK_600: string;
    readonly BLACK_700: string;
    readonly BLACK_800: string;
    readonly BLACK_900: string;
    readonly BLACK: string;
    readonly BLACK_OPACITY_20: "rgba(26, 26, 26, 0.2)";
    readonly WHITE_50: string;
    readonly WHITE_100: string;
    readonly WHITE_200: string;
    readonly WHITE_300: string;
    readonly WHITE_400: string;
    readonly WHITE_500: string;
    readonly WHITE_600: string;
    readonly WHITE_700: string;
    readonly WHITE_800: string;
    readonly WHITE_900: string;
    readonly WHITE: string;
    readonly BLUE_50: string;
    readonly BLUE_100: string;
    readonly BLUE_200: string;
    readonly BLUE_300: string;
    readonly BLUE_400: string;
    readonly BLUE_500: string;
    readonly BLUE_600: string;
    readonly BLUE_700: string;
    readonly BLUE_800: string;
    readonly BLUE_900: string;
    readonly BLUE: string;
    readonly GREY_50: string;
    readonly GREY_100: string;
    readonly GREY_200: string;
    readonly GREY_300: string;
    readonly GREY_400: string;
    readonly GREY_500: string;
    readonly GREY_600: string;
    readonly GREY_700: string;
    readonly GREY_800: string;
    readonly GREY_900: string;
    readonly GREY: string;
    readonly ORANGE: string;
    readonly RED: string;
    readonly GREEN: string;
    readonly YELLOW: string;
    readonly PURPLE: string;
    readonly GREEN_BG: string;
    readonly GREEN_SUCCESS: string;
    readonly ORANGE_BG: string;
    readonly ORANGE_CAUTION: string;
    readonly RED_BG: string;
    readonly RED_ERROR: string;
    readonly GRAPH_SECONDARY_BROWN: string;
    readonly GRAPH_SECONDARY_PINK: string;
    readonly GRAPH_SECONDARY_TEAL: string;
    readonly GRAPH_SECONDARY_DARK_BLUE: string;
    readonly GRAPH_SECONDARY_BLACK: string;
    readonly GRAPH_SECONDARY_GREY: string;
};
/**
 * Chart color palette for consistent graph styling
 * Uses the primary graph colors from the design system
 */
export declare const CHART_COLORS: readonly [string, string, string, string, string, string, string, string, string, string, string, string];
export type ColorToken = keyof typeof COLORS;
