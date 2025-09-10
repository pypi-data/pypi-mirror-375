import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { Label, LabelProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StLabel({ args, disabled, theme }: ComponentProps<any>): ReactElement {
  const {
    name,
    children = "Label Text",
    infoText,
    className,
    ...labelProps
  } = args as {
    name?: string
    children?: React.ReactNode
    infoText?: string
    className?: string
  } & Partial<LabelProps>

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Merge label props
  const mergedLabelProps = {
    children,
    infoText,
    className,
    ...labelProps,
  }

  return <Label {...mergedLabelProps} />
}

export default withStreamlitConnection(StLabel)
