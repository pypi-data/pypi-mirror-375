import React from "react";
import "./AreaGraph.scss";
interface AreaDataSeries {
    x: number[];
    y: number[];
    name: string;
    color: string;
    fill?: "tozeroy" | "tonexty" | "toself";
}
type AreaGraphVariant = "normal" | "stacked";
interface AreaGraphProps {
    dataSeries: AreaDataSeries[];
    width?: number;
    height?: number;
    xRange?: [number, number];
    yRange?: [number, number];
    variant?: AreaGraphVariant;
    xTitle?: string;
    yTitle?: string;
    title?: string;
}
declare const AreaGraph: React.FC<AreaGraphProps>;
export { AreaGraph };
export type { AreaDataSeries, AreaGraphVariant, AreaGraphProps };
