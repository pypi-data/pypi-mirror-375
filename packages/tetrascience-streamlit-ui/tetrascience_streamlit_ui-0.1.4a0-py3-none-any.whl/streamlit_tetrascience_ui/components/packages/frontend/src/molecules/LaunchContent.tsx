import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { LaunchContent, LaunchContentProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StLaunchContent({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    initialCode,
    versions,
    currentVersion,
    ...launchContentProps
  } = args as LaunchContentProps

  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  useEffect(() => {
    Streamlit.setComponentValue({
      event: "render",
      currentVersion,
    })
  }, [currentVersion])

  const mergedLaunchContentProps = {
    initialCode,
    versions,
    currentVersion,
    ...launchContentProps,
  }

  return <LaunchContent {...mergedLaunchContentProps} />
}

export default withStreamlitConnection(StLaunchContent) 