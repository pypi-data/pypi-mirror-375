import React from "react";
import { ButtonControlProps } from "@atoms/ButtonControl";
import "./ButtonControlGroup.scss";
interface ButtonControlItem extends ButtonControlProps {
    id: string;
    icon?: React.ReactNode;
    disabled?: boolean;
}
interface ButtonControlGroupProps {
    controls: ButtonControlItem[];
    selectedId?: string;
    onChange?: (id: string) => void;
    vertical?: boolean;
    disabled?: boolean;
}
declare const ButtonControlGroup: React.FC<ButtonControlGroupProps>;
export { ButtonControlGroup };
export type { ButtonControlGroupProps, ButtonControlItem };
