import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { Chromatogram, ChromatogramProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StChromatogram({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    name,
    data = [],
    width = 900,
    height = 600,
    positionInterval = 10,
    colorA = "#2D9CDB",
    colorT = "#A1C63C",
    colorG = "#FF5C64",
    colorC = "#FFA62E",
    ...chromatogramProps
  } = args as {
    name?: string
    data?: Array<{
      position: number
      base?: string
      peakA: number
      peakT: number
      peakG: number
      peakC: number
    }>
    width?: number
    height?: number
    positionInterval?: number
    colorA?: string
    colorT?: string
    colorG?: string
    colorC?: string
  } & Partial<ChromatogramProps>

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Send chromatogram render event back to Streamlit when component mounts
  useEffect(() => {
    Streamlit.setComponentValue({
      event: "render",
      name,
      dataPoints: data.length,
      width,
      height,
      positionInterval,
    })
  }, [name, data.length, width, height, positionInterval])

  // Merge chromatogram props
  const mergedChromatogramProps = {
    data,
    width,
    height,
    positionInterval,
    colorA,
    colorT,
    colorG,
    colorC,
    ...chromatogramProps,
  }

  return <Chromatogram {...mergedChromatogramProps} />
}

export default withStreamlitConnection(StChromatogram)
