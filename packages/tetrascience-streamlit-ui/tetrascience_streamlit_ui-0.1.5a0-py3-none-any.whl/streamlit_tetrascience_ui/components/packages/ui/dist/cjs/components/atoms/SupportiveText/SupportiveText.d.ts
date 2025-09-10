import React from "react";
import "./SupportiveText.scss";
interface SupportiveTextProps {
    children: React.ReactNode;
    showCheck?: boolean;
    className?: string;
}
declare const SupportiveText: React.FC<SupportiveTextProps>;
export { SupportiveText };
export type { SupportiveTextProps };
