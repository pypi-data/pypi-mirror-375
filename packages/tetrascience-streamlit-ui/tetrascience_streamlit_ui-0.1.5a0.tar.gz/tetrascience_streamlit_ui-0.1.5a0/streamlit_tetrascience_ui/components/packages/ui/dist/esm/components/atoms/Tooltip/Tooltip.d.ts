import React, { ReactNode } from "react";
import "./Tooltip.scss";
type TooltipPlacement = "top" | "right" | "bottom" | "left";
interface TooltipProps {
    content: ReactNode;
    children: ReactNode;
    placement?: TooltipPlacement;
    className?: string;
    delay?: number;
}
declare const Tooltip: React.FC<TooltipProps>;
export { Tooltip };
export type { TooltipProps, TooltipPlacement };
