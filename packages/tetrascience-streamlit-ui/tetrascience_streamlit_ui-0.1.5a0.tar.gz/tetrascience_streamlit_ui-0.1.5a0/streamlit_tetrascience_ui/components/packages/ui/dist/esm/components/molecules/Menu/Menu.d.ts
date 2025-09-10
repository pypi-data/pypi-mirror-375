import React from "react";
import { MenuItemProps } from "@atoms/MenuItem";
import "./Menu.scss";
interface MenuItemData extends Omit<MenuItemProps, "onClick" | "onCheckChange"> {
    id: string;
}
interface MenuProps {
    title?: string;
    items: MenuItemData[];
    onItemClick?: (itemId: string) => void;
    onItemCheckChange?: (itemId: string, checked: boolean) => void;
    activeItemId?: string | null;
    className?: string;
}
declare const Menu: React.FC<MenuProps>;
export { Menu };
export type { MenuProps, MenuItemData };
