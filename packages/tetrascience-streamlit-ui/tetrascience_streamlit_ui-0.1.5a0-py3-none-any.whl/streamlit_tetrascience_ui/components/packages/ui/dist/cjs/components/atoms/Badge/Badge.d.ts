import React from "react";
import "./Badge.scss";
type BadgeSize = "small" | "medium";
type BadgeVariant = "default" | "primary";
interface BadgeProps {
    children: React.ReactNode;
    size?: BadgeSize;
    variant?: BadgeVariant;
    disabled?: boolean;
    iconLeft?: React.ReactNode;
    iconRight?: React.ReactNode;
    className?: string;
}
declare const Badge: React.FC<BadgeProps>;
export { Badge };
export type { BadgeProps, BadgeSize, BadgeVariant };
