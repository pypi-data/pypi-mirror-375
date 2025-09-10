import React from "react";
import "./Histogram.scss";
interface HistogramDataSeries {
    x: number[];
    name: string;
    color?: string;
    autobinx?: boolean;
    xbins?: {
        start: number;
        end: number;
        size: number;
    };
    opacity?: number;
    showDistributionLine?: boolean;
    lineWidth?: number;
}
type HistogramProps = {
    dataSeries: HistogramDataSeries | HistogramDataSeries[];
    width?: number;
    height?: number;
    title?: string;
    xTitle?: string;
    yTitle?: string;
    bargap?: number;
    showDistributionLine?: boolean;
};
declare const Histogram: React.FC<HistogramProps>;
export { Histogram };
export type { HistogramDataSeries, HistogramProps };
