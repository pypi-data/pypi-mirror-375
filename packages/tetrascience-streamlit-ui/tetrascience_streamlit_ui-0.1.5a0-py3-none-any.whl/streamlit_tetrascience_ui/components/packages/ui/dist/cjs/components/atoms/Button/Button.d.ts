import React from "react";
import "./Button.scss";
type ButtonSize = "small" | "medium";
type ButtonVariant = "primary" | "secondary" | "tertiary";
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    children: React.ReactNode;
    variant?: ButtonVariant;
    size?: ButtonSize;
    loading?: boolean;
    leftIcon?: React.ReactNode;
    rightIcon?: React.ReactNode;
    noPadding?: boolean;
    fullWidth?: boolean;
}
declare const Button: React.ForwardRefExoticComponent<ButtonProps & React.RefAttributes<HTMLButtonElement>>;
export { Button };
export type { ButtonProps, ButtonSize, ButtonVariant };
