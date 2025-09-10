import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { Icon, IconName } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StIcon({ args, disabled, theme }: ComponentProps<any>): ReactElement {
  const {
    componentName,
    name = IconName.HOME,
    fill = "currentColor",
    width = "24",
    height = "24",
    ...iconProps
  } = args as {
    componentName?: string
    name?: IconName
    fill?: string
    width?: string
    height?: string
  } & Partial<{
    name: IconName
    fill?: string
    width?: string
    height?: string
  }>

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Merge icon props
  const mergedIconProps = {
    name,
    fill,
    width,
    height,
    ...iconProps,
  }

  return <Icon {...mergedIconProps} />
}

export default withStreamlitConnection(StIcon)
