import React from "react";
import "./Label.scss";
interface LabelProps {
    children: React.ReactNode;
    infoText?: string;
    className?: string;
}
declare const Label: React.FC<LabelProps>;
export { Label };
export type { LabelProps };
