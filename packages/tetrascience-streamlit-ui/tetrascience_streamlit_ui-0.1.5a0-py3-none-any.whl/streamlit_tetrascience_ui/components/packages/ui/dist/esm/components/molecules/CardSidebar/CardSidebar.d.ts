import "./CardSidebar.scss";
type CardSidebarStatus = "default" | "active" | "hover" | "disabled";
interface CardSidebarProps {
    title: string;
    description?: string;
    buttonText?: string;
    linkText?: string;
    status?: CardSidebarStatus;
    onButtonClick?: () => void;
    onLinkClick?: () => void;
    className?: string;
}
declare const CardSidebar: import("react").ForwardRefExoticComponent<CardSidebarProps & import("react").RefAttributes<HTMLDivElement>>;
export { CardSidebar };
export type { CardSidebarProps };
