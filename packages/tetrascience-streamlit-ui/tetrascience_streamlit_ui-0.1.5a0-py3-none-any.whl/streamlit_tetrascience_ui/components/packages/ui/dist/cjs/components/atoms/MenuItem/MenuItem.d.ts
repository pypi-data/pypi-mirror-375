import "./MenuItem.scss";
interface MenuItemProps {
    label: string;
    checked?: boolean;
    showCheckbox?: boolean;
    onClick?: () => void;
    onCheckChange?: (checked: boolean) => void;
    active?: boolean;
    className?: string;
}
declare const MenuItem: import("react").ForwardRefExoticComponent<MenuItemProps & import("react").RefAttributes<HTMLDivElement>>;
export { MenuItem };
export type { MenuItemProps };
