import React from "react";
import "./LaunchContent.scss";
export interface LaunchContentProps {
    initialCode?: string;
    onDeploy?: () => void;
    versions?: string[];
    currentVersion?: string;
    onVersionChange?: (version: string) => void;
}
declare const LaunchContent: React.FC<LaunchContentProps>;
export default LaunchContent;
