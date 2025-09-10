import React from "react";
import "./Heatmap.scss";
interface HeatmapProps {
    data?: number[][];
    xLabels?: string[] | number[];
    yLabels?: string[] | number[];
    title?: string;
    xTitle?: string;
    yTitle?: string;
    colorscale?: string | Array<[number, string]>;
    width?: number;
    height?: number;
    showScale?: boolean;
    precision?: number;
    zmin?: number;
    zmax?: number;
    valueUnit?: string;
}
declare const Heatmap: React.FC<HeatmapProps>;
export { Heatmap };
export type { HeatmapProps };
