import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { Histogram, HistogramProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

function StHistogram({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    dataSeries,
    width = 480,
    height = 480,
    title = "Histogram",
    xTitle = "X Axis",
    yTitle = "Frequency",
    bargap = 0.2,
    showDistributionLine = false,
    ...histogramProps
  } = args as HistogramProps

  useEffect(() => {
    Streamlit.setFrameHeight(height + 100) // Add some padding for title and legend
  }, [theme, height])

  useEffect(() => {
    Streamlit.setComponentValue({
      event: "render",
      dataSeries,
      width,
      height,
      title,
    })
  }, [dataSeries, width, height, title])

  const mergedHistogramProps = {
    dataSeries,
    width,
    height,
    title,
    xTitle,
    yTitle,
    bargap,
    showDistributionLine,
    ...histogramProps,
  }

  return <Histogram {...mergedHistogramProps} />
}

export default withStreamlitConnection(StHistogram)
