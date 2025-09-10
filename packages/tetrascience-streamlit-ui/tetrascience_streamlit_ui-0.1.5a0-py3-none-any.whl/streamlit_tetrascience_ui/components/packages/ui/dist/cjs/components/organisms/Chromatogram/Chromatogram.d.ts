import React from "react";
import "./Chromatogram.scss";
interface PeakData {
    position: number;
    base?: string;
    peakA: number;
    peakT: number;
    peakG: number;
    peakC: number;
}
interface ChromatogramProps {
    data?: PeakData[];
    width?: number;
    height?: number;
    positionInterval?: number;
    colorA?: string;
    colorT?: string;
    colorG?: string;
    colorC?: string;
}
declare const Chromatogram: React.FC<ChromatogramProps>;
export { Chromatogram };
export type { PeakData, ChromatogramProps };
