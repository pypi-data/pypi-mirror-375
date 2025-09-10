import React from "react";
import { IconName } from "@atoms/Icon";
import "./Sidebar.scss";
interface SidebarItemProps {
    icon: IconName;
    label: string;
    active?: boolean;
    onClick?: () => void;
}
interface SidebarProps {
    items: SidebarItemProps[];
    activeItem?: string;
    onItemClick?: (label: string) => void;
}
declare const Sidebar: React.FC<SidebarProps>;
export { Sidebar };
export type { SidebarProps };
