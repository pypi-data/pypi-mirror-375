import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { PieChart, PieChartProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StPieChart({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    name,
    dataSeries = { labels: [], values: [], name: "", colors: [] },
    width = 400,
    height = 400,
    title = "Pie Chart",
    textInfo = "percent",
    hole = 0,
    rotation = 0,
    ...pieChartProps
  } = args as {
    name?: string
    dataSeries?: {
      labels: string[]
      values: number[]
      name: string
      colors?: string[]
    }
    width?: number
    height?: number
    title?: string
    textInfo?: "none" | "label" | "percent" | "value" | "label+percent" | "label+value" | "value+percent" | "label+value+percent"
    hole?: number
    rotation?: number
  } & Partial<PieChartProps>

  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  useEffect(() => {
    Streamlit.setComponentValue({
      event: "render",
      name,
      title,
      labelCount: dataSeries.labels.length,
    })
  }, [name, title, dataSeries.labels.length])

  const mergedPieChartProps = {
    dataSeries,
    width,
    height,
    title,
    textInfo,
    hole,
    rotation,
    ...pieChartProps,
  }

  return <PieChart {...mergedPieChartProps} />
}

export default withStreamlitConnection(StPieChart) 