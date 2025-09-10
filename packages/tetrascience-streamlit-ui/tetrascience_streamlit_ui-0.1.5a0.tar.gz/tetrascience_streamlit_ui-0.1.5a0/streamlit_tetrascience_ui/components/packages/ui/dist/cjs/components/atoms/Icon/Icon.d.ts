interface IconsProps {
    fill?: string;
    width?: string;
    height?: string;
    name: IconName;
}
interface IconProps {
    fill?: string;
    width?: string;
    height?: string;
}
declare enum IconName {
    BARS_3_BOTTOM_LEFT = "bars-3-bottom-left",
    BUILDING = "building",
    BULK_CHECK = "bulk-check",
    CHECK = "check",
    CHECK_CIRCLE = "check-circle",
    CHECK_SQUARE = "check-square",
    CHEVRON_DOWN = "chevron-down",
    CLOSE = "close",
    CODE = "code",
    COMPUTER = "computer",
    COPY = "copy",
    CUBE = "cube",
    DATABASE = "database",
    EXCLAMATION_CIRCLE = "exclamation-circle",
    EXCLAMATION_TRIANGLE = "exclamation-triangle",
    GEAR = "gear",
    GLobe = "globe",
    HASHTAG = "hashtag",
    HOME = "home",
    INBOX = "inbox",
    INFORMATION_CIRCLE = "information-circle",
    INFORMATION_CIRCLE_MICRO = "information-circle-micro",
    LAMP = "lamp",
    LOCK_OPEN = "lock-open",
    MINUS = "minus",
    PAPER_PLANE = "paper-plane",
    PENCIL = "pencil",
    PIE_CHART = "pie-chart",
    PIPELINE = "pipeline",
    PLUS = "plus",
    PROFILE = "profile",
    QUESTION_CIRCLE = "question-circle",
    ROCKET_LAUNCH = "rocket-launch",
    SEARCH = "search",
    SEARCH_DOCUMENT = "search-document",
    SEARCH_SQL = "search-sql",
    SITEMAP = "sitemap",
    TETRASCIENCE_ICON = "tetrascience-icon",
    TEXT = "text",
    TRASH = "trash",
    VIEWFINDER_CIRCLE = "viewfinder-circle"
}
declare const Icon: (props: IconsProps) => import("react/jsx-runtime").JSX.Element;
export { Icon, IconName };
export type { IconProps, IconsProps };
