import React from "react";
import "./Dropdown.scss";
type DropdownSize = "xsmall" | "small";
interface DropdownOption {
    value: string;
    label: string;
    disabled?: boolean;
}
interface DropdownProps {
    options: DropdownOption[];
    value?: string;
    placeholder?: string;
    disabled?: boolean;
    error?: boolean;
    size?: DropdownSize;
    onChange?: (value: string) => void;
    onOpen?: () => void;
    onClose?: () => void;
    width?: string;
    menuWidth?: string;
}
declare const Dropdown: React.FC<DropdownProps>;
export { Dropdown };
export type { DropdownProps, DropdownSize, DropdownOption };
