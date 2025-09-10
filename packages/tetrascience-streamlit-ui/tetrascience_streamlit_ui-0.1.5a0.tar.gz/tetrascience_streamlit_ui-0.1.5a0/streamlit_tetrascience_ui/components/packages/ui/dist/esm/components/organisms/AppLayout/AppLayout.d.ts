import React from "react";
import "./AppLayout.scss";
interface AppLayoutProps {
    userProfile: {
        name: string;
        avatar?: string;
    };
    hostname: string;
    organization: {
        name: string;
        subtext?: string;
        logo?: React.ReactNode;
    };
    children?: React.ReactNode;
}
declare const AppLayout: React.FC<AppLayoutProps>;
export { AppLayout };
export type { AppLayoutProps };
