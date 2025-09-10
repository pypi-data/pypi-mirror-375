import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { ErrorAlert, ErrorAlertProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StErrorAlert({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    name,
    error = "An error occurred",
    title = "An Error Occurred",
    showDetailsDefault = false,
    noErrorContent,
    ...errorAlertProps
  } = args as {
    name?: string
    error?: unknown
    title?: React.ReactNode
    showDetailsDefault?: boolean
    noErrorContent?: React.ReactNode
  } & Partial<ErrorAlertProps>

  // Handle close action and send back to Streamlit
  const handleClose = () => {
    Streamlit.setComponentValue({
      action: "closed",
      name: name || "error_alert",
    })
  }

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Merge error alert props
  const mergedErrorAlertProps = {
    error,
    title,
    onClose: handleClose,
    showDetailsDefault,
    noErrorContent,
    ...errorAlertProps,
  }

  return <ErrorAlert {...mergedErrorAlertProps} />
}

export default withStreamlitConnection(StErrorAlert)
