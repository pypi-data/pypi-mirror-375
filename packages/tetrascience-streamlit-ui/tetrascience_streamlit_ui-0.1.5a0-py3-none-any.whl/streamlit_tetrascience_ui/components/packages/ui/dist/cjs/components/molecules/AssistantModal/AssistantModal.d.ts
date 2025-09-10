import React from "react";
import "./AssistantModal.scss";
interface AssistantModalProps {
    open: boolean;
    title: string;
    prompt: string;
    initialCode?: string;
    userQuery?: string;
    onUserQueryChange?: (value: string) => void;
    onCopy: (code: string) => void;
    onLaunch: (code: string) => void;
    onSend: (input: string) => void;
    onCancel: () => void;
}
declare const AssistantModal: React.FC<AssistantModalProps>;
export { AssistantModal };
export type { AssistantModalProps };
