import { DropdownProps } from "@atoms/Dropdown";
import "./SelectField.scss";
interface SelectFieldProps extends Omit<DropdownProps, "className"> {
    label: string;
    infoText?: string;
    supportiveText?: string;
    showSupportiveCheck?: boolean;
    className?: string;
}
declare const SelectField: import("react").ForwardRefExoticComponent<SelectFieldProps & import("react").RefAttributes<HTMLDivElement>>;
export { SelectField };
export type { SelectFieldProps };
