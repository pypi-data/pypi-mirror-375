import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { Boxplot, BoxplotProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StBoxplot({
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
    title = "Boxplot",
    showPoints = false,
    ...boxplotProps
  } = args as {
    name?: string
    dataSeries?: Array<{
      y: number[]
      name: string
      color: string
      x?: string[] | number[]
      boxpoints?: "all" | "outliers" | "suspectedoutliers" | false
      jitter?: number
      pointpos?: number
    }>
    width?: number
    height?: number
    xRange?: [number, number]
    yRange?: [number, number]
    xTitle?: string
    yTitle?: string
    title?: string
    showPoints?: boolean
  } & Partial<BoxplotProps>

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Send boxplot render event back to Streamlit when component mounts
  useEffect(() => {
    Streamlit.setComponentValue({
      event: "render",
      name,
      title,
      seriesCount: dataSeries.length,
      showPoints,
    })
  }, [name, title, dataSeries.length, showPoints])

  // Merge boxplot props
  const mergedBoxplotProps = {
    dataSeries,
    width,
    height,
    xRange,
    yRange,
    xTitle,
    yTitle,
    title,
    showPoints,
    ...boxplotProps,
  }

  return <Boxplot {...mergedBoxplotProps} />
}

export default withStreamlitConnection(StBoxplot)
