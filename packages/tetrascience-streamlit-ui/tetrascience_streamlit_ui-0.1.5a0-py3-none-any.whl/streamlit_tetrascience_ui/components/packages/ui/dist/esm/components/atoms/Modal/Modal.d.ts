import { ReactNode } from "react";
import "./Modal.scss";
interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    onCloseLabel?: string;
    onConfirm: () => void;
    onConfirmLabel?: string;
    children: ReactNode;
    width?: string;
    className?: string;
    hideActions?: boolean;
    title?: string;
}
declare const Modal: ({ isOpen, onClose, onCloseLabel, onConfirm, onConfirmLabel, children, width, className, hideActions, title, }: ModalProps) => false | import("react/jsx-runtime").JSX.Element;
export { Modal };
export type { ModalProps };
