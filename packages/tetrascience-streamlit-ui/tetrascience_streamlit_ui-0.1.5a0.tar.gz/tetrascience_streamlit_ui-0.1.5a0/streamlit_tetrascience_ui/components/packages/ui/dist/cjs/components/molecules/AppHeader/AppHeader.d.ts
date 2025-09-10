import React from "react";
import "./AppHeader.scss";
interface UserProfileProps {
    name: string;
    avatar?: string;
}
interface AppHeaderProps {
    hostname: string;
    userProfile: UserProfileProps;
    onHomeClick?: () => void;
    onSettingsClick?: () => void;
    onUserProfileClick?: () => void;
}
declare const AppHeader: React.FC<AppHeaderProps>;
export { AppHeader };
export type { AppHeaderProps };
