import React from "react";
import "./PythonEditorModal.scss";
interface PythonEditorModalProps {
    open: boolean;
    initialValue?: string;
    title?: string;
    onSave: (value: string) => void;
    onCancel: () => void;
}
declare const PythonEditorModal: React.FC<PythonEditorModalProps>;
export { PythonEditorModal };
export type { PythonEditorModalProps };
