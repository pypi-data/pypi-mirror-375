import React from "react";
import "./Toast.scss";
type ToastType = "info" | "success" | "warning" | "danger" | "default";
interface ToastProps {
    type?: ToastType;
    heading: string;
    description?: string;
    className?: string;
}
declare const Toast: React.FC<ToastProps>;
export { Toast };
export type { ToastProps, ToastType };
