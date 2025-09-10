import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { ScatterGraph, ScatterGraphProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StScatterGraph({
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
    xTitle = "Columns",
    yTitle = "Rows",
    title = "Scatter Plot",
    ...scatterGraphProps
  } = args as {
    name?: string
    dataSeries?: Array<{
      x: number[]
      y: number[]
      name: string
      color: string
    }>
    width?: number
    height?: number
    xRange?: [number, number]
    yRange?: [number, number]
    xTitle?: string
    yTitle?: string
    title?: string
  } & Partial<ScatterGraphProps>

  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  useEffect(() => {
    Streamlit.setComponentValue({
      event: "render",
      name,
      title,
      seriesCount: dataSeries.length,
    })
  }, [name, title, dataSeries.length])

  const mergedScatterGraphProps = {
    dataSeries,
    width,
    height,
    xRange,
    yRange,
    xTitle,
    yTitle,
    title,
    ...scatterGraphProps,
  }

  return <ScatterGraph {...mergedScatterGraphProps} />
}

export default withStreamlitConnection(StScatterGraph) 