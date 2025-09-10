import React from "react";
import "./PieChart.scss";
interface PieDataSeries {
    labels: string[];
    values: number[];
    name: string;
    colors?: string[];
}
type PieTextInfo = "none" | "label" | "percent" | "value" | "label+percent" | "label+value" | "value+percent" | "label+value+percent";
type PieChartProps = {
    dataSeries: PieDataSeries;
    width?: number;
    height?: number;
    title?: string;
    textInfo?: PieTextInfo;
    hole?: number;
    rotation?: number;
};
declare const PieChart: React.FC<PieChartProps>;
export { PieChart };
export type { PieDataSeries, PieTextInfo, PieChartProps };
