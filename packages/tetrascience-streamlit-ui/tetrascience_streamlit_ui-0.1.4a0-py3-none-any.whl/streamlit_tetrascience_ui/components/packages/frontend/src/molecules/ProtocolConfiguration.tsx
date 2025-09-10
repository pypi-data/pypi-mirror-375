import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { ProtocolConfiguration, ProtocolConfigurationProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StProtocolConfiguration({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    className,
    ...protocolConfigurationProps
  } = args as ProtocolConfigurationProps

  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  useEffect(() => {
    Streamlit.setComponentValue({
      event: "render",
    })
  }, [])

  const mergedProtocolConfigurationProps = {
    className,
    ...protocolConfigurationProps,
  }

  return <ProtocolConfiguration {...mergedProtocolConfigurationProps} />
}

export default withStreamlitConnection(StProtocolConfiguration) 