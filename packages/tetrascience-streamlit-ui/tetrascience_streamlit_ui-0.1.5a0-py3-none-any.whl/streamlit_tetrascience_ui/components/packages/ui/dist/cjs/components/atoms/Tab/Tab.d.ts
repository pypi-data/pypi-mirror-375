import React from "react";
import "./Tab.scss";
type TabSize = "small" | "medium";
interface TabProps {
    label: string;
    active?: boolean;
    disabled?: boolean;
    size?: TabSize;
    onClick?: () => void;
}
declare const Tab: React.FC<TabProps>;
export { Tab };
export type { TabProps, TabSize };
