import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { AreaGraph, AreaGraphProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StAreaGraph({
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
    variant = "normal",
    xTitle = "Columns",
    yTitle = "Rows",
    title = "Area Graph",
    ...areaGraphProps
  } = args as {
    name?: string
    dataSeries?: Array<{
      x: number[]
      y: number[]
      name: string
      color: string
      fill?: "tozeroy" | "tonexty" | "toself"
    }>
    width?: number
    height?: number
    xRange?: [number, number]
    yRange?: [number, number]
    variant?: "normal" | "stacked"
    xTitle?: string
    yTitle?: string
    title?: string
  } & Partial<AreaGraphProps>

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Send area graph render event back to Streamlit when component mounts
  useEffect(() => {
    Streamlit.setComponentValue({
      event: "render",
      name,
      title,
      seriesCount: dataSeries.length,
      variant,
    })
  }, [name, title, dataSeries.length, variant])

  // Merge area graph props
  const mergedAreaGraphProps = {
    dataSeries,
    width,
    height,
    xRange,
    yRange,
    variant,
    xTitle,
    yTitle,
    title,
    ...areaGraphProps,
  }

  return <AreaGraph {...mergedAreaGraphProps} />
}

export default withStreamlitConnection(StAreaGraph)
