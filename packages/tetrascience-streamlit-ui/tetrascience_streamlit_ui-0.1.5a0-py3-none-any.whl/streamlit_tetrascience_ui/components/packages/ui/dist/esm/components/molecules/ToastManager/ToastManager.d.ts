import React from "react";
import { ToastProps, ToastType } from "@atoms/Toast";
import "./ToastManager.scss";
export type ToastPosition = "top" | "bottom";
export interface ToastItem extends Omit<ToastProps, "className"> {
    id: string;
    duration?: number;
}
export interface ToastContainerProps {
    position: ToastPosition;
}
type ToastContextType = {
    toasts: ToastItem[];
    addToast: (toast: Omit<ToastItem, "id">) => string;
    removeToast: (id: string) => void;
};
export declare const toast: {
    show: (heading: string, description?: string, type?: ToastType, duration?: number) => string;
    info: (heading: string, description?: string, duration?: number) => string;
    success: (heading: string, description?: string, duration?: number) => string;
    warning: (heading: string, description?: string, duration?: number) => string;
    danger: (heading: string, description?: string, duration?: number) => string;
    default: (heading: string, description?: string, duration?: number) => string;
    dismiss: (id: string) => void;
};
export declare const useToasts: () => ToastContextType;
export interface ToastManagerProps {
    position?: ToastPosition;
}
export declare const ToastManager: React.FC<ToastManagerProps>;
export default ToastManager;
