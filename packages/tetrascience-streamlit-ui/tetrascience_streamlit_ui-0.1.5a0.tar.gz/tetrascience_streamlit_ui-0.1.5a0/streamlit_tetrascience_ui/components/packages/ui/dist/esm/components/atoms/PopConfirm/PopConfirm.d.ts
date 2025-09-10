import React, { ReactNode } from "react";
import "./PopConfirm.scss";
type PopConfirmPlacement = "top" | "left" | "right" | "bottom" | "topLeft" | "topRight" | "bottomLeft" | "bottomRight" | "leftTop" | "leftBottom" | "rightTop" | "rightBottom";
interface PopConfirmProps {
    title?: ReactNode;
    description?: ReactNode;
    onConfirm?: (e?: React.MouseEvent<HTMLElement>) => void;
    onCancel?: (e?: React.MouseEvent<HTMLElement>) => void;
    okText?: string;
    cancelText?: string;
    placement?: PopConfirmPlacement;
    children: ReactNode;
    className?: string;
    okButtonProps?: React.ButtonHTMLAttributes<HTMLButtonElement>;
    cancelButtonProps?: React.ButtonHTMLAttributes<HTMLButtonElement>;
}
declare const PopConfirm: React.FC<PopConfirmProps>;
export { PopConfirm };
export type { PopConfirmProps };
