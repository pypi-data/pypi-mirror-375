import React from "react";
import "./MarkdownDisplay.scss";
type MarkdownDisplayProps = {
    markdown: string;
    codeRenderer?: ({ inline, className, children, ...props }: CodeProps) => React.ReactElement;
};
type CodeProps = {
    node?: any;
    inline?: boolean;
    className?: string;
    children?: React.ReactNode;
    [key: string]: any;
};
declare const MarkdownDisplay: ({ markdown, codeRenderer }: MarkdownDisplayProps) => import("react/jsx-runtime").JSX.Element;
export { MarkdownDisplay };
export type { MarkdownDisplayProps };
