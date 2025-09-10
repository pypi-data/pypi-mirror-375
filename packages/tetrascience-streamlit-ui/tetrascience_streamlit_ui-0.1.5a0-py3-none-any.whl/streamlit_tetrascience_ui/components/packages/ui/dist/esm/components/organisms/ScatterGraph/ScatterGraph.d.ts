import React from "react";
import "./ScatterGraph.scss";
interface ScatterDataPoint {
    x: number;
    y: number;
    additionalInfo?: Record<string, string | number>;
}
interface ScatterDataSeries {
    x: number[];
    y: number[];
    name: string;
    color: string;
}
interface ScatterGraphProps {
    dataSeries: ScatterDataSeries[];
    width?: number;
    height?: number;
    xRange?: [number, number];
    yRange?: [number, number];
    xTitle?: string;
    yTitle?: string;
    title?: string;
}
declare const ScatterGraph: React.FC<ScatterGraphProps>;
export { ScatterGraph };
export type { ScatterDataPoint, ScatterDataSeries, ScatterGraphProps };
