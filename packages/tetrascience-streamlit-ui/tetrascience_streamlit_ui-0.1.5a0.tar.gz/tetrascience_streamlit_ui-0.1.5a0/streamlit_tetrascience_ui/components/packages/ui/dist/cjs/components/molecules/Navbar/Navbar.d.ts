import React from "react";
import "./Navbar.scss";
interface OrganizationInfo {
    name: string;
    subtext?: string;
    logo?: React.ReactNode;
}
interface NavbarProps {
    organization: OrganizationInfo;
}
declare const Navbar: React.FC<NavbarProps>;
export { Navbar };
export type { NavbarProps };
