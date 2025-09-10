import React from "react";
import "./Main.scss";
interface MainProps {
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
}
declare const Main: React.FC<MainProps>;
export { Main };
export type { MainProps };
