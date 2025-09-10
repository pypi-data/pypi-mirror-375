import React from "react";
import "./ErrorAlert.scss";
interface ErrorAlertProps {
    /** The error object to display. Can be Error, AxiosError, string, or any other type. */
    error: unknown;
    /** Optional title for the error alert. Defaults to 'An Error Occurred'. */
    title?: React.ReactNode;
    /** Optional callback function when the alert is closed. */
    onClose?: () => void;
    /** Set to true to show technical details expanded by default. Defaults to false. */
    showDetailsDefault?: boolean;
    /** Custom message to show when error is null/undefined (optional, component renders nothing by default) */
    noErrorContent?: React.ReactNode;
}
declare const ErrorAlert: React.FC<ErrorAlertProps>;
export { ErrorAlert };
export type { ErrorAlertProps };
