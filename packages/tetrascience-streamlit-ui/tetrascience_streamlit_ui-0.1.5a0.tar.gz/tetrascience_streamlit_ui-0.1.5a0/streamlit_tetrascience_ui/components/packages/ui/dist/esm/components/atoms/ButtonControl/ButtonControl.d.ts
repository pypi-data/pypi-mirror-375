import React from "react";
import "./ButtonControl.scss";
interface ButtonControlProps {
    icon?: React.ReactNode;
    selected?: boolean;
    disabled?: boolean;
    onClick?: () => void;
}
declare const ButtonControl: React.FC<ButtonControlProps>;
export { ButtonControl };
export type { ButtonControlProps };
