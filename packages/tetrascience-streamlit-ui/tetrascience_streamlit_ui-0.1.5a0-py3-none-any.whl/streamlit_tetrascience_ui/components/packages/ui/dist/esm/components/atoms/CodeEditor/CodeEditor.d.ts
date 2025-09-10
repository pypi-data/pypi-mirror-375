import React from "react";
import { OnChange } from "@monaco-editor/react";
import "./CodeEditor.scss";
interface CodeEditorProps {
    value: string;
    onChange: OnChange;
    language?: string;
    theme?: "light" | "dark";
    height?: string | number;
    width?: string | number;
    options?: Record<string, unknown>;
    label?: string;
    onCopy?: (code: string) => void;
    onLaunch?: (code: string) => void;
    disabled?: boolean;
}
declare const CodeEditor: React.FC<CodeEditorProps>;
export { CodeEditor };
export type { CodeEditorProps };
