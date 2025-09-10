import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { LineGraph, LineGraphProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StLineGraph({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    name,
    dataSeries = [],
    width = 1000,
    height = 600,
    xRange,
    yRange,
    variant = "lines",
    xTitle = "Columns",
    yTitle = "Rows",
    title = "Line Graph",
    ...lineGraphProps
  } = args as {
    name?: string
    dataSeries?: Array<{
      x: number[]
      y: number[]
      name: string
      color: string
      symbol?: string
      error_y?: {
        type: "data"
        array: number[]
        visible: boolean
      }
    }>
    width?: number
    height?: number
    xRange?: [number, number]
    yRange?: [number, number]
    variant?: "lines" | "lines+markers" | "lines+markers+error_bars"
    xTitle?: string
    yTitle?: string
    title?: string
  } & Partial<LineGraphProps>

  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  useEffect(() => {
    Streamlit.setComponentValue({
      event: "render",
      name,
      title,
      seriesCount: dataSeries.length,
      variant,
    })
  }, [name, title, dataSeries.length, variant])

  const mergedLineGraphProps = {
    dataSeries,
    width,
    height,
    xRange,
    yRange,
    variant,
    xTitle,
    yTitle,
    title,
    ...lineGraphProps,
  }

  return <LineGraph {...mergedLineGraphProps} />
}

export default withStreamlitConnection(StLineGraph) 