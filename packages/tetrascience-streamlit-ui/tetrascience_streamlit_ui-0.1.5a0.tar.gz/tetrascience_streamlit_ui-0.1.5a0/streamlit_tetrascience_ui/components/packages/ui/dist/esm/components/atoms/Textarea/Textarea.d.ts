import React from "react";
import "./Textarea.scss";
type TextareaSize = "xsmall" | "small";
interface TextareaProps extends Omit<React.TextareaHTMLAttributes<HTMLTextAreaElement>, "size"> {
    size?: TextareaSize;
    error?: boolean;
    disabled?: boolean;
    fullWidth?: boolean;
    rows?: number;
}
declare const Textarea: React.ForwardRefExoticComponent<TextareaProps & React.RefAttributes<HTMLTextAreaElement>>;
export { Textarea };
export type { TextareaProps, TextareaSize };
