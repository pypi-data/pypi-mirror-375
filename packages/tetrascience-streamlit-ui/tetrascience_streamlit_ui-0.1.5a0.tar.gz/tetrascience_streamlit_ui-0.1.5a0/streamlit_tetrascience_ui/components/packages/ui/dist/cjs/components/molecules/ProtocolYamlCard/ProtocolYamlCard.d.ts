import React from "react";
import { DropdownOption } from "@atoms/Dropdown";
import "./ProtocolYamlCard.scss";
interface ProtocolYamlCardProps {
    title: string;
    newVersionMode: boolean;
    onToggleNewVersionMode: (checked: boolean) => void;
    versionOptions: DropdownOption[];
    selectedVersion: string;
    onVersionChange: (value: string) => void;
    onDeploy: () => void;
    yaml: string;
    onYamlChange: (value: string) => void;
}
declare const ProtocolYamlCard: React.FC<ProtocolYamlCardProps>;
export { ProtocolYamlCard };
export type { ProtocolYamlCardProps };
