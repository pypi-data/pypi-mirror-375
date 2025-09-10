import React from "react";
import "./Input.scss";
type InputSize = "xsmall" | "small";
interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "size"> {
    size?: InputSize;
    iconLeft?: React.ReactNode;
    iconRight?: React.ReactNode;
    error?: boolean;
    disabled?: boolean;
}
declare const Input: React.ForwardRefExoticComponent<InputProps & React.RefAttributes<HTMLInputElement>>;
export { Input };
export type { InputProps, InputSize };
