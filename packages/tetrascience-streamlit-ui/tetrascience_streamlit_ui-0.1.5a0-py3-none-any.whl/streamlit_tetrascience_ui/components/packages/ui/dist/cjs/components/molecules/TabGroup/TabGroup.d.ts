import React from "react";
import { TabProps, TabSize } from "@atoms/Tab";
import "./TabGroup.scss";
interface TabItem extends Omit<TabProps, "active" | "onClick"> {
    id: string;
}
interface TabGroupProps {
    tabs: TabItem[];
    activeTab?: string;
    onChange?: (tabId: string) => void;
    disabled?: boolean;
    size?: TabSize;
}
declare const TabGroup: React.FC<TabGroupProps>;
export { TabGroup };
export type { TabGroupProps, TabItem };
