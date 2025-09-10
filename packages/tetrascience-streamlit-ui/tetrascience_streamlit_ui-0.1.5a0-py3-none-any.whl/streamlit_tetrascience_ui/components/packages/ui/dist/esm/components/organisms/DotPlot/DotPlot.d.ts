import React from "react";
import "./DotPlot.scss";
type MarkerSymbol = "circle" | "square" | "diamond" | "triangle-up" | "triangle-down" | "star";
interface DotPlotDataSeries {
    x: number[];
    y: number[];
    name: string;
    color?: string;
    symbol?: MarkerSymbol;
    size?: number;
}
type DotPlotVariant = "default" | "stacked";
type DotPlotProps = {
    dataSeries: DotPlotDataSeries | DotPlotDataSeries[];
    width?: number;
    height?: number;
    title?: string;
    xTitle?: string;
    yTitle?: string;
    variant?: DotPlotVariant;
    markerSize?: number;
};
declare const DotPlot: React.FC<DotPlotProps>;
export { DotPlot };
export type { DotPlotDataSeries, DotPlotProps, DotPlotVariant, MarkerSymbol };
