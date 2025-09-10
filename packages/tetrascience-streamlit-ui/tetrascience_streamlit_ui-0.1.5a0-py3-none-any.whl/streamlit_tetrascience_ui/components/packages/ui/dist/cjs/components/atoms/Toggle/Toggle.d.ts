import React from "react";
import "./Toggle.scss";
interface ToggleProps {
    checked?: boolean;
    onChange?: (checked: boolean) => void;
    disabled?: boolean;
    label?: string;
    className?: string;
}
declare const Toggle: React.FC<ToggleProps>;
export { Toggle };
export type { ToggleProps };
