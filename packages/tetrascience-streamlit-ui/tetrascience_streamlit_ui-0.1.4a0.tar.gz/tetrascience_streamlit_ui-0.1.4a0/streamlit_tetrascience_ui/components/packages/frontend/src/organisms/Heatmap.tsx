import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { Heatmap, HeatmapProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StHeatmap({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    name,
    data = [],
    xLabels,
    yLabels,
    title = "Heatmap",
    xTitle = "Columns",
    yTitle = "Rows",
    colorscale,
    width = 1000,
    height = 600,
    showScale = true,
    precision = 0,
    zmin = 0,
    zmax = 50000,
    valueUnit = "",
    ...heatmapProps
  } = args as {
    name?: string
    data?: number[][]
    xLabels?: string[] | number[]
    yLabels?: string[] | number[]
    title?: string
    xTitle?: string
    yTitle?: string
    colorscale?: string | Array<[number, string]>
    width?: number
    height?: number
    showScale?: boolean
    precision?: number
    zmin?: number
    zmax?: number
    valueUnit?: string
  } & Partial<HeatmapProps>

  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  useEffect(() => {
    Streamlit.setComponentValue({
      event: "render",
      name,
      title,
      dataPoints: data.length,
    })
  }, [name, title, data.length])

  const mergedHeatmapProps = {
    data,
    xLabels,
    yLabels,
    title,
    xTitle,
    yTitle,
    colorscale,
    width,
    height,
    showScale,
    precision,
    zmin,
    zmax,
    valueUnit,
    ...heatmapProps,
  }

  return <Heatmap {...mergedHeatmapProps} />
}

export default withStreamlitConnection(StHeatmap) 