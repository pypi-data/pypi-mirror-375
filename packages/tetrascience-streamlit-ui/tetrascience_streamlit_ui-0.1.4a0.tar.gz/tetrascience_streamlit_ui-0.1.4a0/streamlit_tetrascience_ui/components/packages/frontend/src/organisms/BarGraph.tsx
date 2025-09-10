import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { BarGraph, BarGraphProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StBarGraph({
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
    variant = "group",
    xTitle = "Columns",
    yTitle = "Rows",
    title = "Bar Graph",
    barWidth = 24,
    ...barGraphProps
  } = args as {
    name?: string
    dataSeries?: Array<{
      x: number[]
      y: number[]
      name: string
      color: string
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
    variant?: "group" | "stack" | "overlay"
    xTitle?: string
    yTitle?: string
    title?: string
    barWidth?: number
  } & Partial<BarGraphProps>

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Send bar graph render event back to Streamlit when component mounts
  useEffect(() => {
    Streamlit.setComponentValue({
      event: "render",
      name,
      title,
      seriesCount: dataSeries.length,
      variant,
    })
  }, [name, title, dataSeries.length, variant])

  // Merge bar graph props
  const mergedBarGraphProps = {
    dataSeries,
    width,
    height,
    xRange,
    yRange,
    variant,
    xTitle,
    yTitle,
    title,
    barWidth,
    ...barGraphProps,
  }

  return <BarGraph {...mergedBarGraphProps} />
}

export default withStreamlitConnection(StBarGraph)
