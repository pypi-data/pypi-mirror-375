import { Button } from "@atoms/Button";
import { Modal } from "@atoms/Modal";
import "./CodeScriptEditorButton.scss";
interface CodeScriptEditorButtonProps {
    initialCode?: string;
    onCodeSave?: (newCode: string) => void;
    language?: string;
    buttonText?: string;
    modalTitle?: string;
    buttonProps?: React.ComponentProps<typeof Button>;
    modalProps?: Omit<React.ComponentProps<typeof Modal>, "isOpen" | "onConfirm" | "onClose">;
    disabled?: boolean;
    isEditMode?: boolean;
}
/**
 * Renders an 'Edit code' button that opens a modal with a Monaco code editor.
 */
declare const CodeScriptEditorButton: ({ initialCode, onCodeSave, language, buttonText, modalTitle, buttonProps, modalProps, disabled, }: CodeScriptEditorButtonProps) => import("react/jsx-runtime").JSX.Element;
export { CodeScriptEditorButton };
export type { CodeScriptEditorButtonProps };
