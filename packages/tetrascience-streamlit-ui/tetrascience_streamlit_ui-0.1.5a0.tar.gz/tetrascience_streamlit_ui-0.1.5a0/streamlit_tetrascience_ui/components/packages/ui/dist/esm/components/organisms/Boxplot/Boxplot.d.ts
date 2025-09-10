import React from "react";
import "./Boxplot.scss";
interface BoxDataSeries {
    y: number[];
    name: string;
    color: string;
    x?: string[] | number[];
    boxpoints?: "all" | "outliers" | "suspectedoutliers" | false;
    jitter?: number;
    pointpos?: number;
}
interface BoxplotProps {
    dataSeries: BoxDataSeries[];
    width?: number;
    height?: number;
    xRange?: [number, number];
    yRange?: [number, number];
    xTitle?: string;
    yTitle?: string;
    title?: string;
    showPoints?: boolean;
}
declare const Boxplot: React.FC<BoxplotProps>;
export { Boxplot };
export type { BoxDataSeries, BoxplotProps };
