import React from "react";
import "./Checkbox.scss";
interface CheckboxProps {
    checked?: boolean;
    onChange?: (checked: boolean) => void;
    disabled?: boolean;
    className?: string;
    onClick?: (e: React.MouseEvent) => void;
    label?: React.ReactNode;
    noPadding?: boolean;
}
declare const Checkbox: React.ForwardRefExoticComponent<CheckboxProps & React.RefAttributes<HTMLInputElement>>;
export { Checkbox };
export type { CheckboxProps };
