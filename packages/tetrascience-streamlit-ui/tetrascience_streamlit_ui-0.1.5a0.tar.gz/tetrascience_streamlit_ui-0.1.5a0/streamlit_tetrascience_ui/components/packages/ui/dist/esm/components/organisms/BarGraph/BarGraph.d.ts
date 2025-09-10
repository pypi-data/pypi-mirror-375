import React from "react";
import "./BarGraph.scss";
interface BarDataSeries {
    x: number[];
    y: number[];
    name: string;
    color: string;
    error_y?: {
        type: "data";
        array: number[];
        visible: boolean;
    };
}
type BarGraphVariant = "group" | "stack" | "overlay";
interface BarGraphProps {
    dataSeries: BarDataSeries[];
    width?: number;
    height?: number;
    xRange?: [number, number];
    yRange?: [number, number];
    variant?: BarGraphVariant;
    xTitle?: string;
    yTitle?: string;
    title?: string;
    barWidth?: number;
}
declare const BarGraph: React.FC<BarGraphProps>;
export { BarGraph };
export type { BarDataSeries, BarGraphVariant, BarGraphProps };
