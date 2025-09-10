import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"

import "tetrascience-ui/index.css"
import { DotPlot, DotPlotProps } from "tetrascience-ui"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StDotPlot({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    name,
    dataSeries = [],
    width = 1000,
    height = 600,
    variant = "default",
    xTitle = "Columns",
    yTitle = "Rows",
    title = "Dot Plot",
    markerSize = 8,
    ...dotPlotProps
  } = args as {
    name?: string
    dataSeries?: Array<{
      x: number[]
      y: number[]
      name: string
      color?: string
      symbol?:
        | "circle"
        | "square"
        | "diamond"
        | "triangle-up"
        | "triangle-down"
        | "star"
      size?: number
    }>
    width?: number
    height?: number
    variant?: "default" | "stacked"
    xTitle?: string
    yTitle?: string
    title?: string
    markerSize?: number
  } & Partial<DotPlotProps>

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Send dot plot render event back to Streamlit when component mounts
  useEffect(() => {
    Streamlit.setComponentValue({
      event: "render",
      name,
      title,
      seriesCount: Array.isArray(dataSeries) ? dataSeries.length : 1,
      variant,
    })
  }, [name, title, dataSeries, variant])

  // Merge dot plot props
  const mergedDotPlotProps = {
    dataSeries,
    width,
    height,
    variant,
    xTitle,
    yTitle,
    title,
    markerSize,
    ...dotPlotProps,
  }

  return <DotPlot {...mergedDotPlotProps} />
}

export default withStreamlitConnection(StDotPlot)
