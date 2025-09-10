import { InputProps } from "@atoms/Input";
import "./FormField.scss";
interface FormFieldProps extends Omit<InputProps, "className"> {
    label: string;
    infoText?: string;
    supportiveText?: string;
    showSupportiveCheck?: boolean;
    className?: string;
}
declare const FormField: import("react").ForwardRefExoticComponent<FormFieldProps & import("react").RefAttributes<HTMLInputElement>>;
export { FormField };
export type { FormFieldProps };
