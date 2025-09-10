import React from "react";
import "./Card.scss";
type CardSize = "small" | "medium" | "large";
type CardVariant = "default" | "outlined" | "elevated";
interface CardProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "title"> {
    children: React.ReactNode;
    title?: React.ReactNode;
    size?: CardSize;
    variant?: CardVariant;
    className?: string;
    fullWidth?: boolean;
}
declare const Card: React.ForwardRefExoticComponent<CardProps & React.RefAttributes<HTMLDivElement>>;
export { Card };
export type { CardProps, CardSize, CardVariant };
